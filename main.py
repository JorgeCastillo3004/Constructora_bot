import sys

from datetime import date


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QFormLayout
)

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox

#### LOAD MODULES ###
from whatsapp_functions import *
from database import *
from contac_creation import *

def process_control(t):
    _stop = False
    if t ==0:
        print("step1")
        time.sleep(0.3)
        # t+=1
    if t ==1:
        print("step2")
        time.sleep(0.3)
        # t+=1
    if t ==2:
        print("step3")
        time.sleep(0.3)
        # t+=
    if t ==3:
        print("step4")
        time.sleep(0.3)
    if t ==4:
        print("step5")
        time.sleep(0.3)
    if t ==5:
        print("step6")
        time.sleep(0.3)
    if t ==6:
        print("step7")
        time.sleep(0.3)
    if t ==7:
        print("step8")
        time.sleep(0.3)
    if t ==8:
        print("step9")
        time.sleep(0.3)
    if t ==9:
        print("step10")
        time.sleep(0.3)        
    if t ==11:
        print("restart")
        time.sleep(0.3)
        t = -1
        _stop = True
    if _stop:
        print("Process Completed")
    return t + 1, _stop

class Worker(QtCore.QObject):

    update_process_point = QtCore.pyqtSignal(object)
    build_contacts_signal = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._i = 0
        self._stop = False        
    # ACTION OR PROCCESS TO MANIPULATE START OR STOP
    def activateFunction(self):
        def incAndEmit():
            # self._i, self._stop = process_control(self._i)
            self._i, self._stop, self.df_unfound = start_send_messages(self.profile_info, self._i)
            self.update_process_point.emit(self)
            if self._stop and len(self.df_unfound) != 0:
                self.build_contacts_signal.emit(self)

            
        QtCore.QTimer.singleShot(100, incAndEmit)

class WindowMain(QWidget):

    emit_signal_start_process = QtCore.pyqtSignal()
    # updateFile = QtCore.pyqtSignal() 
    updateExportFile = QtCore.pyqtSignal() 

    def __init__(self):
        super().__init__()        
        self.fecha = date.today().strftime("%d/%m/%Y")        
        self.selected_file = ''       
        
        self.ButtonLaunchWhatsApp = QtWidgets.QPushButton('WhatsApp')
        self.ButtonLaunchWhatsApp.setFixedSize(150, 25)        
        self.ButtonLaunchWhatsApp.clicked.connect(self.ExecuteLaunchWhatsApp)

        self.ButtonGenerateContacts = QtWidgets.QPushButton('Generar Contactos')
        self.ButtonGenerateContacts.setFixedSize(150, 25)        
        self.ButtonGenerateContacts.clicked.connect(self.ExecuteGenerateContacts)

        self.ButtonStartPause = QtWidgets.QPushButton('Start')
        self.ButtonStartPause.setFixedSize(150, 25)        
        self.ButtonStartPause.clicked.connect(self.ExecuteStart)

        self.ButtonStop = QtWidgets.QPushButton('Stop')
        self.ButtonStop.setFixedSize(150, 25)        
        self.ButtonStop.clicked.connect(self.ExecuteStop)

        self.ButtonSelectFile = QtWidgets.QPushButton('SelectFile')
        self.ButtonSelectFile.setFixedSize(150, 25)        
        self.ButtonSelectFile.clicked.connect(self.ExecuteSelectFile)

        self.filepath = QtWidgets.QTextEdit()
        self.filepath.setFixedSize(250, 75)
        
        # label and text to change template message
        self.msgTemplateLabel = QtWidgets.QLabel('Plantilla mensaje')
        self.msgTemplateLabel.setFixedSize(250, 25)

        self.templateMSG = QtWidgets.QTextEdit()
        self.templateMSG.setAlignment(Qt.AlignJustify)        
        self.templateMSG.setFixedSize(350, 100)

        # Sections to set initial settings
        filename_ = 'check_points/profile_info.json'
        if not os.path.isfile(filename_):
            create_profile_dict(filename = filename_)

        self.profile_info = load_check_point(filename_)

        # Set profile info inside GUI
        self.filepath.setText(self.profile_info['filepath'])
        self.templateMSG.setText(self.profile_info['msg_template'])

        SetInicio(self)
        #############################################################
        #                   WORKER SETTINGS                         #
        #############################################################
        self.worker = Worker()
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self._thread = self.thread # protect from destroying by gc
        self._worker = self.worker # protect from destroying by gc

        #############################################################
        #                SETTINGS SIGNALS EMITIONS                  #
        #############################################################        

        #############################################################
        #                SETTINGS SIGNALS connections               #
        #############################################################
        self.emit_signal_start_process.connect(self.worker.activateFunction)
        self.worker.update_process_point.connect(self.check_parameters_continue_process)
        self.worker.build_contacts_signal.connect(self.build_list_contacts)
        
        #############################################################
        #                   SETTINGS INITIAL FLAGS                  #
        #############################################################
        self.launch_navigator_flag = False
        # self.file_selected = False        
        self._stop = True

    def ExecuteGenerateContacts(self):
        if self.profile_info['filepath'] != '':           
           create_csv_contacts(self.profile_info['filepath'], 'check_points/csv_contacts_info.csv')
           create_vcf_file('check_points/csv_contacts_info.csv', file_out = 'contacts_file')

        else:
            QMessageBox.about(self, "Error", 'Recuerda selecionar un archivo de entrada')

    def ExecuteLaunchWhatsApp(self):        
        try:
            if not self.launch_navigator_flag:
                if self.profile_info['filepath'] != '' and self.profile_info['msg_template']!='':
                    self.ExecuteUpdateProfileInfo()
                    print('Procediendo a abrir "WhatsApp Web"')
                    self.driver = launch_navigator(self.profile_info)
                    self.launch_navigator_flag = True
                else:
                    QMessageBox.about(self, "Error", 'Recuerda seleccionar el archivo de entrada y escribir el mensaje')
            else:
                QMessageBox.about(self, "Error", 'Previa session en curso')
        except:
            # self.driver.quit()
            QMessageBox.about(self, "Error", 'Recuerda cerrar todas las ventanas Chrome Navigator')

    def ExecuteUpdateProfileInfo(self):
        self.profile_info['msg_template'] = self.templateMSG.toPlainText()
        self.profile_info['filepath'] = self.filepath.toPlainText()
        save_check_point('check_points/profile_info.json', self.profile_info)

    def ExecuteStart(self):        
        if self.launch_navigator_flag:
            flag_block = True
            self.ExecuteUpdateProfileInfo()
            if self._stop and flag_block:                
                self.ButtonStartPause.setText("Pause") 
                self.ButtonStop.setChecked(False)    
                self._stop = False
                self.worker.profile_info = self.profile_info
                # print("self.profile_info['msg_template']", self.profile_info['msg_template'])
                # print("self.worker.profile_info", self.worker.profile_info, '\n')
                self.emit_signal_start_process.emit()
                flag_block = False

            if not self._stop and flag_block:                
                self.ButtonStartPause.setText("Start")
                self._stop = True
        else:
            QMessageBox.about(self, "Error", 'Debes ejecutar primero "WhatsApp"')

    def check_parameters_continue_process(self):
        if self.worker._stop:
            self._stop = self.worker._stop            
        if self._stop:
            # self._stop = _stop            
            self.ButtonStartPause.setText("Start")
            return        
        else:
            self.emit_signal_start_process.emit()

    def build_list_contacts(self):
        create_csv_contacts('processed_file_unfound.csv', 'check_points/csv_contacts_info.csv')
        create_vcf_file('check_points/csv_contacts_info.csv', file_out = 'contacts_file')
        QMessageBox.about(self, "Contactos faltantes creados", 'nueva lista creada con el nombre "contacts_file.vcf" ')

    def ExecuteStop(self):        
        self._stop = True
        Worker._stop = self._stop
        self.driver.quit()
        self.launch_navigator_flag = False

    def ExecuteSelectFile(self):
        print("Excete seltect file: ")
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)        
        selected_file, _ = file_dialog.getOpenFileName(self, "Open File", ".csv", "All files (*)")
        self.filepath.setText(selected_file)
        self.profile_info['filepath'] = selected_file
        if self.profile_info['filepath']!='':
            previous_run_flag, row_number = search_check_points(selected_file)
            if previous_run_flag:
                QMessageBox.about(self, "Aviso", 'Se encontro un check point desea continuar o reiniciar')
        # if self.selected_file:
        #     self.updateFile.emit()
        #     self.file_selected = True

    # def ExecuteUploadFile(self):
    #     Worker.selected_file = self.selected_file
    #     self.FileName.setText(self.selected_file.split('/')[-1])

def SetInicio(self):
    #               LAYERS SETTING                      
    #####################################################
    #                                                   #
    #           FirstButtonlayout                       #
    #                                                   #
    #####################################################
    #                    #                              #
    #   SideButtonLeft   #     SideButtonRight          #
    # -Launch WhatsApp   #     -select file             #
    # -Start             #     -patch selected          #
    # -Stop              #     -message template        #
    #                    #                              #
    #####################################################
    # CleanSideButtonTable(self)
    # MAIN LAYOUT VERTICAL#       
    self.Mainlayout = QHBoxLayout()

    # # FIRST ROWS OF BUTTONS
    # self.FirstButtonlayout = QHBoxLayout()

    # SIDE LAYOUT SETTED TO THE LEFT
    self.SideButtonLeft = QVBoxLayout()
    # LAYOUT FOR THE TABLE
    self.SideButtonRight = QVBoxLayout()    

    # Add Buttons to Buttons layout    
    # self.FirstButtonlayout.addWidget(self.ButtonLaunchNavigator, 0)

    # ADD ELEMENTS TO THE SIDEBUTTONLEFT LAYOUT    
    # self.SideButtonLeft.addWidget(self.ButtonStart)    
    self.SideButtonLeft.addWidget(self.ButtonGenerateContacts)
    self.SideButtonLeft.addWidget(self.ButtonLaunchWhatsApp)
    self.SideButtonLeft.addWidget(self.ButtonStartPause)
    self.SideButtonLeft.addWidget(self.ButtonStop)

    # ADD ELEMENTS TO THE SIDEBUTTONRIGHT LAYOUT
    self.SideButtonRight.addWidget(self.ButtonSelectFile)
    self.SideButtonRight.addWidget(self.filepath)
    self.SideButtonRight.addWidget(self.msgTemplateLabel)
    self.SideButtonRight.addWidget(self.templateMSG)

    # CREATE AND ADD VERTICAL SPACER TO LAYER SIDEBUTTONS
    self.VerticalSpacer = QFrame()
    self.VerticalSpacer.Shape(QFrame.VLine)
    self.VerticalSpacer.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)    
    self.SideButtonRight.addWidget(self.VerticalSpacer)
    self.SideButtonLeft.addWidget(self.VerticalSpacer)


    # ADD ALL THE ELEMENTS 
    self.Mainlayout.addLayout(self.SideButtonLeft)
    self.Mainlayout.addLayout(self.SideButtonRight)
    self.setLayout(self.Mainlayout)

    self.setWindowTitle("TUINMUEBLE.COM")


if __name__ == "__main__":  
    app = QApplication(sys.argv)
    window = WindowMain()
    # window.setCentralWidget (frm)
    # window.resize(340, 440)
    window.show()
    sys.exit(app.exec_())    
    closeConection(dbase)
    driver.close()
