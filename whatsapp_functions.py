from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from selenium import webdriver
from datetime import datetime
import pandas as pd
import random
import time
import json
import re
import os

#####################################################################
#					CHECK POINTS BLOCK 								#
#####################################################################
def save_check_point(filename, dictionary):
    json_object = json.dumps(dictionary, indent=4)
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def load_check_point(filename):
    # Opening JSON file
    if os.path.isfile(filename):
        with open(filename, 'r') as openfile:        
            json_object = json.load(openfile)
    else:
        json_object = {}
    return json_object

def search_check_points(csv_filepath, check_point_filename = 'check_points/last_row.json'):
	file_name = csv_filepath.split('/')[-1]
	previous_run_flag = False
	if not os.path.isfile(check_point_filename):
		last_row_dict = {}
		row_number = 0		
	else:
		last_row_dict = load_check_point(check_point_filename)
		try:
			last_row = last_row_dict[file_name]['last_row']
			row_number = last_row + 1
			previous_run_flag = True
		except:
			previous_run_flag = False
			row_number = 0
	return previous_run_flag, row_number


def create_profile_dict(filename = 'check_points/profile_info.json'):
	folder_name = filename.split('/')[0]
	if not os.path.exist(folder_name):
		os.mkdir(folder_name)

	if not os.path.isfile(filename):
		dict_profile = {   
		"filepath":"",
		"chrome_profile": {
		"user_data_dir": "",
		"profile_directory": ""},
		"msg_template": "Saludos cordiales le escribe {} de la empresa TUINMUEBLE.COM,\n nos comunicamos para recordarle que su plan {} esta proximo a \n vencer,la fecha de vencimiento es: {}, restan {} dias de servicio"    
		}
	save_check_point(filename, dict_profile)

def launch_navigator(dict_profile):
	global driver
	options = webdriver.ChromeOptions()
	options.add_argument("--disable-blink-features=AutomationControlled") 
	options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
	options.add_experimental_option("useAutomationExtension", False)

	if dict_profile['chrome_profile']['user_data_dir']!='':
	    options.add_argument(r"user-data-dir={}".format(dict_profile['chrome_profile']['user_data_dir']) )

	if dict_profile['chrome_profile']['profile_directory'] != '':
	    options.add_argument(r"profile-directory={}".format(dict_profile['chrome_profile']['profile_directory']) )	
	driver = webdriver.Chrome(options=options)
	driver.get('https://web.whatsapp.com/')# Load whatsApp website
	return driver

def wait_autentication():
    autentication = False
    max_try = 10
    count = 0
    while not autentication:
        conversations = driver.find_elements(By.CLASS_NAME, '_8nE1Y')
        if len(conversations)!=0:
            autentication = True
            print("Permission granted: ")
        else:
            time.sleep(1.5)
            print("-",end='')

def get_search_box():
	"""Function to get the search box of the contacs, get the box to send the contact name or phone number"""
	search_box_complete =  driver.find_element(By.CLASS_NAME, '_1EUay')
	search_box =  search_box_complete.find_element(By.CSS_SELECTOR, 'p')
	return search_box

def make_search(complete_phone):
	
	search_box = get_search_box()

	if search_box.text != '':
		"""Clean search box in case of previos unconcluded search """
		cancel_search = driver.find_element(By.CLASS_NAME,'-Jnba')    
		cancel_search.click()
	search_box = get_search_box()
	search_box.send_keys(complete_phone)

def click_conversation(registername):
    result_contacts = driver.find_elements(By.CLASS_NAME, '_199zF._3j691')    
    if len(result_contacts)!= 0:
        for conversations in result_contacts:
            contact_title = conversations.text.split('\n')[0]
            # contact_title = conversations.find_element()
            print("contact_title ", contact_title, "registername ", registername)

            if registername in contact_title:
                conversations.click()
                print("Click")
                break
        contact_found =  True
    else:
        print("Contact unfound ")
        contact_found =  False
    return contact_found

def get_resulted_contact(registername, max_try = 2):
    flag_search = True
    count = 0
    id_conversation = 0
    while flag_search:
        try:
            contact_found = click_conversation(registername)
            time.sleep(0.5)
            flag_search = False
        except:
            count +=1
            time.sleep(1.2)
            if count == max_try:
                flag_search = False
                contact_found = False
    return contact_found

def delete_previous_text(box_text):
    box_text.send_keys(Keys.BACKSPACE*len(box_text.text))
        
def build_msg(row, template):
	remaining_days = (datetime.now() - row['Vencimiento']).days	

	msg = template.format(row['Asesor'].title(), row['Plan'], row['Vencimiento_formated'], remaining_days)
	return ' '.join(msg.replace('\n','').split())

def send_msg(template, flag_sent = False):
    msg_box = driver.find_element(By.CLASS_NAME, '_2lryq')# find block to send msg
    box_text = msg_box.find_element(By.CLASS_NAME, 'selectable-text.copyable-text.iq0m558w.g0rxnol2') # find msg box to load text

    delete_previous_text(box_text)
    box_text.send_keys(template) # send msg
    button_send = msg_box.find_element(By.CLASS_NAME, '_2xy_p._3XKXx') # find button send msg
    if flag_sent:
        button_send.click() # click to send msg
    time.sleep(1)
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()   

def check_unfound_contacts(filename, filenameout):
	df = pd.read_csv(filename)	
	df_unfound = df[df['dontsent']==False]
	df_unfound.to_csv(filenameout)
	return df_unfound
# if __name__ == "__main__":
# 	dict_profile = load_check_point('check_points/profile_info.json')
# 	launch_navigator(dict_profile)
# 	driver.get('https://web.whatsapp.com/')# Load whatsApp website
# 	wait_autentication() # Wait until the user scand the QR to permission grant

# 	df = pd.read_excel(dict_profile['filepath'])# load file with the information related to contacts and plans.
# 	df['Vencimiento_formated'] = df['Vencimiento'].dt.strftime('%d/%m/%Y')
# 	# Loop over data frame.
# 	for i, row in df[0:5].iterrows():
	    
# 	    complete_phone ='+58'+row['Teléfono'].replace(' ','')	    
# 	    print("Checking the contact: ", complete_phone)    
	    
# 	    make_search(row['Asesor'])
# 	    time.sleep(1)
# 	    flag_continue = get_resulted_contact(row['Asesor'])	    
	    
# 	    if flag_continue:
# 	        msg = build_msg(row)
# 	        send_msg(msg, flag_sent = True)
# 	        time.sleep(2)  
# 	time.sleep(180)	
# 	driver.close()

def start_send_messages(dict_profile, _i):
	global df, complete_phone, flag_continue, row, template, df_missed, check_point_row, dict_check_point, current_file_name
	_stop = False
	nsteps = 5
	

	if _i == 0:
		# print("Steep 0")
		wait_autentication()
		dict_check_point = load_check_point('check_points/last_row.json')
		df = pd.read_excel(dict_profile['filepath'])# load file with the information related to contacts and plans.				
		df['dontsent'] = True
		df['Vencimiento_formated'] = df['Vencimiento'].dt.strftime('%d/%m/%Y')
		template = dict_profile['msg_template']
		df_missed = pd.DataFrame()
		check_point_row = dict_profile['last_row']
		print("check_point_row inside start_send_messages step 0: ", check_point_row)
		current_file_name = dict_profile['filepath'].split('/')[-1]
		# previous_run_flag, check_point_row = search_check_points(dict_profile['filepath'], check_point_filename = 'check_points/last_row.json')
	# Loop over data frame.
	# for i, row in df[0:5].iterrows():

	current_row = (_i-1)//nsteps + check_point_row
	if current_row +1 >= len(df):
		_stop = True

	if (_i-1)%nsteps == 0:
		# print("Steep 1")
		row = df.iloc[current_row]
		# complete_phone ='+58'+row['Teléfono'].replace(' ','')
		
		print("Fila actual", current_row+1,"/", len(df), "Nombre: ",row['Asesor'])
		
		# print("Checking the contact: ", complete_phone)

	if (_i-1)%nsteps == 1:	    
		# print("Steep 2")
		make_search(row['Asesor'])
		time.sleep(1)

	if (_i-1)%nsteps == 2:
		# print("Steep 3")
		flag_continue = get_resulted_contact(row['Asesor'])

	if (_i-1)%nsteps == 3:
		print("Steep 4, last step")
		if flag_continue:
			msg = build_msg(row, template)
			send_msg(msg, flag_sent = False)
			time.sleep(2)
			df.loc[current_row,'dontsent']= False
			df_missed = df[df['dontsent']==False]
			new_file_name = dict_profile['filepath'].replace('.xlsx','_faltantes.csv')
			print("new_name ", new_file_name)
			df_missed.to_csv(new_file_name)# save new file with only missed contacts
		# print("current_row", current_row, "Len df",len(df))
		if current_row +1 >= len(df):
			print("Documento Procesado")
			cancel_search = driver.find_element(By.CLASS_NAME,'-Jnba')    
			cancel_search.click()
			
			# filter rows that contact don't exist
			# df_unfound = check_unfound_contacts(dict_profile['filepath'].replace('.csv','_faltantes.csv'), 'processed_file_unfound.csv')
			# save check point for this file			
			dict_check_point[current_file_name] = {'last_row':current_row}
			save_check_point('check_points/last_row.json', dict_check_point)
			_stop = True
			_i = -1
	df_missed = df[df['dontsent']==False]
	return _i +1, _stop, df_missed#, previous_run_flag
