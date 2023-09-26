import sqlite3
import os

def createConection():
    dbase = sqlite3.connect("check_points/peoplesearch.db")
    return dbase

def closeConection(dbase):
    dbase.close()

def createTablePeople(dbase):
	dbase.execute('''CREATE TABLE IF NOT EXISTS people (name TEXT, phone TEXT,
	  				address TEXT, list_phones TEXT, past_address TEXT, status TEXT, filename TEXT)''')

def getPeopleContact(dbase):
	data = dbase.execute("SELECT name, phone, address FROM people")
	result = data.fetchall()    
	return result

def getPeopleContactByFile(dbase, filename_):
	data = dbase.execute("SELECT name, phone, address FROM people WHERE filename =='{}'".format(filename_))	
	result = data.fetchall()    
	return result

def getPeopleContactByFileAllColumns(dbase, filename_):
	data = dbase.execute("SELECT * FROM people WHERE filename =='{}'".format(filename_))	
	result = data.fetchall()    
	return result

def insertNewRegister(dbase, dictdata, filename_):
	name = dictdata['name']
	phone = dictdata['primary_phone']	
	address = dictdata['main_address']		
	list_phones = str(dictdata['list_phones'])
	past_address = str(dictdata['past_address'])
	status = dictdata['status']
	

	dbase.execute(''' INSERT INTO people (name, phone, address, list_phones, past_address, status,filename) VALUES (?, ?, ?, ?, ?, ?, ?)''',
	 (name, phone, address, list_phones, past_address, status, filename_))
	dbase.commit()

def deleteRows(dbase, filename_):
	data = dbase.execute("DELETE FROM people WHERE filename =='{}'".format(filename_))	

# Creating the folder for save
if not os.path.exists('check_points'):
	os.mkdir('check_points')

dbase = createConection()
createTablePeople(dbase)
# deleteRows(dbase, 'Propwire_Export_230_Properties_Sep 2_2023.csv')
# results = getPeopleContactByFileAllColumns(dbase, 'Propwire_Export_230_Properties_Sep 2_2023.csv')

closeConection(dbase)