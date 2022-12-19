#Imports
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton, 
    QScrollArea, QWidget, QGraphicsBlurEffect, QStackedWidget, QTextEdit, QComboBox, QCalendarWidget, QButtonGroup, QGridLayout
)
from PyQt6 import QtGui, uic, QtCore
from PyQt6.QtGui import QImage, QIcon, QBrush, QPainter, QPixmap, QCloseEvent, QCursor, QFont
from datetime import date, timedelta

import QuizBoxClient.MySQL_Queries as query
import shutil
import os
import sys
import time
import logging
import subprocess
import datetime
import random
import json

#Global Variables
FILES = {
    "resources": ("MySQL.png", "App_Logo.png", "home.jpg", "home_selected.jpg", "help_selected.jpg", "help.jpg",
                    "quiz_selected.jpg", "quiz.jpg", "settings_selected.jpg", "settings.jpg", "Computer.png",
                    "GK.png", "Maths.png", "Science.png", "Back.png", "tick.png", "default.png"),
    "ui": ("Loading.ui", "SQLLog.ui", "Main_App.ui", "Feedback.ui"),
    "directory": ("Resources", "QuizBoxClient", "UI")
} #Contains data for verification of files
FI = GUI_FILE = RESOURCE_FILE = list() #Contains the list of missing directories, if found
LAB_LOAD = MAIN_WINDOW = CONNECT = QUIZDATA = None #Loading label; TIme of error; Main_Window_Class(); Connection with SQL
MAIN_VAL = False #False -> On loading screen; True -> On main app
COUNT = 0 #Progress bar
DESC = "An unexpected error occured! Please try again later!" #Error message

#Functions
def except_hook(exc_type, exc_value, exc_traceback):
    """
    Except hook to catch unexpected exceptions.

    exc_type : The type of error
    exc_value : The error message
    exc_traceback : Traceback of the exception
    """

    #Ignores KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger = logging.getLogger(__name__) #Gets logger
    logger.critical(f"[Uncaught Exception]\n", exc_info=(exc_type, exc_value, exc_traceback)) #Logs the exception


def check_sql_connection():
    """Checks the status of SQL connection with credentials provided."""

    global CONNECT, DESC

    logger = logging.getLogger(__name__) #Gets logger

    val, var = query.check() # val: bool, var: str (for errors)
    if var is not None: #If an error is found
        DESC = var 
    if var == 'Timeout': #If the user took too long
        DESC = 'SQL Login Timeout! Please Relaunch!'
        logger.warning('SQL Connection Timeout!')
    CONNECT = val #Status of connection


def mask_image(imgdata, imgtype ='png', size = 64):
    """
    This function convert rectangular image to circular image.

    Parameters:
        imgdata : The data of image in bytes
        imgtype [Default: .png] : The type of image
        size [Default: 64]: The size of the image
    
    Returns:
        pixelmap_img : The new rounded pixmap data of the image
    """
  
    image = QImage.fromData(imgdata, imgtype) #Loads data
    image.convertToFormat(QImage.Format.Format_ARGB32) #Converts image to 32 bits ARGB format
  
    imgsize = min(image.width(), image.height())
    rect = QtCore.QRect(
        (image.width() - imgsize) // 2,
        (image.height() - imgsize) // 2,
        imgsize,
        imgsize,
     ) #Converts the image to square
       
    image = image.copy(rect) #Copies the image
  
    #Create the output image with the same dimensions 
    out_img = QImage(imgsize, imgsize, QImage.Format.Format_ARGB32)
    out_img.fill(QtCore.Qt.GlobalColor.transparent)
  
    brush = QBrush(image) #Create a texture brush and paint a circle 
  
    # Paint the output image
    painter = QPainter(out_img)
    painter.setBrush(brush)
  
    painter.setPen(QtCore.Qt.PenStyle.NoPen) #Doesn't draw the borders
    painter.drawEllipse(0, 0, imgsize, imgsize) #Draws an ellipse
    painter.end() #Closes painter

    #Converts the image to a pixmap and rescale it. 
    pr = QtGui.QWindow().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(round(size), round(size), QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                               QtCore.Qt.TransformationMode.SmoothTransformation)
  
    return pm #Returns back the pixmap data


#Class
class quiz_data(QtCore.QObject):
    """
    This class validates Quiz Data in the directory.

    Attributes:
        finished : Signal to indicate task is finsihed
    """

    #Signals
    finished = QtCore.pyqtSignal()

    #Functions
    def check_quiz(self):
        """Validates Quiz Data"""

        global QUIZDATA

        files = (
            "Computers_Easy.csv", "Computers_Medium.csv", "Computers_Hard.csv",
            "GK_Easy.csv", "GK_Medium.csv", "GK_Hard.csv",
            "Maths_Easy.csv", "Maths_Medium.csv", "Maths_Hard.csv",
            "Science_Easy.csv", "Science_Medium.csv", "Science_Hard.csv",
            "NASA.csv", "Wonder_Of_The_World.csv",
            "Bhopal_Gas_Tragedy.csv", "Plastics.csv"
        )

        QUIZDATA = all([os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Data\\Profile\\", file_name)) for file_name in files])

        self.finished.emit()


class resources(QtCore.QObject):
    """
    This class validates Resources and UI in the directory.

    Attributes:
        finished : Signals provided by PyQt6
        res_files : Tuple of Resources
        ui_file : Tuple of UI
    """

    global FILES

    #Signals
    finished = QtCore.pyqtSignal()

    #Variables
    res_file = FILES["resources"]
    ui_file = FILES["ui"]

    #Functions
    def res_load(self):
        """Validates Resources and UI"""

        global RESOURCE_FILE, GUI_FILE

        file_t = tuple([os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", file_name)) for file_name in self.res_file]) #Creates a tuple of actual Resources found
        for x in file_t:
            time.sleep(0.01)
            if x is False:
                z = file_t.index(x)
                RESOURCE_FILE.append(self.res_file[z]) #Adds missing file in the list

        dir_t = tuple([os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\UI\\", dir_name)) for dir_name in self.ui_file])
        for n in dir_t:
            time.sleep(0.01)
            if n is False:
                p = dir_t.index(n)
                GUI_FILE.append(self.ui_file[p])
            
        self.finished.emit() #Signals the completion of validation


class dependency(QtCore.QObject):
    """
    This class validates the directories.

    Attributes:
        finished : Signal provided y PyQt6
        direc : Tuple of directories
    """

    global FILES

    #Signals
    finished = QtCore.pyqtSignal()

    #Variables
    direc = FILES["directory"]

    #Functions
    def check_load(self):
        """Validates the directories"""

        global FI

        dir_t = tuple([os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), dir_name)) for dir_name in self.direc])
        for n in dir_t:
            time.sleep(0.01)
            if n is False:
                p = dir_t.index(n)
                FI.append(self.direc[p])
            
        self.finished.emit()


class check_sql(QtCore.QObject):
    """
    This class is used for checking the connection with MySQL and loading presets, if launched very first time.

    Attributes:
        finished : Signal provided by PyQt6
    """

    #Signals
    finished = QtCore.pyqtSignal()

    #Functions
    def check(self):
        """Checks the connection with MySQL and loads presets, if launched first time"""

        check_sql_connection() #Triggers checking sql function
        self.finished.emit() #Signals the completion


class loading_lab(QtCore.QObject):
    """
    This class is for closing the loading screen after it completes.

    Atributes:
        finished, check : Signals provided by PyQt6
        var : True, if the progress bar goes to 100%
        force_close : If True, force closes the loading screen
        txt : Tuple of loading text to be looped
    """

    #Signals
    finished = QtCore.pyqtSignal()
    check = QtCore.pyqtSignal()

    def __init__(self):
        """The constructor of loading_lab class."""

        QtCore.QObject.__init__(self) #Initiates QObject with the class

        #Variables
        self.var = False
        self.force_close = False
        self.txt = ("loading...", "loading.", "loading..")


    #Functions
    def load(self):
        """Sets the text of loading in loop and closes the loading screen, either by force or 100%"""

        global LAB_LOAD

        while True:
            if self.force_close is False:
                if self.var is False:
                    for x in self.txt:
                        time.sleep(0.5)
                        LAB_LOAD.setText(x) #Text changes every 0.5 seconds
                else:
                    self.finished.emit()
                    break #Breaks the loop at 100%
            else:
                break #Breaks the loop when force closed


class Loading(QMainWindow):
    """
    This class is neccesary for the Loading screen when the application is launched.

    Attributes:
        check, dependant, res_load, quiz_load, res, err : Signals provided by PyQt6

        main_class : Instance of bg_process class
        depend : Instance of dependancy class
        connect : Instance of check_internet class
        load : Instance of loading_lab class
        resource : Instance of resources class
        ui : The file path of Loading.ui file
        quiz_files : Instance of quiz_data class
        logger : The logger

        dropShadowFrame : Name of the frame in Loading.ui file [Type: QFrame]
        progress_bar : Name of the progress bar in Loading.ui file [Type: QProgressBar]
        desc : Name of the label in Loading.ui file [Type: QLabel]
        timer : Timer provided by PyQt6
        shadow : Graphical shadow effect provided by PyQt6

        _thread, _thread1, _thread2, _thread3, _thread4 : Thread instances provided by PyQt6
    """

    #Signals
    check = QtCore.pyqtSignal()
    dependent = QtCore.pyqtSignal()
    res_load = QtCore.pyqtSignal()
    quiz_load = QtCore.pyqtSignal()
    res = QtCore.pyqtSignal()
    err = QtCore.pyqtSignal()

    def __init__(self):
        """The constructor for Loading class. Main threads and progress bar are loaded."""

        global LAB_LOAD

        super().__init__() #Initializes Loading class with QMainWindow

        #Variables
        self.depend = dependency()
        self.connect = check_sql()
        self.load = loading_lab()
        self.resource = resources()
        self.quiz_files = quiz_data()

        self.logger = logging.getLogger(__name__)
        self.ui = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\UI\\", "Loading.ui")
        
        uic.loadUi(self.ui, self) #loads the Loading.ui file that can be used by PyQt6

        self.logger.info('Loading start...')

        #Widgets
        self.dropShadowFrame = self.findChild(QFrame, "dropShadowFrame")
        self.progress_bar = self.findChild(QProgressBar, "progressBar")
        LAB_LOAD = self.findChild(QLabel, "label_loading")
        self.desc = self.findChild(QLabel, "label_description")
        self.timer = QtCore.QTimer()
        self.shadow = QGraphicsDropShadowEffect()

        #Threads
        self._thread = QtCore.QThread()
        self._thread1 = QtCore.QThread()
        self._thread2 = QtCore.QThread()
        self._thread3 = QtCore.QThread()
        self._thread4 = QtCore.QThread()
        
        #Config
        self.setFixedSize(680, 400) #Fixes the window size (680x480)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint) #Removes frame from the window
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True) #Makes the background translucent
        self.shadow.setBlurRadius(20) #Blur
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 60)) #Changes shadow color to Grey
        self.dropShadowFrame.setGraphicsEffect(self.shadow) #Adds shadow graphic effect

        #Connections
        self.err.connect(self.msg_error) #Connects err attribute to msg_error method

        self.load.moveToThread(self._thread) #Moves load to _thread
        self._thread.started.connect(self.load.load) #Connects the thread
        self.load.finished.connect(self._thread.quit) #Exits thr thread
        self.load.finished.connect(self.close) #Closes the window

        self.connect.moveToThread(self._thread1)
        self.check.connect(self._thread1.start)
        self._thread1.started.connect(self.connect.check)
        self.connect.finished.connect(self._thread1.quit)

        self.depend.moveToThread(self._thread2)
        self.dependent.connect(self._thread2.start)
        self._thread2.started.connect(self.depend.check_load)
        self.depend.finished.connect(self._thread2.quit)

        self.resource.moveToThread(self._thread3)
        self.res_load.connect(self._thread3.start)
        self._thread3.started.connect(self.resource.res_load)
        self.resource.finished.connect(self._thread3.quit)

        self.quiz_files.moveToThread(self._thread4)
        self.quiz_load.connect(self._thread4.start)
        self._thread4.started.connect(self.quiz_files.check_quiz)
        self.quiz_files.finished.connect(self._thread4.quit)

        #Executions
        self._thread.start() #Starts the main thread

        #Progress Bar
        self.timer.timeout.connect(self.progress) #Connects the timer with progress bar
        self.timer.start(100) #Starts the timer
    

    @staticmethod
    def wait(time=10):
        """
        Custom wait to prevent freezing of the UI.

        Parameters:
            time [int] : time/10 seconds
        """

        loop = QtCore.QEventLoop() #Creates an event loop
        QtCore.QTimer.singleShot(time*100, loop.quit) #Singleshot first :arg: [1000 = sec]; quits the loop after the time ends
        loop.exec() #Executes the event loop


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        Detects the closing of Loading window.

        Parameters:
            a0 : The CloseEvent
        """

        global COUNT
        
        super().closeEvent(a0)

        if COUNT >= 100:
            return
        
        if os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Logs\\", "QuizAppLog.log")):
            #Creates backup of log file
            log_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Logs\\", "QuizAppLog.log")
            new_log_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Logs\\", f"QuizAppLog-backup-{datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S,%f')}.log")

            shutil.copy2(log_file, new_log_file) #Generates a backup file


    def msg_error(self, txt: str = ""):
        """
        Generates an error message and records the time of the error.

        Parameters:
            txt [str] [Default: ""] : The error message to show
        """

        global DESC

        QMessageBox.critical(self, "ERROR", DESC) #Displays the error message

        if txt == "":
            self.close()
            exit()
        else:
            logger = logging.getLogger(__name__) #Gets logger
            logger.error(txt)
            self.close()
            exit()


    def main_win(self):
        """Shows the main window and lets the program know."""

        global MAIN_WINDOW, MAIN_VAL

        MAIN_WINDOW = Main_Window_Class() #Initiates the class
        MAIN_WINDOW.show()
        MAIN_VAL = True
        if MAIN_WINDOW.start_anim is False:
            MAIN_WINDOW.wait(10)
            MAIN_WINDOW.pre_anim.start() #Starts the animation


    def progress(self):
        """This function is to handle the progress bar and run the designated events step-by-step"""

        global COUNT, CONNECT, DESC, FI, GUI_FILE, RESOURCE_FILE, QUIZDATA

        self.progress_bar.setValue(COUNT) #Sets the value of progress bar to COUNT

        if COUNT >= 100: #Launches the app
            self.logger.info('Loading Success!!')
            self.desc.setText("STATUS: Launching the app!")
            self.load.var = True
            self.timer.stop()
            self.main_win()
        elif COUNT < 10: #Checks the connection with MySQL
            self.desc.setText("STATUS: Connecting with MySQL!")

            if DESC == 'SQL Login Timeout! Please Relaunch!':
                self.err.emit()

            if query.FIRST:
                query.edit_config('LOGIN', 'first', 'False')

            if query.CONNECTED is False: #If the auto-SQL connection fails
                self.wait(20) #Waits for 2 sec
                login_page = SqlLogin()
                login_page.show()
                self.wait(150) #Waits for 15 sec
            
            self.check.emit()

            if query.CONNECTED is False:
                self.wait(10)

            if CONNECT: #CONNECT : Status of connection with MySQL
                self.logger.debug('Sql Connection Success!!')
                query.save_to_file()
                if (query.salt_decode(query.read_config()["SETTINGS"]["sql"]) == "True") is False:
                    query.edit_config("SETTINGS", "sql", "False")
                self.timer.start(25)
                COUNT += 1
            elif CONNECT is False:
                self.err.emit() #Closes the app
        elif COUNT < 30: #Validates quiz data
            self.desc.setText("STATUS: Checking & Validating Quiz Data!")
            self.quiz_load.emit()
            if QUIZDATA is False:
                self.load.force_close = True
                self.timer.stop()
                DESC = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue, if it persist after re-installation."
                self.msg_error("Quiz Data files not found!")
            elif QUIZDATA:
                self.logger.info('Quiz Data Verified!!')
                self.timer.start(15)
                COUNT += 1
        elif COUNT < 60: #Validates the Directories
            self.desc.setText("STATUS: Checking & Validating Directories!")
            self.dependent.emit()
            if FI:
                self.load.force_close = True #Closes the app
                self.timer.stop() #Stops the timer
                DESC = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue, if it persist after re-installation."
                self.msg_error(f"\nThe following list of directories not found! \n {FI}")
            else:
                self.logger.info('Directories Verified!!')
                self.timer.start(15)
                COUNT += 1
        elif COUNT < 89: #Validates UI and Resources
            self.desc.setText("STATUS: Checking & Validating Resources!")
            self.res_load.emit()
            if GUI_FILE and RESOURCE_FILE:
                self.load.force_close = True
                self.timer.stop()
                DESC = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue if it persist after re-installation."
                self.msg_error(f"\nResources: \n {RESOURCE_FILE} \nUser Interface: \n {GUI_FILE} \nNOT FOUND!")
            elif RESOURCE_FILE:
                self.load.force_close = True
                self.timer.stop()
                DESC = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue if it persist after re-installation."
                self.msg_error(f"\nThe following list of resource files not found! \n {RESOURCE_FILE}")
            elif GUI_FILE:
                self.load.force_close = True
                self.timer.stop()
                DESC = "Some files are found missing or corrupt! \nTry re-installing the app! \n\nA crash report has been created for the developer to solve the issue if it persist after re-installation."
                self.msg_error(f"\nThe following list of user interface files not found! \n {GUI_FILE}")
            else:
                self.logger.info('Resources Verified!!')
                self.timer.start(15)
                COUNT += 1
        elif COUNT < 100: #Loads the main window
            self.load.remove = True
            self.desc.setText("STATUS: Setting up the app!")
            self.timer.start(25)
            COUNT += 1


class SqlLogin(QMainWindow):
    """
    Loads the UI for entering username and password for accessing MySQL Database.

    Attributes:
        _login : Button for get credentials and connect the database
        _username : Username of MySQL
        _password : Password of MySQL
        anim : The animation for opacity of the window
        shadow : Graphics effect provided by PyQt6
        dropShadowFrame : Name of the frame
    """

    def __init__(self):
        """The constructor for SqlLogin class."""

        super().__init__()

        uic.loadUi(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\UI\\", "SQLLog.ui"), self) #Loads the UI

        #Variables
        self._login = self.findChild(QPushButton, "Login")
        self._username = self.findChild(QLineEdit, "Username")
        self._password = self.findChild(QLineEdit, "Password")
        self.dropShadowFrame = self.findChild(QFrame, "dropShadowFrame")
        self.shadow = QGraphicsDropShadowEffect()

        #Animation
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity") #windowOpacity is the name of opacity property
        self.anim.setDuration(400) #.4 seconds durationn
        self.anim.setStartValue(0.0) #Starts with 0 opacity
        self.anim.setEndValue(1.0) #Ends with 1 opacity
        self.anim.start() #Starts the animation

        #Config
        self.setFixedSize(355, 200) # Resolution : 355x200
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint) #Removes frames
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.shadow.setBlurRadius(10) #Sets Blur to 10
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        self.dropShadowFrame.setGraphicsEffect(self.shadow) #Sets the shadow effect

        #Events
        self._login.clicked.connect(self.sl) #Connects login button with sl function
        self._username.textChanged.connect(lambda: self.change_css()) #Triggers the function change_css when text is changed

    #Functions
    def change_css(self):
        """Changes the css style of the QLineEdit."""

        css_style = ("border: 1px solid red;", "")[self._username.text().strip() != ''] #Sets style sheet to "", if text is not equal to ""
        self._username.setStyleSheet(css_style) #Implements the change


    def sl(self):
        """Encrypts username and password, and closes the window"""

        if self._username.text().strip() != '':
            query.USER = query.encrypt(self._username.text().strip())
            query.PASSWORD = query.encrypt(self._password.text())
            self.close()


class Feedback_UI(QMainWindow):
    """
    Loads the UI for Feedback.

    Attributes:
        username : The username sending the feedback
        feedback : The feedback text to be sent
        send : The button to send the feedback
        close_window : The button to close the window (cancel button)
        anim : The animation for opacity of the window
        shadow : Graphics effect provided by PyQt6
        dropShadowFrame : Name of the frame
    """

    def __init__(self, user: str):
        """
        The constructor for the class.

        Parameters:
            user [str] : The username sending the feedback
        """

        super().__init__() #Initiates the class

        uic.loadUi(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\UI\\", "Feedback.ui"), self) #Loads the UI

        #Variables
        self.username = user
        self.feedback = self.findChild(QTextEdit, "Feedback_Text")
        self.send = self.findChild(QPushButton, "Send")
        self.close_window = self.findChild(QPushButton, "Close")
        self.dropShadowFrame = self.findChild(QFrame, "dropShadowFrame")
        self.shadow = QGraphicsDropShadowEffect()

        #Animation
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity") #windowOpacity is the name of opacity property
        self.anim.setDuration(400) #.4 seconds durationn
        self.anim.setStartValue(0.0) #Starts with 0 opacity
        self.anim.setEndValue(1.0) #Ends with 1 opacity
        self.anim.start() #Starts the animation

        #Config
        self.setFixedSize(412, 262) # Resolution : 412x262
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint) #Removes frames
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.shadow.setBlurRadius(10) #Sets Blur to 10
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        self.dropShadowFrame.setGraphicsEffect(self.shadow) #Sets the shadow effect

        #Connections
        self.feedback.textChanged.connect(lambda: self.check_length())
        self.close_window.clicked.connect(self.close)
        self.send.clicked.connect(self.send_feedback)

    #Functions
    def check_length(self):
        """Checks and verifies the max length in the Text Edit"""

        if len(self.feedback.toPlainText()) > 500:
            text = self.feedback.toPlainText()
            text = text[:500] #Sets text till 500 words
            self.feedback.setPlainText(text) #Sets the text
            cursor = self.feedback.textCursor() #Gets the cursor
            cursor.setPosition(500) #Add it at the end of the text
            self.feedback.setTextCursor(cursor) #Sets the cursor


    def send_feedback(self):
        """The function to send the feedback"""

        feedback = self.feedback.toPlainText() #Gets the text from the TextEdit
        query.sql_query(
            insert_query='insert into feedbacks (Username, Feedback) values (%s, %s)',
            insert_query_values=(self.username, feedback)
        )
        QMessageBox.information(self, 'Thank You', 'We are grateful for your feedback!')
        self.close()


class Main_Window_Class(QMainWindow):
    """
    This class is for the main application deployed.

    Atrributes:
        logger: The logger

        selected : The widget that is selected by the user
        myquiz_selected : The latest quiz data of the user
        logged : The status of Login
        timer : The timer control value
        count : 10 min counter
        quiz_dict : The data of questions
        home_data_dict : The dictionary for home community data
        filter_home_data_dict : The dictionary for home community data filters
        register : The state of registration process
        myquiz_buttongroup : The button group for scroll area in profile
        quiz_question_buttongroup : The button group for questions in quiz
        home_quiz_buttongroup : The button group for community quiz in home
        imgdata : The image data retreived of profile image
        pix_map : The circular default profile image

        sql_toggle_background : The sql label widget to change color after clicking
        sql_secondary : More info on the setting selected
        sql_toggle : The sql button to be clicked for True or False values
        account_toggle_background : The account label widget to change color after clicking
        account_secondary : More account info on the setting selected
        account_toggle : The account button to be clicked for True or False values
        anim_toggle_background : The animation label widget to change color after clicking
        anim_secondary : More animation info on the setting selected
        anim_toggle : The animation button to be clicked for True or False values

        bg_frame : The main frame of the app
        logo_frame : The frame for logo
        logo_text : The widget where the text of logo is
        logo_frame : The widget where the image of logo is
        license_scroll : The scrollarea widget of the license page
        help_scroll : The scrollarea of help frame

        stack : The Stacked widget of the main display frame
        settings_stack : The Stacked widget of settings frame
        login_stack : The Stacked widget of login frame
        register_stack : The Stacked widget of register frame
        account_stack : The Stacked widget of account frame
        profile_stack : The Stacked widget of profile frame

        home_trending_one : No. 1 Trending
        home_trending_two : No. 2 Trending
        home_trending_three : No. 3 Trending
        home_search : Search box filter
        home_difficulty : Difficulty filter
        home_question_number : Total question numbers filter
        home_scroll : Scroll area for buttons
        home_scroll_area : Widget holding buttons

        username : The lineEdit to have username
        password : The lineEdit to have the password
        login : The pushButton for login
        account_access : The pushButton to open account

        full_name : The lineEdit to have full name
        gender : The comboBox to have gender selection
        birth : The label with DOB data
        calendar : The calender widget for DOB
        register_next : The next button in register frame
        register_user : The lineEdit to have username for registration
        register_usertick : The tick of registration username
        confirm_register_user : The lineEdit to have confirmed username for registration
        confirm_register_usertick : The tick of confirmed registration username
        register_pass : The lineEdit to have password for registration
        register_passtick : The tick of registration password
        confirm_register_pass : The lineEdit to have confirmed password for registration
        confirm_register_passtick : The tick of confirmed registration password
        register_key_label : The label having generated key
        register_generatekey : The button to generate random alphanumeric key
        register_btn : The register button for registration

        forgot_username : The pushButton for forgot username
        user_fullname : The full name in Forgot Username
        forgot_userkey : The lineEdit taking key
        forgot_usertick : The label having tick for key
        forgot_newuser : The new username
        forgot_newuser_tick : The verification of new username
        forgot_confirmuser : Confirmed new username
        forgot_confirmuser_tick : Tick for confirmed new username
        forgot_user_btn : The button to change username

        forgot_password : The pushButton for forgot password
        pwd_fullname : The full name in Forgot Password
        forgot_pwdkey : The lineEdit taking key
        forgot_pwdtick : The label having tick for key
        forgot_newpwd : The new password
        forgot_newpwd_tick : The verification of new password
        forgot_confirmpwd : Confirmed new password
        forgot_confirmpwd_tick : Tick for confirmed new password
        forgot_pass_btn : The button to change password

        profile_user : The username in profile main page
        profile_delete : The delete button to remove account from database
        profile_logout : The logout button
        profile_myquiz : My Quiz button in profile
        profile_changeuser : Change username button in profile
        profile_changepwd : Change password button in profile
        profile_changekey : Change forgot username/password key in profile
        myquiz_scroll : The scroll area of quiz created
        myquiz_scroll_contents : The contents holding widget in scroll area
        myquiz_create : Create quiz button
        myquiz_delete : Delete selected quiz
        myquiz_open : Play selected quiz

        profile_user_fullname : The full name in Forgot Username
        profile_forgot_userkey : The lineEdit taking key
        profile_forgot_usertick : The label having tick for key
        profile_forgot_newuser : The new username
        profile_forgot_newuser_tick : The verification of new username
        profile_forgot_confirmuser : Confirmed new username
        profile_forgot_confirmuser_tick : Tick for confirmed new username
        profile_forgot_user_btn : The confirm button for changing username

        profile_pwd_fullname : The full name in Forgot Password
        profile_forgot_pwdkey : The lineEdit taking key
        profile_forgot_pwdtick : The label having tick for key
        profile_forgot_newpwd : The new password
        profile_forgot_newpwd_tick : The verification of new password
        profile_forgot_confirmpwd : Confirmed new password
        profile_forgot_confirmpwd_tick : Tick for confirmed new password
        profile_forgot_pass_btn : Confirm button for changing password

        profile_key_fullname : The full name in Generate Key
        profile_key_pwd : The password in Generate Key
        profile_key_label : The generate key label
        profile_generate_key : Generate key button

        account_mainpage_logo : The logo of the account in the home page
        profile_img : The logo of the account in the profile page

        home_btn : The home button
        home_pg : The home page
        quiz_btn : The quiz button
        quiz_pg : The quiz page
        settings_btn : The settings button
        reset_btn : The reset app button
        feedback : The feedback button
        login_button : The login button in main screen
        register_button : The register button in main screen
        second_register_button : The register button in login page
        
        settings_feedback : The feedback button in settings
        settings_about_btn : The about button in settings page
        settings_back : The back button from About page
        license : The license button in settings page
        about_back : The back button from License page
        help_btn : The help button
        settings_help : The help button in settings
        signup_login_btn : The login button in register page
        
        settings_pg : The settings page
        home_settings_pg : The settings page (home)
        about_settings_pg : The about page in settings frame
        license_pg : The license page
        help_pg : The help page
        login_pg : The login page
        register_pg : The register page
        login_mainpage : The login main page
        login_userpage : The forgot username page
        login_pwdpage : The forgot password page
        register_firstpg : The first page of register frame
        register_secondpg : The second page of register frame
        attempt_quiz_pg : The quiz attemp page
        notlog_pg : The page for login and registration
        log_pg : The page for account image and username
        result_pg : The page for result
        create_pg : The page for creating quizzes
        
        account_pg : The page for profile
        profile_none_pg : Default profile page
        profile_myquiz_pg : My Quizzes page in profile page
        profile_changeuser_pg : Change username page in profile
        profile_changepwd_pg : Change password page in profile
        profile_changekey_pg : Change forgot username/password key in profile

        quiz_title : The title of the quiz
        quiz_logo : The logo of the quiz
        quiz_scroll_contents : The widget to have question numbers
        quiz_time : Quiz Timer
        quiz_clear : Clears the option selected
        quiz_question : Label to have question
        quiz_no : Label to show number
        quiz_option_label_a : Option A Label
        quiz_option_label_b : Option B Label
        quiz_option_label_c : Option C Label
        quiz_option_label_d : Option D Label
        quiz_option_btn_a : Option A Button
        quiz_option_btn_b : Option B Button
        quiz_option_btn_c : Option C Button
        quiz_option_btn_d : Option D Button
        quiz_quit : Exit the quiz
        quiz_submit : Submit the quiz

        result_title : The title in result
        result_logo : The logo in result
        result_scroll_contents : The contents of scroll area in result
        result_correct : The correct answers
        result_incorrect : The incorrect answers
        result_unattempted : Unattempted questions
        result_total : The total questions

        create_title : The title in create quiz
        create_difficulty : The difficulty in create quiz
        create_scroll : The scroll in create quiz
        create_scroll_contents : The widget to have frames of questions
        create_add_question : Add question frame button
        create_remove_question : Remove question frame button
        create_btn : Create button

        gk_btn : The General Knowledge button in Quiz
        gk_img : The image for General Knowledge
        computers_btn : The Computers button in Quiz
        computers_img : The image for Computers
        maths_btn : The Maths button in Quiz
        maths_img : The image for Maths
        science_btn : The Science button in Quiz
        science_img : The image for Science
        tick_pixmap : The pixmap instance of tick image

        gk_difficuly : The difficulty of GK
        gk_question : The no. of questions of GK
        computers_difficuly : The difficulty of Computers
        computers_question : The no. of questions of Computers
        maths_difficuly : The difficulty of Maths
        maths_question : The no. of questions of Maths
        science_difficuly : The difficulty of Science
        science_question : The no. of questions of Science

        start_anim : The bool value to initiate start animation or not, True - No animation; False - Animation
        pre_anim : Animation for initial logo
        anim : The animation for the geometry of logo_frame
        anim2 : The animation for toggle button (True)
        anim3 : The animation for toggle button (False)
        blur_effect : The blur effect applied to bg_frame
    """

    def __init__(self) -> None:
        """The constructor for the Main_Window_Class class"""

        super().__init__() #Initiates the class with QMainWindow

        uic.loadUi(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\UI\\", "Main_App.ui"), self) #Loads the UI

        self.logger = logging.getLogger(__name__)
        self.logger.info('Main Window Launched!')

        #Settings
        self.myquiz_buttongroup = QButtonGroup()
        self.quiz_question_buttongroup = QButtonGroup()
        self.home_quiz_buttongroup = QButtonGroup()
        self.logged = False
        self.timer = False
        self.home_data_dict = dict()
        self.filter_home_data_dict = dict()
        self.count = 600
        self.quiz_dict = None
        self.start_anim = query.salt_decode(query.read_config()["SETTINGS"]["start"]) == "False"

        #Widgets
        self.bg_frame = self.findChild(QFrame, "Bg_Frame")
        self.icon_frame = self.findChild(QFrame, "Home_Quiz")
        self.logo_frame = self.findChild(QFrame, "logoFrame")
        self.logo_text = self.findChild(QLabel, "Logo_text_2")
        self.logo = self.findChild(QLabel, "logo_2")
        self.license_scroll = self.findChild(QScrollArea, "LicenseScroll")
        self.help_scroll = self.findChild(QScrollArea, "HelpScroll")

        self.stack = self.findChild(QStackedWidget, "Main_SW")
        self.settings_stack = self.findChild(QStackedWidget, "SettingsStacked")
        self.login_stack = self.findChild(QStackedWidget, "LoginStacked")
        self.register_stack = self.findChild(QStackedWidget, "RegisterStacked")
        self.account_stack = self.findChild(QStackedWidget, "Reg_Log")
        self.profile_stack = self.findChild(QStackedWidget, "ProfileWidget")

        self.home_trending_one = self.findChild(QPushButton, "one_quiz")
        self.home_trending_two = self.findChild(QPushButton, "two_quiz")
        self.home_trending_three = self.findChild(QPushButton, "three_quiz")
        self.home_search = self.findChild(QLineEdit, "searchBox")
        self.home_difficulty = self.findChild(QComboBox, "DifficultyHome")
        self.home_question_number = self.findChild(QComboBox, "NumberHome")
        self.home_scroll = self.findChild(QScrollArea, "community")
        self.home_scroll_area = self.findChild(QWidget, "community_scrollarea")

        self.username = self.findChild(QLineEdit, "Username")
        self.password = self.findChild(QLineEdit, "Password")
        self.login = self.findChild(QPushButton, "LoginButton")
        self.account_access = self.findChild(QPushButton, "Account_Name")

        self.full_name = self.findChild(QLineEdit, "RegName")
        self.gender = self.findChild(QComboBox, "Gender")
        self.birth = self.findChild(QLabel, "DOB")
        self.calendar = self.findChild(QCalendarWidget, "calendarWidget")
        self.register_next = self.findChild(QPushButton, "NextButton")
        self.register_user = self.findChild(QLineEdit, "RegUser")
        self.register_usertick = self.findChild(QLabel, "RegUserTick")
        self.confirm_register_user = self.findChild(QLineEdit, "RegConfirmUser")
        self.confirm_register_usertick = self.findChild(QLabel, "RegConfirmUserTick")
        self.register_pass = self.findChild(QLineEdit, "RegPass")
        self.register_passtick = self.findChild(QLabel, "RegPassTick")
        self.confirm_register_pass = self.findChild(QLineEdit, "RegConfirmPass")
        self.confirm_register_passtick = self.findChild(QLabel, "RegConfirmPassTick")
        self.register_key_label = self.findChild(QLabel, "KeyLabel")
        self.register_generatekey = self.findChild(QPushButton, "Generate_Key")
        self.register_btn = self.findChild(QPushButton, "RegisterSign")

        self.forgot_username = self.findChild(QPushButton, "ForgotUsername")
        self.user_fullname = self.findChild(QLineEdit, "UserFullname")
        self.forgot_userkey = self.findChild(QLineEdit, "UsernameKey")
        self.forgot_usertick = self.findChild(QLabel, "keyTick")
        self.forgot_newuser = self.findChild(QLineEdit, "NewUsername")
        self.forgot_newuser_tick = self.findChild(QLabel, "NewUserTick")
        self.forgot_confirmuser = self.findChild(QLineEdit, "ConfirmUsername")
        self.forgot_confirmuser_tick = self.findChild(QLabel, "ConfirmTick")
        self.forgot_user_btn = self.findChild(QPushButton, "UserChange")

        self.forgot_password = self.findChild(QPushButton, "ForgotPassword")
        self.pwd_fullname = self.findChild(QLineEdit, "UserFullname_2")
        self.forgot_pwdkey = self.findChild(QLineEdit, "PassKey_2")
        self.forgot_pwdtick = self.findChild(QLabel, "keyTick_2")
        self.forgot_newpwd = self.findChild(QLineEdit, "NewPass")
        self.forgot_newpwd_tick = self.findChild(QLabel, "NewPassTick")
        self.forgot_confirmpwd = self.findChild(QLineEdit, "ConfirmPass")
        self.forgot_confirmpwd_tick = self.findChild(QLabel, "ConfirmPassTick")
        self.forgot_pass_btn = self.findChild(QPushButton, "PassChange")

        self.profile_user = self.findChild(QPushButton, "ProfileName")
        self.profile_delete = self.findChild(QPushButton, "Delete")
        self.profile_logout = self.findChild(QPushButton, "Logout")
        self.profile_myquiz = self.findChild(QPushButton, "ChangeUser_2")
        self.profile_changeuser = self.findChild(QPushButton, "ChangeUser")
        self.profile_changepwd = self.findChild(QPushButton, "ChangePass")
        self.profile_changekey = self.findChild(QPushButton, "ChangeKey")
        self.myquiz_scroll = self.findChild(QScrollArea, "myquizScroll")
        self.myquiz_scroll_contents = self.findChild(QWidget, "scrollAreaWidgetContents_2")
        self.myquiz_create = self.findChild(QPushButton, "Create")
        self.myquiz_delete = self.findChild(QPushButton, "DeleteQuiz")
        self.myquiz_open = self.findChild(QPushButton, "Open")

        self.profile_user_fullname = self.findChild(QLineEdit, "ProfileUserFull")
        self.profile_forgot_userkey = self.findChild(QLineEdit, "ProfileUserKey")
        self.profile_forgot_usertick = self.findChild(QLabel, "keyTick_5")
        self.profile_forgot_newuser = self.findChild(QLineEdit, "ProfileNewUser")
        self.profile_forgot_newuser_tick = self.findChild(QLabel, "NewUserTick_3")
        self.profile_forgot_confirmuser = self.findChild(QLineEdit, "ProfileConfirmUser")
        self.profile_forgot_confirmuser_tick = self.findChild(QLabel, "ConfirmTick_3")
        self.profile_forgot_user_btn = self.findChild(QPushButton, "UserChange_3")

        self.profile_pwd_fullname = self.findChild(QLineEdit, "UserFullname_3")
        self.profile_forgot_pwdkey = self.findChild(QLineEdit, "PassKey_5")
        self.profile_forgot_pwdtick = self.findChild(QLabel, "keyTick_6")
        self.profile_forgot_newpwd = self.findChild(QLineEdit, "NewPass_2")
        self.profile_forgot_newpwd_tick = self.findChild(QLabel, "NewPassTick_3")
        self.profile_forgot_confirmpwd = self.findChild(QLineEdit, "ConfirmPass_3")
        self.profile_forgot_confirmpwd_tick = self.findChild(QLabel, "ConfirmPassTick_3")
        self.profile_forgot_pass_btn = self.findChild(QPushButton, "PassChange_3")

        self.profile_key_fullname = self.findChild(QLineEdit, "ProfileUserFull_2")
        self.profile_key_pwd = self.findChild(QLineEdit, "NewPass_5")
        self.profile_key_label = self.findChild(QLabel, "KeyLabel_2")
        self.profile_generate_key = self.findChild(QPushButton, "generate")
        self.profile_key_confirm = self.findChild(QPushButton, "PassChange_4")

        self.account_mainpage_logo = self.findChild(QLabel, "AccountLogo")
        self.profile_img = self.findChild(QLabel, "ProfileImg")

        self.sql_toggle_background = self.findChild(QLabel, "SqlToggle")
        self.account_toggle_background = self.findChild(QLabel, "AccountToggle")
        self.anim_toggle_background = self.findChild(QLabel, "AnimToggle")

        self.sql_secondary = self.findChild(QLabel, "SqlSec")
        self.account_secondary = self.findChild(QLabel, "AccountSec")
        self.anim_secondary = self.findChild(QLabel, "AnimSec")

        self.sql_toggle = self.findChild(QPushButton, "SqlButton")
        self.account_toggle = self.findChild(QPushButton, "AccountButton")
        self.anim_toggle = self.findChild(QPushButton, "AnimButton")

        self.reset_btn = self.findChild(QPushButton, "Reset")
        self.settings_feedback = self.findChild(QPushButton, "SettingsFeedback")
        self.feedback = self.findChild(QPushButton, "Feedback")
        self.login_button = self.findChild(QPushButton, "Login")
        self.register_button = self.findChild(QPushButton, "Register")
        self.second_register_button = self.findChild(QPushButton, "RegisterButton")
        self.home_btn = self.findChild(QPushButton, "homeButton")
        self.quiz_btn = self.findChild(QPushButton, "quizButton")
        self.settings_btn = self.findChild(QPushButton, "settingsButton")
        self.settings_about_btn = self.findChild(QPushButton, "About")
        self.signup_login_btn = self.findChild(QPushButton, "LoginSignup")

        self.quiz_title = self.findChild(QLabel, "TopicTitle")
        self.quiz_logo = self.findChild(QLabel, "TopicLogo")
        self.quiz_scroll_contents = self.findChild(QWidget, "scrollAreaWidgetContents")
        self.quiz_time = self.findChild(QLabel, "Time")
        self.quiz_clear = self.findChild(QPushButton, "Clear")
        self.quiz_question = self.findChild(QLabel, "Question")
        self.quiz_no = self.findChild(QLabel, "QuestionNumber")
        self.quiz_option_label_a = self.findChild(QLabel, "LabelA")
        self.quiz_option_label_b = self.findChild(QLabel, "LabelB")
        self.quiz_option_label_c = self.findChild(QLabel, "LabelC")
        self.quiz_option_label_d = self.findChild(QLabel, "LabelD")
        self.quiz_option_btn_a = self.findChild(QPushButton, "OptionA")
        self.quiz_option_btn_b = self.findChild(QPushButton, "OptionB")
        self.quiz_option_btn_c = self.findChild(QPushButton, "OptionC")
        self.quiz_option_btn_d = self.findChild(QPushButton, "OptionD")
        self.quiz_quit = self.findChild(QPushButton, "Quit")
        self.quiz_submit = self.findChild(QPushButton, "Submit")

        self.result_title = self.findChild(QLabel, "ResultTitle")
        self.result_logo = self.findChild(QLabel, "ResultLogo")
        self.result_scroll_contents = self.findChild(QWidget, "scrollAreaWidgetContents_4")
        self.result_correct = self.findChild(QLabel, "Correct")
        self.result_incorrect = self.findChild(QLabel, "Incorrect")
        self.result_unattempted = self.findChild(QLabel, "Incorrect_2")
        self.result_total = self.findChild(QLabel, "Total")

        self.create_title = self.findChild(QLineEdit, "Title_Quiz")
        self.create_difficulty = self.findChild(QComboBox, "CreateDifficulty")
        self.create_scroll = self.findChild(QScrollArea, "CreateScroll")
        self.create_scroll_contents = self.findChild(QWidget, "scrollAreaWidgetContents_3")
        self.create_add_question = self.findChild(QPushButton, "AddQuestion")
        self.create_remove_question = self.findChild(QPushButton, "AddQuestion_2")
        self.create_btn = self.findChild(QPushButton, "CreateQuiz")

        self.gk_btn = self.findChild(QPushButton, "GK")
        self.gk_img = self.findChild(QLabel, "GKLabel")
        self.computers_btn = self.findChild(QPushButton, "Computers")
        self.computers_img = self.findChild(QLabel, "ComputersLabel")
        self.maths_btn = self.findChild(QPushButton, "Maths")
        self.maths_img = self.findChild(QLabel, "MathsLabel")
        self.science_btn = self.findChild(QPushButton, "Science")
        self.science_img = self.findChild(QLabel, "ScienceLabel")

        self.gk_difficuly = self.findChild(QComboBox, "DifficultyGK")
        self.gk_question = self.findChild(QComboBox, "NumberGK")
        self.computers_difficuly = self.findChild(QComboBox, "DifficultyComputers")
        self.computers_question = self.findChild(QComboBox, "NumberComputers")
        self.maths_difficuly = self.findChild(QComboBox, "DifficultyMaths")
        self.maths_question = self.findChild(QComboBox, "NumberMaths")
        self.science_difficuly = self.findChild(QComboBox, "DifficultyScience")
        self.science_question = self.findChild(QComboBox, "NumberScience")

        self.settings_back = self.findChild(QPushButton, "back")
        self.about_back = self.findChild(QPushButton, "backAbout")
        self.license = self.findChild(QPushButton, "OSLicense")
        self.help_btn = self.findChild(QPushButton, "helpButton")
        self.settings_help = self.findChild(QPushButton, "SettingsHelp")

        self.home_pg = self.findChild(QWidget, "homepage")
        self.quiz_pg = self.findChild(QWidget, "quizpage")
        self.settings_pg = self.findChild(QWidget, "settingspage")
        self.home_settings_pg = self.findChild(QWidget, "homeSettings")
        self.about_settings_pg = self.findChild(QWidget, "aboutpage")
        self.license_pg = self.findChild(QWidget, "licensepage")
        self.help_pg = self.findChild(QWidget, "helppage")
        self.login_pg = self.findChild(QWidget, "loginpage")
        self.register_pg = self.findChild(QWidget, "registerpage")
        self.login_mainpage = self.findChild(QWidget, "mainpage")
        self.login_userpage = self.findChild(QWidget, "usernamepage")
        self.login_pwdpage = self.findChild(QWidget, "passwordpage")
        self.register_firstpg = self.findChild(QWidget, "userpasspage")
        self.register_secondpg = self.findChild(QWidget, "secondpage")
        self.attempt_quiz_pg = self.findChild(QWidget, "doquizpage")
        self.notlog_pg = self.findChild(QWidget, "Login_Widget")
        self.log_pg = self.findChild(QWidget, "Account_Widget")
        self.result_pg = self.findChild(QWidget, "resultpage")
        self.create_pg = self.findChild(QWidget, "createquizpage")

        self.account_pg = self.findChild(QWidget, "accountpage")
        self.profile_none_pg = self.findChild(QWidget, "nonepage")
        self.profile_myquiz_pg = self.findChild(QWidget, "myquizpage")
        self.profile_changeuser_pg = self.findChild(QWidget, "user")
        self.profile_changepwd_pg = self.findChild(QWidget, "pass")
        self.profile_changekey_pg = self.findChild(QWidget, "key")

        #Animations
        if self.start_anim is False:
            self.pre_anim = QtCore.QPropertyAnimation(self.logo, b"geometry")
            self.pre_anim.setDuration(250) #.25 seconds
            self.pre_anim.setStartValue(QtCore.QRect(70, 0, 71, 71)) #Center
            self.pre_anim.setEndValue(QtCore.QRect(0, 0, 71, 71)) #Little left
            self.pre_anim.finished.connect(lambda: self.add_text_logo()) #Triggers adding text function

            self.anim = QtCore.QPropertyAnimation(self.logo_frame, b"geometry") #Animation for changing geometry
            self.anim.setDuration(650) #.65 seconds duration
            self.anim.setStartValue(QtCore.QRect(290, 250, 221, 71)) #Center
            self.anim.setEndValue(QtCore.QRect(20, 20, 221, 71)) #Top-right
            self.anim.finished.connect(lambda: self.remove_blur()) #Removes blur after the logo animation ends

        #Toggles
        self.sql_toggle.setChecked(query.salt_decode(query.read_config()["SETTINGS"]["sql"]) == "True") #Sets the checked value of the button
        self.toggle(False, self.sql_toggle, self.sql_toggle_background, 28, self.sql_secondary, "sql", ["SQL Login data will be saved", "SQL Login data will not be saved"]) #Adjusts the button

        self.account_toggle.setChecked(query.salt_decode(query.read_config()["SETTINGS"]["rememberaccount"]) == "True")
        self.toggle(False, self.account_toggle, self.account_toggle_background, 107, self.account_secondary, "rememberaccount", ["Automatic Login", "You will have to login everytime with app restart"])

        self.anim_toggle.setChecked(query.salt_decode(query.read_config()["SETTINGS"]["start"]) == "False")
        self.toggle(False, self.anim_toggle, self.anim_toggle_background, 186, self.anim_secondary, "start", ["Startup Animation Disabled", "Startup Animation is Active"])

        #Defaults
        self.tick_pixmap = QPixmap(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", "tick.png"))
        self.register = False #To know registration process
        self.myquiz_selected = False #The selected pushbutton for my quizzes
        self.selected = self.home_btn #Active frame

        self.mytimer = QtCore.QTimer(self)
        self.mytimer.timeout.connect(self.change_timer)
        self.mytimer.start(1000)

        if (query.salt_decode(query.read_config()["SETTINGS"]["rememberaccount"]) == "True") is False:
            query.edit_config("SETTINGS", "rememberaccount", "False")

        if 'guest' not in query.salt_decode(query.read_config()['LOGIN']['accountlogin']):
            self.logged = True

        self.frame_page(self.home_btn, self.home_pg, 'home')
        
        self.imgdata = open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", "default.png"), 'rb').read()
        self.pix_map = mask_image(self.imgdata)

        self.account_mainpage_logo.setPixmap(self.pix_map)
        self.profile_img.setPixmap(self.pix_map)

        if self.start_anim is False:
            self.bg_frame.setEnabled(self.start_anim) #Sets the value to the config in settings
            self.logo_frame.setGeometry(290, 250, 221, 71) #Sets app logo in the middle
            self.logo_text.setText('') #Removes the text
            self.logo.setGeometry(70, 0, 71, 71) #Sets the logo at the center

        #Effects
        if self.start_anim is False:
            self.blur_effect = QGraphicsBlurEffect() #Blur effect
            self.blur_effect.setBlurRadius(10) #Sets blur
            self.bg_frame.setGraphicsEffect(self.blur_effect) #Initializes the effect

        #Connections
        self.home_btn.enterEvent = lambda b: self.hover_change_image(self.home_btn)
        self.home_btn.leaveEvent = lambda b: self.hover_change_image(self.home_btn, True)
        self.quiz_btn.enterEvent = lambda b: self.hover_change_image(self.quiz_btn)
        self.quiz_btn.leaveEvent = lambda b: self.hover_change_image(self.quiz_btn, True)
        self.settings_btn.enterEvent = lambda b: self.hover_change_image(self.settings_btn)
        self.settings_btn.leaveEvent = lambda b: self.hover_change_image(self.settings_btn, True)
        self.help_btn.enterEvent = lambda b: self.hover_change_image(self.help_btn)
        self.help_btn.leaveEvent = lambda b: self.hover_change_image(self.help_btn, True)

        #Events
        self.calendar.selectionChanged.connect(lambda: self.birth.setText('-'.join(str(self.calendar.selectedDate().toPyDate()).split('-')[::-1])))

        self.username.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;"], self.username))
        self.password.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;"], self.password))
        self.user_fullname.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"], self.user_fullname))
        self.pwd_fullname.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"], self.pwd_fullname))
        self.full_name.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"], self.full_name))
        self.calendar.selectionChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"], self.birth))
        
        self.profile_user_fullname.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"], self.profile_user_fullname))
        self.profile_pwd_fullname.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"], self.profile_pwd_fullname))
        self.profile_key_fullname.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"], self.profile_key_fullname))
        self.profile_key_pwd.textChanged.connect(lambda: self.change_style(["background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;", "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"], self.profile_key_pwd))

        #Triggers frame_page function
        self.home_btn.clicked.connect(lambda: self.frame_page(self.home_btn, self.home_pg, 'home'))
        self.quiz_btn.clicked.connect(lambda: self.frame_page(self.quiz_btn, self.quiz_pg))
        self.settings_btn.clicked.connect(lambda: self.frame_page(self.settings_btn, self.settings_pg, 'settings'))
        self.help_btn.clicked.connect(lambda: self.frame_page(self.help_btn, self.help_pg, 'help'))
        self.settings_help.clicked.connect(lambda: self.frame_page(self.help_btn, self.help_pg, 'help'))

        #Home
        self.home_trending_one.clicked.connect(self.trending_start_quiz)
        self.home_trending_two.clicked.connect(self.trending_start_quiz)
        self.home_trending_three.clicked.connect(self.trending_start_quiz)
        self.home_quiz_buttongroup.buttonClicked.connect(lambda btn: self.start_quiz(btn))
        self.home_search.textChanged.connect(lambda: self.home_changed_search())
        self.home_difficulty.currentTextChanged.connect(self.home_changed_difficulty)
        self.home_question_number.currentTextChanged.connect(self.home_changed_question)

        #Quiz
        self.quiz_quit.clicked.connect(lambda: self.frame_page(self.home_btn, self.home_pg, 'home'))
        self.quiz_question_buttongroup.buttonClicked.connect(self.quiz_change_question)
        self.quiz_option_btn_a.clicked.connect(self.quiz_option_clicked)
        self.quiz_option_btn_b.clicked.connect(self.quiz_option_clicked)
        self.quiz_option_btn_c.clicked.connect(self.quiz_option_clicked)
        self.quiz_option_btn_d.clicked.connect(self.quiz_option_clicked)
        self.quiz_clear.clicked.connect(self.clear_options)
        self.quiz_submit.clicked.connect(self.show_result)
        self.create_add_question.clicked.connect(self.create_add)
        self.create_remove_question.clicked.connect(self.create_remove)
        self.create_btn.clicked.connect(self.create_quiz)

        #Profile
        self.account_access.clicked.connect(self.profile)
        self.profile_logout.clicked.connect(self.account_log_delete)
        self.profile_delete.clicked.connect(lambda: self.account_log_delete(delete=True))
        self.profile_myquiz.clicked.connect(lambda: self.change_profile_page(self.profile_myquiz_pg))
        self.profile_changeuser.clicked.connect(lambda: self.change_profile_page(self.profile_changeuser_pg))
        self.profile_changepwd.clicked.connect(lambda: self.change_profile_page(self.profile_changepwd_pg))
        self.profile_changekey.clicked.connect(lambda: self.change_profile_page(self.profile_changekey_pg))
        self.profile_user_fullname.textChanged.connect(lambda: self.profile_key_check())
        self.profile_forgot_userkey.textChanged.connect(lambda: self.profile_key_check())
        self.profile_pwd_fullname.textChanged.connect(lambda: self.profile_key_check(True))
        self.profile_forgot_pwdkey.textChanged.connect(lambda: self.profile_key_check(True))
        self.profile_forgot_newuser.textChanged.connect(lambda: self.profile_login_label())
        self.profile_forgot_confirmuser.textChanged.connect(lambda: self.profile_login_label(confirm=True))
        self.profile_forgot_newpwd.textChanged.connect(lambda: self.profile_login_label(pwd=True))
        self.profile_forgot_confirmpwd.textChanged.connect(lambda: self.profile_login_label(pwd=True, confirm=True))
        self.profile_generate_key.clicked.connect(lambda: self.profile_gen(self.profile_key_label))
        self.profile_forgot_user_btn.clicked.connect(self.profile_confirm)
        self.profile_forgot_pass_btn.clicked.connect(lambda: self.profile_confirm(pwd=True))
        self.profile_key_confirm.clicked.connect(self.profile_change_generatekey)
        self.myquiz_buttongroup.buttonClicked.connect(self.profile_select_button)
        self.myquiz_open.clicked.connect(self.open_quiz)
        self.myquiz_delete.clicked.connect(self.delete_quiz)
        self.myquiz_create.clicked.connect(self.profile_create_quiz)

        #Login
        self.login.clicked.connect(self.login_check)
        self.user_fullname.textChanged.connect(lambda: self.forgot_key_check())
        self.forgot_userkey.textChanged.connect(lambda: self.forgot_key_check())
        self.pwd_fullname.textChanged.connect(lambda: self.forgot_key_check(True))
        self.forgot_pwdkey.textChanged.connect(lambda: self.forgot_key_check(True))
        self.forgot_newuser.textChanged.connect(lambda: self.forgot_login_label())
        self.forgot_confirmuser.textChanged.connect(lambda: self.forgot_login_label(confirm=True))
        self.forgot_newpwd.textChanged.connect(lambda: self.forgot_login_label(pwd=True))
        self.forgot_confirmpwd.textChanged.connect(lambda: self.forgot_login_label(pwd=True, confirm=True))
        self.forgot_user_btn.clicked.connect(self.forgot_confirm)
        self.forgot_pass_btn.clicked.connect(lambda: self.forgot_confirm(pwd=True))

        #Registration
        self.register_btn.clicked.connect(self.register_sucess)
        self.register_user.textChanged.connect(lambda: self.register_process())
        self.confirm_register_user.textChanged.connect(lambda: self.register_process(confirm=True))
        self.register_pass.textChanged.connect(lambda: self.register_process(True))
        self.confirm_register_pass.textChanged.connect(lambda: self.register_process(True, True))

        #Triggers toggle button
        self.sql_toggle.clicked.connect(lambda: self.toggle(True, self.sql_toggle, self.sql_toggle_background, 28, self.sql_secondary, "sql", ["SQL Login data will be saved", "SQL Login data will not be saved"]))
        self.account_toggle.clicked.connect(lambda: self.toggle(True, self.account_toggle, self.account_toggle_background, 107, self.account_secondary, "rememberaccount", ["Automatic Login", "You will have to login everytime with app restart"]))
        self.anim_toggle.clicked.connect(lambda: self.toggle(True, self.anim_toggle, self.anim_toggle_background, 186, self.anim_secondary, "start", ["Startup Animation Disabled", "Startup Animation is Active"]))

        #Button Triggers
        self.reset_btn.clicked.connect(self.reset_app_data)
        self.settings_feedback.clicked.connect(self.send_feedback)
        self.feedback.clicked.connect(self.send_feedback)
        self.login_button.clicked.connect(self.reset_login)
        self.signup_login_btn.clicked.connect(self.reset_login)
        self.forgot_username.clicked.connect(self.forgot_login)
        self.register_next.clicked.connect(self.registration_next_reset)
        self.register_generatekey.clicked.connect(lambda: self.generate_key(self.register_generatekey, self.register_key_label))

        self.gk_btn.clicked.connect(lambda: self.start_quiz(self.gk_btn, self.gk_img, 'GK'))
        self.computers_btn.clicked.connect(lambda: self.start_quiz(self.computers_btn, self.computers_img, 'Computers'))
        self.maths_btn.clicked.connect(lambda: self.start_quiz(self.maths_btn, self.maths_img, 'Maths'))
        self.science_btn.clicked.connect(lambda: self.start_quiz(self.science_btn, self.science_img, 'Science'))

        self.forgot_password.clicked.connect(lambda: self.forgot_login(True))
        self.register_button.clicked.connect(lambda: self.reset_login(True))
        self.second_register_button.clicked.connect(lambda: self.reset_login(True))

        self.settings_about_btn.clicked.connect(lambda: self.settings_stack.setCurrentWidget(self.about_settings_pg))
        self.settings_back.clicked.connect(lambda: self.settings_stack.setCurrentWidget(self.home_settings_pg))
        self.license.clicked.connect(lambda: self.settings_stack.setCurrentWidget(self.license_pg))
        self.about_back.clicked.connect(lambda: self.settings_stack.setCurrentWidget(self.about_settings_pg))

        self.about_back.clicked.connect(lambda: self.license_scroll.verticalScrollBar().setValue(0))
        self.about_back.clicked.connect(lambda: self.license_scroll.horizontalScrollBar().setValue(0))
    
    #Functions
    @staticmethod
    def wait(time=10):
        """
        Custom wait to prevent freezing of the UI.

        Parameters:
            time [int] : time/10 seconds
        """

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(time*100, loop.quit)
        loop.exec()


    def handler(msg_type, msg_log_context, msg_string):
        """The warning message handler"""
        pass
    QtCore.qInstallMessageHandler(handler) #Installs message handler for warnings


    def closeEvent(self, a0: QCloseEvent) -> None:
        """
        Triggered after the closing of the MainWindow.

        Parameters:
            a0 : The close event of the window
        """

        super().closeEvent(a0) #Triggeres close event

        #Clears Cache
        path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Data\\", "Cache\\") #The path for the Cache folder
        
        for file_name in os.listdir(path): #Gets the list of the files
            file = path + file_name #Constructs full file path
            if os.path.isfile(file):
                os.remove(file) #Removes the files
        
        self.logger.info('App Closed!')

        if os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Logs\\", "QuizAppLog.log")):
            #Creates backup of log file
            log_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Logs\\", "QuizAppLog.log")
            new_log_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Logs\\", f"QuizAppLog-backup-{datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S,%f')}.log")

            shutil.copy2(log_file, new_log_file) #Generates a backup file

        #Checks and removes old log files
        path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\", "Logs\\")
        log_file = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        for file in log_file:
            file_name = os.path.splitext(file)[0]
            if 'QuizAppLog-backup-' in file_name:
                file_name = file_name.replace('QuizAppLog-backup-', '')

                try:
                    if datetime.datetime.strptime(file_name, "%d-%m-%Y %H.%M.%S,%f") <= (datetime.datetime.strptime(date.today().strftime("%d-%m-%Y %H.%M.%S,%f"), "%d-%m-%Y %H.%M.%S,%f") - timedelta(days=2)):
                        os.remove(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\QuizBoxClient\\Logs\\", file))
                except ValueError as err:
                    self.logger.warning(err)


    def create_quiz(self):
        """Creates and adds quiz data to database"""

        data_dict = dict() #Data dictionary

        #Checks all the stuff
        if self.create_title.text() == '':
            QMessageBox.warning(self, 'ERROR', 'Title is empty!')
            return

        if self.create_title.text() in ['GK', 'Maths', 'Science', 'Computers']:
            QMessageBox.warning(self, 'ERROR', f'{self.create_title.text()} not allowed in title!')
            return

        for frame in self.create_scroll_contents.findChildren(QFrame):
            if frame.objectName() == '':
                continue

            data = dict() #Dictionary for question data
            option_list = list() #Options list

            #Question
            for question in frame.findChildren(QLineEdit, 'Question'):
                if question.text() == '':
                    QMessageBox.warning(self, 'ERROR', f'S.No. {frame.objectName()}, Question field(s) incomplete!')
                    return

                data[question.objectName()] = question.text()
            
            #Options
            for option in frame.findChildren(QLineEdit, 'Option'):
                if question.text() == '':
                    QMessageBox.warning(self, 'ERROR', f'S.No. {frame.objectName()}, Option field(s) incomplete!')
                    return
                
                if ',' in option.text():
                    QMessageBox.warning(self, 'ERROR', f'S.No. {frame.objectName()}, [,](comma) not allowed in Option field(s)!')
                    return

                option_list.append(option.text())
            
            if len(list(set(option_list))) != 4:
                QMessageBox.warning(self, 'ERROR', f'S.No. {frame.objectName()}, Option field(s) similar!')
                return

            data['Options'] = ','.join(option_list)

            #Answers
            for answer in frame.findChildren(QLineEdit, 'Answer'):
                if answer.text() not in option_list:
                    QMessageBox.warning(self, 'ERROR', f'S.No. {frame.objectName()}, Answer field(s) does not match Option field(s)!')
                    return
                
                data[answer.objectName()] = answer.text()

            #Assigns data
            data_dict[frame.objectName()] = data

        if self.confirm('Do you want to proceed?\n\nThe data of the quiz can no longer be edited afterwards.'):
            query.sql_query(
                insert_query='insert into quizzes (Username, QuizTitle, UniqueKey, Data, Difficulty) values (%s, %s, %s, %s, %s)',
                insert_query_values=(self.account_access.text(), self.create_title.text(), query.random_key(True), json.dumps(data_dict), self.create_difficulty.currentText())
            )
            
            self.register = False
            QMessageBox.information(self, 'SUCCESS', 'Quiz created successfully!')
            self.frame_page(self.home_btn, self.home_pg, 'home')
                

    def create_remove(self):
        """Checks and removes quiz data frame"""

        #Gets the list of frames
        for frame in self.create_scroll_contents.findChildren(QFrame)[::-1][:2]:
            frame.deleteLater() #Deletes the last frame

        #Executions
        number = int(len(self.create_scroll_contents.findChildren(QFrame)) / 2)
        if 5 <= number <= 10:
            self.create_remove_question.setEnabled(True)
            self.create_add_question.setEnabled(True)
            self.create_btn.setEnabled(True)
        elif number > 10:
            self.create_add_question.setEnabled(False)
            self.create_remove_question.setEnabled(True)
            self.create_btn.setEnabled(False)
        elif 1 < number < 5:
            self.create_remove_question.setEnabled(True)
            self.create_btn.setEnabled(False)
        elif number == 1:
            self.create_btn.setEnabled(False)
            self.create_remove_question.setEnabled(False)


    def create_add(self):
        """Checks and adds quiz data frame"""

        #Gets the number of frame
        number = int((len(self.create_scroll_contents.findChildren(QFrame))/2) + 1)
        self.create_frame(number) #Creates the frame

        #Scrolls down
        bar = self.create_scroll.verticalScrollBar()
        bar.rangeChanged.connect(lambda _, y: bar.setValue(y))

        #Executions
        if 5 <= number < 10:
            self.create_remove_question.setEnabled(True)
            self.create_btn.setEnabled(True)
        elif number >= 10:
            self.create_add_question.setEnabled(False)
            self.create_remove_question.setEnabled(True)
        elif 1 < number < 5:
            self.create_remove_question.setEnabled(True)
            self.create_btn.setEnabled(False)
        elif number == 1:
            self.create_btn.setEnabled(False)
            self.create_remove_question.setEnabled(False)


    def profile_create_quiz(self):
        """Sets create quiz page."""

        self.register = True #Exit-safe

        #Removes previous frames
        for f in self.create_scroll_contents.findChildren(QFrame):
            f.deleteLater()

        #Resets enabling commands
        self.create_add_question.setEnabled(True)
        self.create_remove_question.setEnabled(False)
        self.create_btn.setEnabled(False)

        #Resets text
        self.create_difficulty.setCurrentText('Easy')
        self.create_title.setText('')

        self.create_frame() #Creates frame

        self.stack.setCurrentWidget(self.create_pg) #Changes page


    def create_frame(self, num: int=1):
        """
        Creates frame for create quiz.
        
        Parameters:
            num [int] [Default: 1] : The number of quiz
        """

        #Creates widgets
        layout = self.create_scroll_contents.layout()

        #Frame
        frame = QFrame(self)
        lay = QGridLayout()

        #Sets the frame
        frame.setObjectName(str(num))
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame.setStyleSheet("border-top-left-radius : 0px;\nborder-top-right-radius : 0px;\nborder: 2px solid black;")
        frame.setMinimumSize(561, 171)
        frame.setMaximumSize(561, 171)

        #Sets the question number label
        question_label_no = QLabel()
        question_label_no.setText(str(num))
        question_label_no.setMinimumSize(31, 31)
        question_label_no.setMaximumSize(31, 31)
        question_label_no.setFont(QFont('MS Shell Dlg 2', 12))
        question_label_no.setStyleSheet("border: 1px solid black;\nbackground-color: rgb(255, 255, 255);\nborder-style: outset;\nborder-radius: 15px;\npadding: 4px;")
        question_label_no.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        #Sets the question line
        question_line = QLineEdit()
        question_line.setObjectName('Question')
        question_line.setMinimumHeight(30)
        question_line.setFont(QFont('MS Shell Dlg 2', 12))
        question_line.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid black;")
        question_line.setPlaceholderText('Question (max. 100)')
        question_line.setMaxLength(100)
        question_line.setClearButtonEnabled(True)
        question_line.setFixedWidth(506)

        #Option A
        opt_a_line = QLineEdit()
        opt_a_line.setObjectName('Option')
        opt_a_line.setMinimumSize(241, 30)
        opt_a_line.setMaximumSize(241, 30)
        opt_a_line.setFont(QFont('MS Shell Dlg 2', 11))
        opt_a_line.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid white;")
        opt_a_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        opt_a_line.setPlaceholderText('Option (max. 50)')
        opt_a_line.setMaxLength(50)
        opt_a_line.setClearButtonEnabled(True)

        #Option B
        opt_b_line = QLineEdit()
        opt_b_line.setObjectName('Option')
        opt_b_line.setMinimumSize(241, 30)
        opt_b_line.setMaximumSize(241, 30)
        opt_b_line.setFont(QFont('MS Shell Dlg 2', 11))
        opt_b_line.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid white;")
        opt_b_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        opt_b_line.setPlaceholderText('Option (max. 50)')
        opt_b_line.setMaxLength(50)
        opt_b_line.setClearButtonEnabled(True)

        #Option C
        opt_c_line = QLineEdit()
        opt_c_line.setObjectName('Option')
        opt_c_line.setMinimumSize(241, 30)
        opt_c_line.setMaximumSize(241, 30)
        opt_c_line.setFont(QFont('MS Shell Dlg 2', 11))
        opt_c_line.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid white;")
        opt_c_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        opt_c_line.setPlaceholderText('Option (max. 50)')
        opt_c_line.setMaxLength(50)
        opt_c_line.setClearButtonEnabled(True)

        #Option D
        opt_d_line = QLineEdit()
        opt_d_line.setObjectName('Option')
        opt_d_line.setMinimumSize(241, 30)
        opt_d_line.setMaximumSize(241, 30)
        opt_d_line.setFont(QFont('MS Shell Dlg 2', 11))
        opt_d_line.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid white;")
        opt_d_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        opt_d_line.setPlaceholderText('Option (max. 50)')
        opt_d_line.setMaxLength(50)
        opt_d_line.setClearButtonEnabled(True)

        #Answer
        ans_line = QLineEdit()
        ans_line.setObjectName('Answer')
        ans_line.setMinimumSize(241, 30)
        ans_line.setMaximumSize(241, 30)
        ans_line.setFont(QFont('MS Shell Dlg 2', 11))
        ans_line.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid white;")
        ans_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        ans_line.setPlaceholderText('Answer (max. 50)')
        ans_line.setMaxLength(50)
        ans_line.setClearButtonEnabled(True)

        #Layout Settings
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        lay.setColumnStretch(0, 0)
        lay.setColumnStretch(1, 10)
        lay.setColumnStretch(2, 28)

        #Sets the widgets
        lay.addWidget(question_label_no, 0, 0)
        lay.addWidget(question_line, 0, 1)
        lay.addWidget(opt_a_line, 1, 1)
        lay.addWidget(opt_b_line, 1, 2)
        lay.addWidget(opt_c_line, 2, 1)
        lay.addWidget(opt_d_line, 2, 2)
        lay.addWidget(ans_line, 3, 2)

        #Sets the frame and layouts
        frame.setLayout(lay)
        layout.addWidget(frame)


    def delete_quiz(self):
        """Deletes the quiz"""

        if self.confirm('Do you really want to delete the quiz?\n\nThere will be no way to get it back again!'):
            btn = self.myquiz_buttongroup.checkedButton()

            query.sql_query(
                insert_query='delete from quizzes where UniqueKey = %s and QuizTitle = %s',
                insert_query_values=(btn.objectName(), btn.text())
            )

            btn.deleteLater()

            QMessageBox.information(self, 'SUCCESS', 'Quiz deleted successfully!')


    def open_quiz(self, btn=None):
        """
        Opens the quiz after clicking the button.

        Parameters:
            btn [Default: None] : The button clicked
        """

        if btn:
            self.start_quiz(btn)
            return

        self.start_quiz(self.myquiz_buttongroup.checkedButton())


    def profile_select_button(self, btn):
        """
        Selects the buttons and unselect others.

        Parameters:
            btn : The button clicked
        """

        #Unselects the tyle of button
        for b in self.myquiz_buttongroup.buttons():
            if b.styleSheet() == "color: rgb(255, 255, 255);\nbackground-color: rgb(0, 0, 0);\nborder-top-left-radius : 10px;\nborder-top-right-radius : 10px; \nborder-bottom-left-radius : 10px; \nborder-bottom-right-radius : 10px;":
                b.setStyleSheet("background-color: rgb(255, 255, 255);\nborder-top-left-radius : 10px;\nborder-top-right-radius : 10px; \nborder-bottom-left-radius : 10px; \nborder-bottom-right-radius : 10px;")
                break
        
        #Sets the style of selected button
        btn.setStyleSheet("color: rgb(255, 255, 255);\nbackground-color: rgb(0, 0, 0);\nborder-top-left-radius : 10px;\nborder-top-right-radius : 10px; \nborder-bottom-left-radius : 10px; \nborder-bottom-right-radius : 10px;")
        
        #Sets Open and Delete buttons
        self.myquiz_open.setEnabled(True)
        self.myquiz_delete.setEnabled(True)
        self.myquiz_delete.setStyleSheet("color: rgb(0, 0, 0);\nbackground-color: rgb(255, 255, 255);")
        self.myquiz_open.setStyleSheet("color: rgb(0, 0, 0);\nbackground-color: rgb(255, 255, 255);")


    def profile_change_generatekey(self):
        """Generates a new key for forgot username/password"""

        if self.profile_key_fullname.text() != '' and len(self.profile_key_pwd.text()) >= 8 and self.profile_key_label.text() != '':
            confirm = self.confirm('Do you want to change your Authorization key?\n\nMake sure to copy and save it in a secured location.')
            if confirm:
                query.sql_query(
                    insert_query= 'update accounts set Auth = %s where Fullname = %s and Password = %s',
                    insert_query_values= (self.profile_key_label.text(), self.profile_key_fullname.text(), query.salt_hash(self.profile_key_pwd.text()))
                )
                self.register = False
                QMessageBox.warning(self, 'SUCCESS', 'Forgot Username/Password key changed successfully!')
                self.frame_page(self.home_btn, self.home_pg, 'home')
            return
        self.incomplete()


    def profile_confirm(self, pwd: bool = False):
        """
        Confirms the change of username/password.

        Parameters:
            pwd [bool] [Default: False] : Profile change password execution
        """

        #Forgot password
        if pwd:
            if self.profile_forgot_pwdtick.pixmap().toImage() == self.profile_forgot_newpwd_tick.pixmap().toImage() == self.tick_pixmap.toImage():
                #Change password
                inf = self.confirm('Do you want to change the password?\n\nYou will have to login again!')
                if inf:
                    query.sql_query(
                        insert_query='update accounts set Password = %s where Fullname = %s and Auth = %s',
                        insert_query_values=(query.salt_hash(self.profile_forgot_confirmpwd.text()), self.profile_pwd_fullname.text(), self.profile_forgot_pwdkey.text())
                    )
                    self.register = False
                    query.edit_config('LOGIN', 'accountlogin', 'False')
                    QMessageBox.information(self, 'Success', 'Password changed successfully! You may now login!')
                    self.frame_page(self.home_btn, self.home_pg, 'home')
                    self.reset_login()
                return
            self.incomplete()
            return
        
        #Forgot username
        if self.profile_forgot_usertick.pixmap().toImage() == self.profile_forgot_newuser_tick.pixmap().toImage() == self.tick_pixmap.toImage():
            #Change username
            info = self.confirm('Do you want to change the username?\n\nYou will have to login again!')
            if info:
                query.sql_query(
                    insert_query='update accounts set Username = %s where Fullname = %s and Auth = %s',
                    insert_query_values=(self.profile_forgot_confirmuser.text(), self.profile_user_fullname.text(), self.profile_forgot_userkey.text())
                )
                self.register = False
                query.edit_config('LOGIN', 'accountlogin', 'False')
                QMessageBox.information(self, 'Success', 'Username changed successfully! You may now login!')
                self.frame_page(self.home_btn, self.home_pg, 'home')
                self.reset_login()
            return
        self.incomplete()


    def profile_gen(self, label):
        """
        Generates new key for forgot username/password.

        Parameters:
            label : The label to show the key
        """

        check = query.sql_query(
                    get_query='select Username from accounts where Username = %s and Password = %s and Fullname = %s',
                    get_query_values=(self.account_access.text(), query.salt_hash(self.profile_key_pwd.text()), self.profile_key_fullname.text())
                )

        if check:
            self.generate_key(self.sender(), label)
            self.profile_key_fullname.setEnabled(False)
            self.profile_key_pwd.setEnabled(False)
            return
        QMessageBox.warning(self, 'ERROR', 'Fullname or Password is incorrect!')


    def profile_key_check(self, pwd: bool = False):
        """
        Checks the user/pass key, and takes care of execution.

        Parameters:
            pwd [bool] [Default: False] : The profile change password
        """

        style = "background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"
        red_style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"

        if pwd:
            val = query.sql_query(
                get_query='select Username from accounts where Fullname = %s and Auth = %s',
                get_query_values=(self.profile_pwd_fullname.text(), self.profile_forgot_pwdkey.text())
            )

            if val:
                self.profile_forgot_newpwd.setEnabled(True)
                self.profile_forgot_confirmpwd.setEnabled(True)
                self.profile_forgot_pwdkey.setStyleSheet(style)
                self.profile_forgot_pwdtick.setPixmap(self.tick_pixmap)
                return
            self.profile_forgot_pwdkey.setStyleSheet(red_style)
            self.profile_forgot_pwdtick.setPixmap(QPixmap())
            self.profile_forgot_newpwd.setEnabled(False)
            self.profile_forgot_newpwd.setText('')
            self.profile_forgot_newpwd.setStyleSheet(red_style)
            self.profile_forgot_newpwd_tick.setPixmap(QPixmap())
            self.profile_forgot_confirmpwd.setEnabled(False)
            self.profile_forgot_confirmpwd.setText('')
            self.profile_forgot_confirmpwd.setStyleSheet(red_style)
            self.profile_forgot_confirmpwd_tick.setPixmap(QPixmap())
            return

        value = query.sql_query(
            get_query='select Username from accounts where Fullname = %s and Auth = %s',
            get_query_values=(self.profile_user_fullname.text(), self.profile_forgot_userkey.text())
        )

        if value:
            self.profile_forgot_newuser.setEnabled(True)
            self.profile_forgot_confirmuser.setEnabled(True)
            self.profile_forgot_userkey.setStyleSheet(style)
            self.profile_forgot_usertick.setPixmap(self.tick_pixmap)
            return
        self.profile_forgot_userkey.setStyleSheet(red_style)
        self.profile_forgot_usertick.setPixmap(QPixmap())
        self.profile_forgot_newuser.setEnabled(False)
        self.profile_forgot_newuser.setText('')
        self.profile_forgot_newuser.setStyleSheet(red_style)
        self.profile_forgot_newuser_tick.setPixmap(QPixmap())
        self.profile_forgot_confirmuser.setEnabled(False)
        self.profile_forgot_confirmuser.setText('')
        self.profile_forgot_confirmuser.setStyleSheet(red_style)
        self.profile_forgot_confirmuser_tick.setPixmap(QPixmap())


    def profile_login_label(self, pwd: bool = False, confirm: bool = False):
        """
        Takes care about the execution of profile username/password.

        Parameters:
            pwd [bool] [Default: False] : To execute profile change password
            confirm [bool] [Default: False] : To execute the confirm labels
        """

        style = "background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"
        red_style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"

        #Password execution
        if pwd:
            if confirm:
                if self.profile_forgot_confirmpwd.text() != '':
                    if len(self.profile_forgot_newpwd.text()) >= 8:
                        if self.profile_forgot_newpwd.text() == self.profile_forgot_confirmpwd.text():
                            self.profile_forgot_confirmpwd.setStyleSheet(style)
                            self.profile_forgot_confirmpwd_tick.setPixmap(self.tick_pixmap)
                            return
                        self.profile_forgot_confirmpwd.setStyleSheet(red_style)
                        self.profile_forgot_confirmpwd_tick.setPixmap(QPixmap())
                        return
                    self.profile_forgot_confirmpwd.setStyleSheet(red_style)
                    self.profile_forgot_confirmpwd_tick.setPixmap(QPixmap())
                else:
                    self.profile_forgot_confirmpwd.setStyleSheet(red_style)
                    self.profile_forgot_confirmpwd_tick.setPixmap(QPixmap())
                return

            if self.profile_forgot_newpwd.text() != '' and len(self.profile_forgot_newpwd.text()) >= 8:
                self.profile_forgot_newpwd.setStyleSheet(style)
                self.profile_forgot_newpwd_tick.setPixmap(self.tick_pixmap)
                self.profile_login_label(pwd=True, confirm=True)
            else:
                self.profile_forgot_newpwd.setStyleSheet(red_style)
                self.profile_forgot_newpwd_tick.setPixmap(QPixmap())
                self.profile_login_label(pwd=True, confirm=True)
            return
        
        #Username execution
        if confirm:
            if self.profile_forgot_confirmuser.text() != '':
                #Validates characters
                for letter in self.profile_forgot_confirmuser.text():
                    if ord(letter) in range(65, 91) or ord(letter) in range(97, 123) or ord(letter) in range(48, 57) or ord(letter) == 64 or ord(letter) == 95:
                        continue
                    text = self.profile_forgot_confirmuser.text()
                    text = text.replace(letter, '')
                    self.profile_forgot_confirmuser.setText(text)

                #Confirms the username
                if self.profile_forgot_confirmuser.text() == self.profile_forgot_newuser.text():
                    if self.profile_forgot_newuser_tick.pixmap().toImage() == self.tick_pixmap.toImage():
                        self.profile_forgot_confirmuser.setStyleSheet(style)
                        self.profile_forgot_confirmuser_tick.setPixmap(self.tick_pixmap)
                    return
                self.profile_forgot_confirmuser.setStyleSheet(red_style)
                self.profile_forgot_confirmuser_tick.setPixmap(QPixmap())
            else:
                self.profile_forgot_confirmuser.setStyleSheet(red_style)
                self.profile_forgot_confirmuser_tick.setPixmap(QPixmap())
            return

        if self.profile_forgot_newuser.text() != '':
            #Validates characters
            for letter in self.profile_forgot_newuser.text():
                if ord(letter) in range(65, 91) or ord(letter) in range(97, 123) or ord(letter) in range(48, 57) or ord(letter) == 64 or ord(letter) == 95:
                    continue
                text = self.profile_forgot_newuser.text()
                text = text.replace(letter, '')
                self.profile_forgot_newuser.setText(text)

            #Checks for availibility in the database
            info = query.sql_query(get_query='select Username from accounts where Username = %s', get_query_values=(self.profile_forgot_newuser.text(),))
            if info:
                self.profile_forgot_newuser.setStyleSheet(red_style)
                self.profile_forgot_newuser_tick.setPixmap(QPixmap())
                self.profile_login_label(confirm=True)
                return
            self.profile_forgot_newuser.setStyleSheet(style)
            self.profile_forgot_newuser_tick.setPixmap(self.tick_pixmap)
            self.profile_login_label(confirm=True)
        else:
            self.profile_forgot_newuser.setStyleSheet(red_style)
            self.profile_forgot_newuser_tick.setPixmap(QPixmap())
            self.profile_login_label(confirm=True)


    def change_profile_page(self, page):
        """
        Changes the pages in profile page.

        Parameters:
            page : The page to be selected to
        """

        #Returns the function if the button is spammed
        if self.profile_stack.currentWidget() == page:
            return

        btn = self.sender() #Gets the clicked button

        #Asks for confirmation
        if self.register:
            if not self.confirm("Do you want to leave?"):
                return

        if btn != self.profile_myquiz:
            style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"
            self.register = True #Asks the question

            if btn == self.profile_changeuser:
                #Resets change user page
                self.profile_user_fullname.setText('')
                self.profile_user_fullname.setStyleSheet(style)
                self.profile_forgot_userkey.setText('')
                self.profile_forgot_userkey.setStyleSheet(style)
                self.profile_forgot_usertick.setStyleSheet("border: none")
                self.profile_forgot_usertick.setPixmap(QPixmap())
                self.profile_forgot_newuser.setEnabled(False)
                self.profile_forgot_newuser.setText('')
                self.profile_forgot_newuser.setStyleSheet(style)
                self.profile_forgot_newuser_tick.setStyleSheet("border: none")
                self.profile_forgot_newuser_tick.setPixmap(QPixmap())
                self.profile_forgot_confirmuser.setEnabled(False)
                self.profile_forgot_confirmuser.setText('')
                self.profile_forgot_confirmuser.setStyleSheet(style)
                self.profile_forgot_confirmuser_tick.setStyleSheet("border: none")
                self.profile_forgot_confirmuser_tick.setPixmap(QPixmap())

            elif btn == self.profile_changepwd:
                #Resets change password page
                self.profile_pwd_fullname.setText('')
                self.profile_pwd_fullname.setStyleSheet(style)
                self.profile_forgot_pwdkey.setText('')
                self.profile_forgot_pwdkey.setStyleSheet(style)
                self.profile_forgot_pwdtick.setStyleSheet("border: none")
                self.profile_forgot_pwdtick.setPixmap(QPixmap())
                self.profile_forgot_newpwd.setEnabled(False)
                self.profile_forgot_newpwd.setText('')
                self.profile_forgot_newpwd.setStyleSheet(style)
                self.profile_forgot_newpwd_tick.setStyleSheet("border: none")
                self.profile_forgot_newpwd_tick.setPixmap(QPixmap())
                self.profile_forgot_confirmpwd.setEnabled(False)
                self.profile_forgot_confirmpwd.setText('')
                self.profile_forgot_confirmpwd.setStyleSheet(style)
                self.profile_forgot_confirmpwd_tick.setStyleSheet("border: none")
                self.profile_forgot_confirmpwd_tick.setPixmap(QPixmap())
            
            elif btn == self.profile_changekey:
                #Resets change key page
                self.profile_key_fullname.setEnabled(True)
                self.profile_key_pwd.setEnabled(True)
                self.profile_key_fullname.setText('')
                self.profile_key_fullname.setStyleSheet(style)
                self.profile_key_pwd.setText('')
                self.profile_key_pwd.setStyleSheet(style)
                self.profile_key_label.setText('')
                self.profile_key_label.setStyleSheet(style)
                self.profile_generate_key.setEnabled(True)
        
        else:
            #My Quizzes
            #Resets the buttons
            self.myquiz_open.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);")
            self.myquiz_delete.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);")
            self.myquiz_delete.setEnabled(False)
            self.myquiz_open.setEnabled(False)

            #Gets all the contents from the scroll area
            obj_list = self.myquiz_scroll_contents.findChildren(QPushButton)
            for obj in obj_list[::-1]:
                obj.deleteLater()

            #Gets all the quizzes from the database
            my_quizzes = query.sql_query(
                get_query='select UniqueKey, QuizTitle from quizzes where Username = %s',
                get_query_values=(self.account_access.text(),)
            )

            if my_quizzes:
                for unique_key, quiz_title in my_quizzes[::-1]:
                    #Creates pushButtons
                    layout = self.myquiz_scroll_contents.layout() #Gets the layout

                    button = QPushButton(quiz_title, self, objectName=unique_key) #Creates pushButton

                    #Adds Cursor Style
                    button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

                    #Add StyleSheet
                    button.setStyleSheet("QPushButton::hover{\nbackground-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\n}\n\nQPushButton {\nbackground-color: rgb(255, 255, 255);\nborder-top-left-radius : 10px;\nborder-top-right-radius : 10px; \nborder-bottom-left-radius : 10px; \nborder-bottom-right-radius : 10px;\n}")
                    button.setFont(QFont('MS Shell Dlg 2', 9)) #Sets the font
                    button.setMinimumSize(433, 25) #Determines the min. size
                    button.setCheckable(True) #For knowing which button is selected
                    button.setToolTip(f'By {self.account_access.text()}')

                    self.myquiz_buttongroup.addButton(button) #Adds the push button to button group

                    layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                    layout.addWidget(button) #Adds the button
            else:
                #Creates pushButton for telling none created
                lay = self.myquiz_scroll_contents.layout()
                none_pb = QPushButton("You have created no quizzes.", self)
                none_pb.setStyleSheet("color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;")
                none_pb.setFont(QFont('MS Shell Dlg 2', 15))
                none_pb.setMinimumSize(433, 25)
                none_pb.setEnabled(False)
                self.myquiz_buttongroup.addButton(none_pb)
                lay.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                lay.addWidget(none_pb)
            self.register = False #No question when leaving my quiz

        self.profile_stack.setCurrentWidget(page) #Sets the page


    def account_log_delete(self, delete: bool = False):
        """
        The function to logout or delete account.

        Parameters:
            delete [bool] [Default: False] : To delete the account
        """

        #Delete
        if delete:
            inf = self.confirm("Do you want to permanently delete your account?\n\nYou won't be able to recover your account.")
            if inf:
                query.sql_query(insert_query="delete from accounts where Username = %s", insert_query_values=(self.account_access.text(),))
                QMessageBox.information(self, 'SUCCESS', 'Account deleted permanently!')
                self.register = False
                self.frame_page(self.home_btn, self.home_pg, 'home')
            return
        
        #Logout
        info = self.confirm('Do you want to logout?')
        if info:
            query.edit_config('LOGIN', 'accountlogin', 'False')
            QMessageBox.information(self, 'SUCCESS', 'Logged out successfully!')
            self.register = False
            self.frame_page(self.home_btn, self.home_pg, 'home')


    def profile(self):
        """Adds texts to the profile elements"""

        if self.stack.currentWidget() == self.account_pg:
            return
        
        if self.register:
            if not self.confirm('Do you want to leave?'):
                return
            
        self.register = False
        
        image_name = {
            self.help_btn: 'help.jpg',
            self.home_btn: 'home.jpg',
            self.settings_btn: 'settings.jpg',
            self.quiz_btn: 'quiz.jpg'
        } #Buttons with their image name to be set

        #Iterates over the items and sets the button to unselected state
        resources_location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", image_name[self.selected])
        self.selected.setIcon(QIcon(resources_location))
        
        #Resets
        self.profile_stack.setCurrentWidget(self.profile_none_pg)
        self.profile_user.setText(self.account_access.text())

        self.stack.setCurrentWidget(self.account_pg) #Changes the page


    def forgot_confirm(self, pwd: bool = False):
        """
        Confirms the change of username/password.

        Parameters:
            pwd [bool] [Default: False] : Forgot password execution
        """

        #Forgot password
        if pwd:
            if self.forgot_pwdtick.pixmap().toImage() == self.forgot_newpwd_tick.pixmap().toImage() == self.tick_pixmap.toImage():
                #Change password
                inf = self.confirm('Do you want to change the password?')
                if inf:
                    query.sql_query(
                        insert_query='update accounts set Password = %s where Fullname = %s and Auth = %s',
                        insert_query_values=(query.salt_hash(self.forgot_confirmpwd.text()), self.pwd_fullname.text(), self.forgot_pwdkey.text())
                    )
                    self.register = False
                    QMessageBox.information(self, 'Success', 'Password changed successfully! You may now login!')
                    self.reset_login()
                return
            self.incomplete()
            return
        
        #Forgot username
        if self.forgot_usertick.pixmap().toImage() == self.forgot_newuser_tick.pixmap().toImage() == self.tick_pixmap.toImage():
            #Change username
            info = self.confirm('Do you want to change the username?')
            if info:
                query.sql_query(
                    insert_query='update accounts set Username = %s where Fullname = %s and Auth = %s',
                    insert_query_values=(self.forgot_confirmuser.text(), self.user_fullname.text(), self.forgot_userkey.text())
                )
                self.register = False
                QMessageBox.information(self, 'Success', 'Username changed successfully! You may now login!')
                self.reset_login()
            return
        self.incomplete()


    def forgot_key_check(self, pwd: bool = False):
        """
        Checks the user/pass key, and takes care of execution.

        Parameters:
            pwd [bool] [Default: False] : The forgot password
        """

        style = "background-color: rgb(255, 255, 255);"
        red_style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;"

        if pwd:
            val = query.sql_query(
                get_query='select Username from accounts where Fullname = %s and Auth = %s',
                get_query_values=(self.pwd_fullname.text(), self.forgot_pwdkey.text())
            )

            if val:
                self.forgot_newpwd.setEnabled(True)
                self.forgot_confirmpwd.setEnabled(True)
                self.forgot_pwdkey.setStyleSheet(style)
                self.forgot_pwdtick.setPixmap(self.tick_pixmap)
                return
            self.forgot_pwdkey.setStyleSheet(red_style)
            self.forgot_pwdtick.setPixmap(QPixmap())
            self.forgot_newpwd.setEnabled(False)
            self.forgot_newpwd.setText('')
            self.forgot_newpwd.setStyleSheet(red_style)
            self.forgot_newpwd_tick.setPixmap(QPixmap())
            self.forgot_confirmpwd.setEnabled(False)
            self.forgot_confirmpwd.setText('')
            self.forgot_confirmpwd.setStyleSheet(red_style)
            self.forgot_confirmpwd_tick.setPixmap(QPixmap())
            return

        value = query.sql_query(
            get_query='select Username from accounts where Fullname = %s and Auth = %s',
            get_query_values=(self.user_fullname.text(), self.forgot_userkey.text())
        )

        if value:
            self.forgot_newuser.setEnabled(True)
            self.forgot_confirmuser.setEnabled(True)
            self.forgot_userkey.setStyleSheet(style)
            self.forgot_usertick.setPixmap(self.tick_pixmap)
            return
        self.forgot_userkey.setStyleSheet(red_style)
        self.forgot_usertick.setPixmap(QPixmap())
        self.forgot_newuser.setEnabled(False)
        self.forgot_newuser.setText('')
        self.forgot_newuser.setStyleSheet(red_style)
        self.forgot_newuser_tick.setPixmap(QPixmap())
        self.forgot_confirmuser.setEnabled(False)
        self.forgot_confirmuser.setText('')
        self.forgot_confirmuser.setStyleSheet(red_style)
        self.forgot_confirmuser_tick.setPixmap(QPixmap())


    def forgot_login_label(self, pwd: bool = False, confirm: bool = False):
        """
        Takes care about the execution of forgot username/password.

        Parameters:
            pwd [bool] [Default: False] : To execute forgot password
            confirm [bool] [Default: False] : To execute the confirm labels
        """

        style = "background-color: rgb(255, 255, 255);"
        red_style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;"

        #Password execution
        if pwd:
            if confirm:
                if self.forgot_confirmpwd.text() != '':
                    if len(self.forgot_newpwd.text()) >= 8:
                        if self.forgot_newpwd.text() == self.forgot_confirmpwd.text():
                            self.forgot_confirmpwd.setStyleSheet(style)
                            self.forgot_confirmpwd_tick.setPixmap(self.tick_pixmap)
                            return
                        self.forgot_confirmpwd.setStyleSheet(red_style)
                        self.forgot_confirmpwd_tick.setPixmap(QPixmap())
                        return
                    self.forgot_confirmpwd.setStyleSheet(red_style)
                    self.forgot_confirmpwd_tick.setPixmap(QPixmap())
                else:
                    self.forgot_confirmpwd.setStyleSheet(red_style)
                    self.forgot_confirmpwd_tick.setPixmap(QPixmap())
                return

            if self.forgot_newpwd.text() != '' and len(self.forgot_newpwd.text()) >= 8:
                self.forgot_newpwd.setStyleSheet(style)
                self.forgot_newpwd_tick.setPixmap(self.tick_pixmap)
                self.forgot_login_label(pwd=True, confirm=True)
            else:
                self.forgot_newpwd.setStyleSheet(red_style)
                self.forgot_newpwd_tick.setPixmap(QPixmap())
                self.forgot_login_label(pwd=True, confirm=True)
            return
        
        #Username execution
        if confirm:
            if self.forgot_confirmuser.text() != '':
                #Validates characters
                for letter in self.forgot_confirmuser.text():
                    if ord(letter) in range(65, 91) or ord(letter) in range(97, 123) or ord(letter) in range(48, 57) or ord(letter) == 64 or ord(letter) == 95:
                        continue
                    text = self.forgot_confirmuser.text()
                    text = text.replace(letter, '')
                    self.forgot_confirmuser.setText(text)

                #Confirms the username
                if self.forgot_confirmuser.text() == self.forgot_newuser.text():
                    if self.forgot_newuser_tick.pixmap().toImage() == self.tick_pixmap.toImage():
                        self.forgot_confirmuser.setStyleSheet(style)
                        self.forgot_confirmuser_tick.setPixmap(self.tick_pixmap)
                    return
                self.forgot_confirmuser.setStyleSheet(red_style)
                self.forgot_confirmuser_tick.setPixmap(QPixmap())
            else:
                self.forgot_confirmuser.setStyleSheet(red_style)
                self.forgot_confirmuser_tick.setPixmap(QPixmap())
            return

        if self.forgot_newuser.text() != '':
            #Validates characters
            for letter in self.forgot_newuser.text():
                if ord(letter) in range(65, 91) or ord(letter) in range(97, 123) or ord(letter) in range(48, 57) or ord(letter) == 64 or ord(letter) == 95:
                    continue
                text = self.forgot_newuser.text()
                text = text.replace(letter, '')
                self.forgot_newuser.setText(text)

            #Checks for availibility in the database
            info = query.sql_query(get_query='select Username from accounts where Username = %s', get_query_values=(self.forgot_newuser.text(),))
            if info:
                self.forgot_newuser.setStyleSheet(red_style)
                self.forgot_newuser_tick.setPixmap(QPixmap())
                self.forgot_login_label(confirm=True)
                return
            self.forgot_newuser.setStyleSheet(style)
            self.forgot_newuser_tick.setPixmap(self.tick_pixmap)
            self.forgot_login_label(confirm=True)
        else:
            self.forgot_newuser.setStyleSheet(red_style)
            self.forgot_newuser_tick.setPixmap(QPixmap())
            self.forgot_login_label(confirm=True)


    def login_check(self):
        """Logs the user with the credentials provided"""

        if self.username.text() != '' and len(self.password.text()) >= 8:
            #Checks for credentials
            autologin_list = query.sql_query(
                get_query='select AutoLogin from accounts where Username = %s and Password = %s',
                get_query_values=(self.username.text(), query.salt_hash(self.password.text()))
            )
            if autologin_list:
                autologin = autologin_list[0][0]
                query.edit_config('LOGIN', 'accountlogin', autologin)
                self.logged = True
                QMessageBox.information(self, 'Success', 'Successfully logged in!')
                self.frame_page(self.home_btn, self.home_pg, 'home')
                return
            #Warns if not found
            self.password.setText('')
            QMessageBox.warning(self, 'Error', 'Username or Password is incorrect!')
            return
        self.incomplete()


    def change_style(self, style: list, widget):
        """
        Changes the style of the widget under certain conditions.

        Parameters:
            style [list] : The style sheet to be changed to (0 - String, 1 - No String)
            widget : The style sheet of the widget to be changed
        """

        if widget.text() != '':
            if widget == self.username:
                #Validates characters
                for letter in self.username.text():
                    if ord(letter) in range(65, 91) or ord(letter) in range(97, 123) or ord(letter) in range(48, 57) or ord(letter) == 64 or ord(letter) == 95:
                        continue
                    text = self.username.text()
                    text = text.replace(letter, '')
                    self.username.setText(text)
   
            if widget == self.password or widget == self.profile_key_pwd:
                if len(widget.text()) >= 8:
                    widget.setStyleSheet(style[0])
                return

            widget.setStyleSheet(style[0])
            return
        widget.setStyleSheet(style[1])


    def show_result(self, forced: bool=False):
        """
        Shows and sets the result.

        Parameters:
            forced [bool] [Default: False] : Force submit
        """

        if not forced:
            #Asks for confirmation
            value = QMessageBox.information(
                self,
                'SUBMIT',
                'Do you want to submit the quiz?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
        else:
            value = True

        if value == QMessageBox.StandardButton.Yes:
            tip = ''
            #Increases the popularity for Community
            if self.quiz_no.objectName() != "":
                query.sql_query(
                    insert_query='update quizzes set Popularity = Popularity + 5 where UniqueKey = %s',
                    insert_query_values=(self.quiz_no.objectName(),)
                )
                user_name = query.sql_query(
                    get_query='select Username from quizzes where UniqueKey = %s',
                    get_query_values=(self.quiz_no.objectName(),)
                )
                tip = f'By {user_name[0][0]}'
            else:
                self.increase_popularity_subjects(True)

            #Sets and gets the data
            question_data = self.quiz_dict
            answer_data = {btn.text(): btn.objectName() for btn in self.quiz_question_buttongroup.buttons()}
            self.timer = False
            self.myquiz_selected = False
            self.register = True
            self.quiz_time.setText('10:00')

            #Values
            correct = incorrect = unattempted = 0

            #Styles
            correct_ans_style = "background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid green;"
            incorrect_ans_style = "background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid red;"

            #Resets the labels
            self.result_title.setText(self.quiz_title.text())
            self.result_title.setStyleSheet(self.quiz_title.styleSheet())
            self.result_title.setToolTip(tip)
            self.result_title.setFont(self.quiz_title.font())
            self.result_logo.setPixmap(self.quiz_logo.pixmap())

            #Deletes the previous frames
            for frame in self.result_scroll_contents.findChildren(QFrame):
                frame.deleteLater()
            
            #Creates frame
            for num in question_data:
                frame = QFrame(self) #Frame
                lay = QGridLayout() #Grid Layout

                #Sets the frame
                frame.setObjectName(num)
                frame.setFrameShape(QFrame.Shape.StyledPanel)
                frame.setFrameShadow(QFrame.Shadow.Raised)
                frame.setStyleSheet("border-top-left-radius : 0px;\nborder-top-right-radius : 0px;\nborder: 2px solid black;")
                frame.setMinimumSize(561, 171)
                frame.setMaximumSize(561, 171)

                #Sets the question number label
                question_label_no = QLabel()
                question_label_no.setObjectName(num)
                question_label_no.setText(num)
                question_label_no.setMinimumSize(31, 31)
                question_label_no.setMaximumSize(31, 31)
                question_label_no.setFont(QFont('MS Shell Dlg 2', 12))
                question_label_no.setStyleSheet("border: 1px solid black;\nbackground-color: rgb(255, 255, 255);\nborder-style: outset;\nborder-radius: 15px;\npadding: 4px;")
                question_label_no.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                #Sets the question line
                question_line = QLineEdit()
                question_line.setText(question_data[num]["Question"])
                question_line.setMinimumHeight(30)
                question_line.setFont(QFont('MS Shell Dlg 2', 12))
                question_line.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid black;")
                question_line.setReadOnly(True)
                question_line.setCursorPosition(0)
                question_line.setCursor(QCursor(QtCore.Qt.CursorShape.IBeamCursor))

                #Sets the answer label
                ans_label = QLabel()
                ans_label.setText("YOUR ANSWER:")
                ans_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
                ans_label.setStyleSheet("background-color: rgb(255, 255, 255);")
                ans_label.setMinimumSize(120, 30)
                ans_label.setFont(QFont('MS Shell Dlg 2', 10))

                #Sets the answer line
                ans_line = QLineEdit()
                ans_line.setText(answer_data[num])
                ans_line.setMinimumHeight(30)
                ans_line.setFont(QFont('MS Shell Dlg 2', 11))
                ans_line.setStyleSheet("background-color: rgb(0, 0, 0);\ncolor: rgb(255, 255, 255);\nborder: 1px solid white;")
                ans_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
                ans_line.setReadOnly(True)
                ans_line.setCursorPosition(0)
                ans_line.setCursor(QCursor(QtCore.Qt.CursorShape.IBeamCursor))

                #Sets the correcr answer label
                correct_ans_label = QLabel()
                correct_ans_label.setText("CORRECT ANSWER:")
                correct_ans_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
                correct_ans_label.setStyleSheet("background-color: rgb(255, 255, 255);")
                correct_ans_label.setMinimumSize(120, 30)
                correct_ans_label.setFont(QFont('MS Shell Dlg 2', 10))

                #Sets the correct answer line
                correct_ans_line = QLineEdit()
                correct_ans_line.setText(question_data[num]["Answer"])
                correct_ans_line.setMinimumHeight(30)
                correct_ans_line.setFont(QFont('MS Shell Dlg 2', 11))
                correct_ans_line.setStyleSheet(correct_ans_style)
                correct_ans_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
                correct_ans_line.setReadOnly(True)
                correct_ans_line.setCursorPosition(0)
                correct_ans_line.setCursor(QCursor(QtCore.Qt.CursorShape.IBeamCursor))

                #Assigns correct, incorrect and attempted values
                if ans_line.text() != '':
                    if ans_line.text().strip() == correct_ans_line.text().strip():
                        ans_line.setStyleSheet(correct_ans_style)
                        correct += 1
                    else:
                        ans_line.setStyleSheet(incorrect_ans_style)
                        incorrect += 1
                else:
                    unattempted += 1

                #Layout Settings
                lay.setAlignment(lay, QtCore.Qt.AlignmentFlag.AlignTop)

                #Adds the widgets to the layout
                lay.addWidget(question_label_no, 0, 0)
                lay.addWidget(question_line, 0, 1)
                lay.addWidget(ans_label, 1, 0)
                lay.addWidget(ans_line, 1, 1)
                lay.addWidget(correct_ans_label, 2, 0)
                lay.addWidget(correct_ans_line, 2, 1)

                frame.setLayout(lay) #Adds layout to the frame
                self.result_scroll_contents.layout().addWidget(frame) #Adds the frame to the scroll area
            
            #Sets the values
            self.result_correct.setText(str(correct))
            self.result_incorrect.setText(str(incorrect))
            self.result_unattempted.setText(str(unattempted))
            self.result_total.setText(str(len(question_data)))

            #Sets the page
            self.stack.setCurrentWidget(self.result_pg)


    def clear_options(self):
        """Clears the options for the quiz"""

        for pb in self.quiz_question_buttongroup.buttons():
            if pb.text() == self.quiz_no.text():
                pb.setObjectName('')
                pb.setStyleSheet("border: 1px solid red;\nborder-radius: none;\nbackground-color: rgb(0, 255, 0);\nbackground-color: rgb(255, 170, 0);\nbackground-color: rgb(255, 0, 0);")
                break
        
        labels = [self.quiz_option_label_a, self.quiz_option_label_b, self.quiz_option_label_c, self.quiz_option_label_d]
        for label in labels:
            label.setStyleSheet("background-color: rgb(0,0,0);\ncolor: rgb(255,255,255);\nborder: 2px solid white;\nborder-radius: none;")


    def quiz_option_clicked(self):
        """Sets/Changes the options for the quiz"""

        btn = self.sender() #Gets the button clicked

        btn_label = {
            self.quiz_option_btn_a: self.quiz_option_label_a,
            self.quiz_option_btn_b: self.quiz_option_label_b,
            self.quiz_option_btn_c: self.quiz_option_label_c,
            self.quiz_option_btn_d: self.quiz_option_label_d
        } #Button and labels relation

        #Prevents spam
        if btn_label[btn].styleSheet() == "background-color: rgb(255, 255, 255);\ncolor: rgb(0, 0, 0);\nborder: 2px solid white;\nborder-radius: none;":
            return

        p_btn = None

        for pb in self.quiz_question_buttongroup.buttons():
            if pb.text() == self.quiz_no.text():
                p_btn = pb
                pb.setObjectName(btn_label[btn].text())
                pb.setStyleSheet("border: 1px solid red;\nborder-radius: none;\nbackground-color: rgb(0, 255, 0);\nbackground-color: rgb(255, 170, 0);\nbackground-color: rgb(255, 0, 0);\nbackground-color: rgb(0, 170, 0);")
                break

        for label in btn_label.values():
            if label.text() == p_btn.objectName():
                label.setStyleSheet("background-color: rgb(255, 255, 255);\ncolor: rgb(0, 0, 0);\nborder: 2px solid white;\nborder-radius: none;")
                continue
            label.setStyleSheet("background-color: rgb(0,0,0);\ncolor: rgb(255,255,255);\nborder: 2px solid white;\nborder-radius: none;")


    def quiz_change_question(self, btn):
        """
        Changes the question and options on button click.

        Parameters:
            btn : The button clicked
        """

        #Prevents spam
        if self.quiz_no.text() == btn.text():
            return
        
        self.quiz_no.setText(btn.text()) #Changes question number
        self.quiz_question.setText(self.quiz_dict[self.quiz_no.text()]["Question"]) #Changes question
        option = (self.quiz_dict[self.quiz_no.text()]["Options"]).split(',') #Gets the options

        #Randomizes the options
        if btn.styleSheet() == "border: 1px solid red;\nborder-radius: none;\nbackground-color: rgb(0, 255, 0);\nbackground-color: rgb(255, 170, 0);":
            random.shuffle(option)
            self.quiz_dict[self.quiz_no.text()]["Options"] = ','.join(option)

        #Changes StyleSheet
        if btn.objectName() == '':
            btn.setStyleSheet("border: 1px solid red;\nborder-radius: none;\nbackground-color: rgb(0, 255, 0);\nbackground-color: rgb(255, 170, 0);\nbackground-color: rgb(255, 0, 0);")
        else:
            btn.setStyleSheet("border: 1px solid red;\nborder-radius: none;\nbackground-color: rgb(0, 255, 0);\nbackground-color: rgb(255, 170, 0);\nbackground-color: rgb(255, 0, 0);\nbackground-color: rgb(0, 170, 0);")

        #Sets text in options
        labels = [self.quiz_option_label_a, self.quiz_option_label_b, self.quiz_option_label_c, self.quiz_option_label_d]
        for num, label in enumerate(labels):
            label.setText(option[num])
            if btn.objectName() == label.text():
                label.setStyleSheet("background-color: rgb(255, 255, 255);\ncolor: rgb(0, 0, 0);\nborder: 2px solid white;\nborder-radius: none;")
                continue
            label.setStyleSheet("background-color: rgb(0,0,0);\ncolor: rgb(255,255,255);\nborder: 2px solid white;\nborder-radius: none;")


    def quit_or_submit(self):
        """Shows MessageBox to quit or submit the quiz"""

        value = QMessageBox.information(
            self, 'TIMEOUT',
            'The timer has expired! You can longer attend the quiz! You can either Submit or Quit.\n\nClick "OK" to Submit or "Cancel" to Quit.',
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Ok
        )

        if value == QMessageBox.StandardButton.Ok:
            #Submit
            self.show_result(forced=True)
        else:
            #Quit
            self.myquiz_selected = False
            self.frame_page(self.home_btn, self.home_pg, 'home')
            self.quiz_time.setText('10:00')
            self.timer = False


    def change_timer(self):
        """Changes the time in the timer of quiz"""

        if self.timer:
            if self.count <= 0:
                self.timer = False
                self.quit_or_submit()
            if self.count > 0:
                self.count -= 1 #Decreases the count every one second
        else:
            self.account_stack.setEnabled(True)
            self.quiz_dict = None
            
        minutes = int(self.count / 60) #Convert second to minutes
        seconds = self.count - (60*minutes) #Gets the remaining seconds
        self.quiz_time.setText(str(f'{minutes}:{seconds:02d}')) #Shows the time


    def quiz_setup(self, data: dict, unique_key: str = ''):
        """
        Resets and sets the quiz.

        Parameters:
            data [dict] : All the quiz data
            unique_key [str] : The unique key of the quiz
        """

        self.account_stack.setEnabled(False) #Disables the frames
        self.count = 600

        #Resets the labels        
        for num in data.keys():
            new_btn = QPushButton(num, self)
            new_btn.setMinimumSize(35, 15)
            new_btn.setMaximumSize(35, 35)
            new_btn.setFont(QFont('MS Shell Dlg 2', 9))
            self.quiz_question_buttongroup.addButton(new_btn)
            if num == '1':
                new_btn.setStyleSheet("border: 1px solid red;\nborder-radius: none;\nbackground-color: rgb(0, 255, 0);\nbackground-color: rgb(255, 170, 0);\nbackground-color: rgb(255, 0, 0);")
            else:
                new_btn.setStyleSheet("border: 1px solid red;\nborder-radius: none;\nbackground-color: rgb(0, 255, 0);\nbackground-color: rgb(255, 170, 0);")
            new_btn.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.quiz_scroll_contents.layout().addWidget(new_btn)
        
        #Sets the initial questions and options
        self.quiz_no.setText("1")

        if unique_key != '':
            self.quiz_no.setObjectName(unique_key)
         
        self.quiz_question.setText(data["1"]["Question"])
        option = (data["1"]["Options"]).split(',') #Separates the options
        random.shuffle(option) #Shuffles the options

        #Adds text to option labels
        labels = [self.quiz_option_label_a, self.quiz_option_label_b, self.quiz_option_label_c, self.quiz_option_label_d]
        for num, label in enumerate(labels):
            label.setStyleSheet("background-color: rgb(0,0,0);\ncolor: rgb(255,255,255);\nborder: 2px solid white;\nborder-radius: none;")
            label.setText(option[num])

        self.myquiz_selected = True #Ensures the quiz is active
        self.stack.setCurrentWidget(self.attempt_quiz_pg) #Switches the page

        #Informs all the rules
        QMessageBox.information(self, 'RULES', "Rules:\n\n1. You can quit the quiz anytime, and any of your actions will not get registered.\n\n2. The timer will start as soon as you click 'OK'.\n\n3. The quiz will ask you to either submit or quit, if the timer runs out.\n\n4. You can click 'Clear' button to clear your selected option.\n\n5. Red indicates unattempted, Yellow indicated Unseen, Green indicates Attempted.\n\n\nYou have 10 mins. to complete the quiz. Good Luck!")

        #Starts the timer
        self.timer = True
        self.quiz_dict = data
        self.quiz_dict["1"]["Options"] = ','.join(option)


    def start_quiz(self, button, image=None, topic: str = '', difficulty: str = ''):
        """
        The function to start the quiz.

        Parameters:
            button : The button clicked
            image [Default: None] : The image related to button
            topic [str] [Default: ''] : The topic (GK, Science, Maths, Computers)['' for community]
            difficuly [str] : The difficulty selected
        """

        #Confirms the initiation for quiz
        value = QMessageBox.question(self, "Start Quiz", "Are you sure you want to start the quiz?", QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Ok)
        
        if value == QMessageBox.StandardButton.Ok:
            self.quiz_question.setObjectName('')
            self.quiz_no.setObjectName('')
            self.quiz_logo.setObjectName('')

            for pbtn in self.quiz_scroll_contents.findChildren(QPushButton)[::-1]:
                pbtn.deleteLater()

            image_name = {
                self.help_btn: 'help.jpg',
                self.home_btn: 'home.jpg',
                self.settings_btn: 'settings.jpg',
                self.quiz_btn: 'quiz.jpg'
            } #Buttons with their image name to be set

            # Iterates over the items and sets the button to unselected state
            resources_location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", image_name[self.selected])
            self.selected.setIcon(QIcon(resources_location))

            if not image:
                image = self.pix_map

            if topic == '':
                #Community Quiz
                self.quiz_title.setText(button.text())
                self.quiz_title.setStyleSheet("background-color: rgba(64, 64, 64, 70);\nbackground-color: rgb(0, 0, 0);\ncolor: rgb(221, 221, 221);\ncolor: rgb(255, 255, 255);\nborder: 2px solid white;\nborder-style: outset;\nborder-radius: 10px;\npadding: 4px;")
                self.quiz_title.setFont(QFont('MS Shell Dlg 2', 13))
                self.quiz_logo.setPixmap(image)

                question_data = query.sql_query(
                    get_query='select Data from quizzes where UniqueKey = %s',
                    get_query_values=(button.objectName(),)
                )

                query.sql_query(
                    insert_query='update quizzes set Popularity = Popularity + 1 where UniqueKey = %s',
                    insert_query_values=(button.objectName(),)
                )

                question_data = json.loads(question_data[0][0])

                _list = (random.sample(list(question_data.items()), k=len(question_data.keys())))
                random.shuffle(_list)

                self.quiz_setup({str(num+1): value[1] for num, value in enumerate(_list)}, button.objectName()) #Stars the quiz
                return

            #Subject Quiz
            #Replaces the text and image
            self.quiz_title.setText(button.text())
            self.quiz_title.setStyleSheet(button.styleSheet())
            self.quiz_title.setFont(QFont('MS Shell Dlg 2', 20))
            self.quiz_logo.setPixmap(image.pixmap())
            self.quiz_logo.setStyleSheet(image.styleSheet())

            if topic == 'GK':
                difficulty = self.gk_difficuly.currentText()
                number = self.gk_question.currentText()
            elif topic == "Science":
                difficulty = self.science_difficuly.currentText()
                number = self.science_question.currentText()
            elif topic == 'Maths':
                difficulty = self.maths_difficuly.currentText()
                number = self.maths_question.currentText()
            elif topic == "Computers":
                difficulty = self.computers_difficuly.currentText()
                number = self.computers_question.currentText()

            self.quiz_question.setObjectName(topic)
            self.quiz_logo.setObjectName(difficulty)
            self.increase_popularity_subjects()

            easy = query.sql_query(
                        get_query='select Data from quizzes where QuizTitle = %s and Difficulty = %s',
                        get_query_values=(topic, 'Easy')
                    )
            medium = query.sql_query(
                        get_query='select Data from quizzes where QuizTitle = %s and Difficulty = %s',
                        get_query_values=(topic, 'Medium')
                    )
            hard = query.sql_query(
                        get_query='select Data from quizzes where QuizTitle = %s and Difficulty = %s',
                        get_query_values=(topic, 'Hard')
                    )
                
            easy_dict = json.loads(easy[0][0])
            medium_dict = json.loads(medium[0][0])
            hard_dict = json.loads(hard[0][0])

            self.quiz_setup(self.difficulty_questions_algorithm([easy_dict, medium_dict, hard_dict], difficulty, int(number))) #Stars the quiz


    def increase_popularity_subjects(self, result: bool = False):
        """
        The function to increase non-community quiz popularity.

        Parameters:
            result [bool] [Default: False] : To increase popularity on result
        """

        #Variables
        title, difficulty = self.quiz_question.objectName(), self.quiz_logo.objectName()

        #Easy, Medium or Hard
        if difficulty != 'Mixed':
            #Result
            if result:
                query.sql_query(
                    insert_query='update quizzes set Popularity = Popularity + 5 where QuizTitle = %s and UniqueKey is %s and Difficulty = %s',
                    insert_query_values=(title, None, difficulty)
                )

                return
            
            #Visiting
            query.sql_query(
                insert_query='update quizzes set Popularity = Popularity + 1 where QuizTitle = %s and UniqueKey is %s and Difficulty = %s',
                insert_query_values=(title, None, difficulty)
            )

            return

        #Mixed
        difficulty = ['Easy', 'Medium', 'Hard']

        #Result
        if result:
            for diff in difficulty:
                query.sql_query(
                    insert_query='update quizzes set Popularity = Popularity + 5 where QuizTitle = %s and UniqueKey is %s and Difficulty = %s',
                    insert_query_values=(title, None, diff)
                )

            return

        #Visiting
        for diff in difficulty:
            query.sql_query(
                insert_query='update quizzes set Popularity = Popularity + 1 where QuizTitle = %s and UniqueKey is %s and Difficulty = %s',
                insert_query_values=(title, None, diff)
            )


    def difficulty_questions_algorithm(self, quiz_data: list, diff: str, q_no: int):
        """
        Uses certain algorithm to select questions with respect to difficulty.

        Parameters:
            quiz_data [dict] : The quiz data retrieved in the form of list
            diff [str] : Difficulty (Easy, Medium, Hard, Mixed)
            q_no [int] : The number of questions
        
        Returns:
            questions [dict] : The questions segregated with the algorithm
        """

        easy, medium, hard = quiz_data #Assigns easy, medium and hard from the list
        e = m = h = _list = None

        if diff == 'Easy':
            #Easy difficulty algorithm
            ran = random.choice([1, 2]) #Gets a random digit
            e = (q_no // 2) + ran #No. of easy questions
            m = q_no - e #No. of medium questions
            _list = (random.sample(list(easy.items()), k=e) + random.sample(list(medium.items()), k=m))
        
        elif diff == 'Medium':
            #Medium difficulty algorithm
            ran = random.choice([0, 1])
            e = (q_no // 2) - ran
            m = q_no // 2
            h = q_no - (e + m)
            _list = (random.sample(list(easy.items()), k=e) + random.sample(list(medium.items()), k=m) + random.sample(list(hard.items()), k=h))
        
        elif diff == 'Hard':
            #Hard difficulty algorithm
            ran = random.choice([0, 1])
            m = (q_no // 5) + ran
            h = q_no - m
            _list = (random.sample(list(medium.items()), k=m) + random.sample(list(hard.items()), k=h))
        
        else:
            #Mixed difficulty algorithm
            ran = random.choice([0, 1])
            e = (q_no // 2) - ran
            m = h = (q_no - e) // 2

            #Adjusts the questions
            if q_no - (e + m + h) != 0:
                add = q_no - (e + m + h)
                val = random.choice(['E', 'M', 'H'])
                if val == 'E':
                    e += add
                elif val == 'M':
                    m += add
                elif val == 'H':
                    h += add
            
            _list = (random.sample(list(easy.items()), k=e) + random.sample(list(medium.items()), k=m) + random.sample(list(hard.items()), k=h))

        random.shuffle(_list)
        return {str(num+1): value[1] for num, value in enumerate(_list)}


    def incomplete(self):
        """Generates a message box to inform incomplete information filled"""

        QMessageBox.warning(self, 'Incomplete information', 'Please fill out all the details before continuing.')
    

    def confirm(self, txt: str = 'Are you sure?'):
        """
        Generates a message box to confirm the actions.

        Parameters:
            txt [str] [Default: 'Are you sure?'] : The text to display in the question box
        
        Returns:
            success [bool] : True -> If the user presses Yes
        """

        value = QMessageBox.question(self, 'Confirmation', txt, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if value == QMessageBox.StandardButton.Yes:
            return True


    def generate_key(self, btn, label):
        """
        The function to generate forgot authorization key.

        Parameters:
            btn : The button generating the key
            label : The label showing the key
        """

        label.setText(query.random_key())
        label.setStyleSheet('background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; ')
        btn.setEnabled(False)


    def register_sucess(self):
        """Adds user information to the database"""

        if self.confirm_register_usertick.pixmap().toImage() == self.confirm_register_passtick.pixmap().toImage() == self.tick_pixmap.toImage() and len(self.register_key_label.text()) == 30:
            val = self.confirm('Have you confirmed all the details?\n\nMake sure to copy the key and store it somewhere safe.')
            if val:
                query.sql_query(
                    insert_query='insert into accounts values (%s, %s, %s, %s, %s, %s, %s)',
                    insert_query_values=(self.confirm_register_user.text(), query.salt_hash(self.confirm_register_pass.text()), self.full_name.text(),
                        self.gender.currentText(), self.birth.text(), query.random_key(), self.register_key_label.text())
                )
                QMessageBox.information(self, 'Success', 'Registration successful! You may now login!')
                self.register = False
                self.reset_login()
            return
        self.incomplete()


    def register_process(self, pwd: bool = False, confirm: bool = False):
        """
        The function to execute and process registration.

        Parameters:
            pwd [bool] [Default: False] : Check the process for passwords
            confirm [bool] [Default: False] : Check the process for confirm actions
        """

        red_style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; "
        style = "background-color: rgb(255, 255, 255);\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; "

        #Password execution and checks
        if pwd:
            #Password confirmation
            if confirm:
                if self.confirm_register_pass.text() != '':
                    if len(self.register_pass.text()) >= 8:
                        if self.register_pass.text() == self.confirm_register_pass.text():
                            self.confirm_register_pass.setStyleSheet(style)
                            self.confirm_register_passtick.setPixmap(self.tick_pixmap)
                            return
                        self.confirm_register_pass.setStyleSheet(red_style)
                        self.confirm_register_passtick.setPixmap(QPixmap())
                        return
                    self.confirm_register_pass.setStyleSheet(red_style)
                    self.confirm_register_passtick.setPixmap(QPixmap())
                else:
                    self.confirm_register_pass.setStyleSheet(red_style)
                    self.confirm_register_passtick.setPixmap(QPixmap())
                return

            if self.register_pass.text() != '' and len(self.register_pass.text()) >= 8:
                self.register_pass.setStyleSheet(style)
                self.register_passtick.setPixmap(self.tick_pixmap)
                self.register_process(pwd=True, confirm=True)
            else:
                self.register_pass.setStyleSheet(red_style)
                self.register_passtick.setPixmap(QPixmap())
                self.register_process(pwd=True, confirm=True)
            return

        #Username execution and checks
        #Username confirmation
        if confirm:
            if self.confirm_register_user.text() != '':
                #Validates characters
                for letter in self.confirm_register_user.text():
                    if ord(letter) in range(65, 91) or ord(letter) in range(97, 123) or ord(letter) in range(48, 57) or ord(letter) == 64 or ord(letter) == 95:
                        continue
                    text = self.confirm_register_user.text()
                    text = text.replace(letter, '')
                    self.confirm_register_user.setText(text)

                #Confirms the username
                if self.confirm_register_user.text() == self.register_user.text():
                    if self.register_usertick.pixmap().toImage() == self.tick_pixmap.toImage():
                        self.confirm_register_user.setStyleSheet(style)
                        self.confirm_register_usertick.setPixmap(self.tick_pixmap)
                    return
                self.confirm_register_user.setStyleSheet(red_style)
                self.confirm_register_usertick.setPixmap(QPixmap())
            else:
                self.confirm_register_user.setStyleSheet(red_style)
                self.confirm_register_usertick.setPixmap(QPixmap())
            return

        if self.register_user.text() != '':
            #Validates characters
            for letter in self.register_user.text():
                if ord(letter) in range(65, 91) or ord(letter) in range(97, 123) or ord(letter) in range(48, 57) or ord(letter) == 64 or ord(letter) == 95:
                    continue
                text = self.register_user.text()
                text = text.replace(letter, '')
                self.register_user.setText(text)

            #Checks for availibility in the database
            info = query.sql_query(get_query='select Username from accounts where Username = %s', get_query_values=(self.register_user.text(),))
            if info:
                self.register_user.setStyleSheet(red_style)
                self.register_usertick.setPixmap(QPixmap())
                self.register_process(confirm=True)
                return
            self.register_user.setStyleSheet(style)
            self.register_usertick.setPixmap(self.tick_pixmap)
            self.register_process(confirm=True)
        else:
            self.register_user.setStyleSheet(red_style)
            self.register_usertick.setPixmap(QPixmap())
            self.register_process(confirm=True)


    def registration_next_reset(self):
        """Resets the next page in registration page"""

        #Checks for all filled information
        if all([self.full_name.text() != '', self.birth.text() != '']) is False:
            self.incomplete()
            self.register = False
            return
        
        #Confirms
        if not self.confirm("Do you want to proceed?\n\nYou won't be able to return!"):
            self.register = False
            return
        
        self.register = True #Confirms the engagement in registration process

        #Stylesheet
        style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; "

        #Resets the second page
        self.register_user.setText('')
        self.register_user.setStyleSheet(style)
        self.register_usertick.setStyleSheet("border: none")
        self.register_usertick.setPixmap(QPixmap())
        self.confirm_register_user.setText('')
        self.confirm_register_user.setStyleSheet(style)
        self.confirm_register_usertick.setStyleSheet("border: none")
        self.confirm_register_usertick.setPixmap(QPixmap())
        self.register_pass.setText('')
        self.register_pass.setStyleSheet(style)
        self.register_passtick.setStyleSheet("border: none")
        self.register_passtick.setPixmap(QPixmap())
        self.confirm_register_pass.setText('')
        self.confirm_register_pass.setStyleSheet(style)
        self.confirm_register_passtick.setStyleSheet("border: none")
        self.confirm_register_passtick.setPixmap(QPixmap())
        self.register_key_label.setText('')
        self.register_key_label.setStyleSheet(style)
        self.register_generatekey.setEnabled(True)

        self.register_stack.setCurrentWidget(self.register_secondpg) #Changes to second page


    def forgot_login(self, pwd: bool = False):
        """
        This function switches to forgot password/username ppassword.

        Parameters:
            pwd [bool] [Default: False] : The bool value to determine to switch password page
        """

        self.register = True #Exit safe variable
        style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; \nborder-bottom-left-radius : 0px; \nborder-bottom-right-radius : 0px;"

        if pwd:
            self.pwd_fullname.setText('')
            self.pwd_fullname.setStyleSheet(style)
            self.forgot_pwdkey.setText('')
            self.forgot_pwdkey.setStyleSheet(style)
            self.forgot_pwdtick.setStyleSheet("border: none")
            self.forgot_pwdtick.setPixmap(QPixmap())
            self.forgot_newpwd.setEnabled(False)
            self.forgot_newpwd.setText('')
            self.forgot_newpwd.setStyleSheet(style)
            self.forgot_newpwd_tick.setStyleSheet("border: none")
            self.forgot_newpwd_tick.setPixmap(QPixmap())
            self.forgot_confirmpwd.setEnabled(False)
            self.forgot_confirmpwd.setText('')
            self.forgot_confirmpwd.setStyleSheet(style)
            self.forgot_confirmpwd_tick.setStyleSheet("border: none")
            self.forgot_confirmpwd_tick.setPixmap(QPixmap())

            self.login_stack.setCurrentWidget(self.login_pwdpage)
            return
        
        #Resets the widgets
        self.user_fullname.setText('')
        self.user_fullname.setStyleSheet(style)
        self.forgot_userkey.setText('')
        self.forgot_userkey.setStyleSheet(style)
        self.forgot_usertick.setStyleSheet("border: none")
        self.forgot_usertick.setPixmap(QPixmap())
        self.forgot_newuser.setEnabled(False)
        self.forgot_newuser.setText('')
        self.forgot_newuser.setStyleSheet(style)
        self.forgot_newuser_tick.setStyleSheet("border: none")
        self.forgot_newuser_tick.setPixmap(QPixmap())
        self.forgot_confirmuser.setEnabled(False)
        self.forgot_confirmuser.setText('')
        self.forgot_confirmuser.setStyleSheet(style)
        self.forgot_confirmuser_tick.setStyleSheet("border: none")
        self.forgot_confirmuser_tick.setPixmap(QPixmap())

        self.login_stack.setCurrentWidget(self.login_userpage) #Changes to the page


    def reset_login(self, register: bool = False):
        """
        Resets and switches to the login/register area

        Parameters:
            register [bool] [Default: False] : The register value determiner
        """

        if register:
            if self.stack.currentWidget() == self.register_pg:
                return

        #Asks for confirmation
        if self.register:
            if not self.confirm("Do you want to leave?"):
                return
            
        self.register = False

        if not register:
            self.login_stack.setCurrentWidget(self.login_mainpage) #Sets the active page to login main page
            
        self.register = False

        image_name = {
            self.help_btn: 'help.jpg',
            self.home_btn: 'home.jpg',
            self.settings_btn: 'settings.jpg',
            self.quiz_btn: 'quiz.jpg'
        } #Buttons with their image name to be set

        #Stylesheet
        style = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;"
        style_register = "background-color: rgb(255, 255, 255);\nborder: 1px solid red;\nborder-top-left-radius : 0px;\nborder-top-right-radius : 0px; "

        # Iterates over the items and sets the button to unselected state
        resources_location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", image_name[self.selected])
        self.selected.setIcon(QIcon(resources_location))

        if register:
            if self.stack.currentWidget() == self.register_pg:
                return

            self.register_stack.setCurrentWidget(self.register_firstpg) #Sets the active page to login main page

            today = str(datetime.date.today()).split('-') #Gets today's date
            self.calendar.setSelectedDate(QtCore.QDate(int(today[0]), int(today[1]), int(today[2]))) #Changes to today's date
            self.calendar.setMaximumDate(QtCore.QDate(int(today[0]), int(today[1]), int(today[2]))) #Changes the max date

            self.full_name.setText('')
            self.full_name.setStyleSheet(style_register)
            self.gender.setCurrentText('Male')
            self.birth.setText('')
            self.birth.setStyleSheet(style_register)

            self.stack.setCurrentWidget(self.register_pg) #Changes to register page
            return

        if self.stack.currentWidget() == self.login_pg:
            return

        #Resets login
        self.username.setText('')
        self.username.setStyleSheet(style)
        self.password.setText('')
        self.password.setStyleSheet(style)

        self.stack.setCurrentWidget(self.login_pg) #Changes to login page


    def send_feedback(self):
        if self.logged:
            window = Feedback_UI(self.account_access.text())
            window.show()
            return
        QMessageBox.warning(self, 'Login Required', 'You must be logged in to send a feedback.')


    def reset_app_data(self):
        """Resets the app to its factory settings"""

        ask_box = QMessageBox() #Creates message box instance
        #Asks the question for Yes|Cancel for resetting the app
        value = ask_box.question(self, "Reset App", "Do you want to reset all the app data?\n\n[This will delete all the new information ever created or stored. IT WILL RESET THE SQL DATABASE TOO.]", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Yes)
        
        if value == QMessageBox.StandardButton.Yes: #If the user confirms
            query.edit_config('LOGIN', 'first', 'True') #Resets the data
            query.sql_query(query=('drop database quizboxdata',))
            QMessageBox.information(self, "Reset App", "RESET SUCCESSFUL. YOU MAY RESTART THE APP!") #Sends the message
            self.close() #Closes the app


    def toggle(self, anim: bool, btn, label, y: int, secondary_label, config_key: str, secondary_text: list):
        """
        This function sets the toggle buttons.

        Parameters:
            anim [bool] : The bool value to perform animation or not
            btn : The widget instance of the button
            label : The widget instance of the label
            y : Y axis for the button animation
            secondary_label : The widget instance of more info label
            config_key [str] : The configuration key to change the value
            secondary_text [list] : First index contains text info for True, and second for False
        """

        if btn.isChecked(): #If True value is to be applied
            if anim:
                self.anim2 = QtCore.QPropertyAnimation(btn, b"geometry")
                self.anim2.setDuration(650) #.65 seconds
                self.anim2.setStartValue(QtCore.QRect(535, y, 21, 21))
                self.anim2.setEndValue(QtCore.QRect(565, y, 21, 21))
                self.anim2.start()

                if config_key != 'rememberaccount':
                    if config_key != 'start':
                        self.anim2.finished.connect(lambda: query.edit_config("SETTINGS", config_key, "True"))
                    else:
                        self.anim2.finished.connect(lambda: query.edit_config("SETTINGS", config_key, "False"))
                else:
                    self.anim2.finished.connect(lambda: query.edit_config("SETTINGS", config_key, "True", self.logged))
                self.anim2.finished.connect(lambda: btn.setStyleSheet("border-radius: 10px;min-height: 20px;min-width: 20px;background-color: rgb(0, 0, 255);"))

            #Adds more info
            secondary_label.setText(secondary_text[0])

            #Changes the background color
            if anim is False:
                btn.setGeometry(565, y, 21, 21)
                btn.setStyleSheet("border-radius: 10px;min-height: 20px;min-width: 20px;background-color: rgb(0, 0, 255);")
            label.setStyleSheet("border: 1px solid black;border-top-left-radius : 20px;border-top-right-radius : 20px; border-bottom-left-radius : 60px; border-bottom-right-radius : 60px; background-color: rgb(0, 85, 255);")
        else:
            if anim:
                self.anim3 = QtCore.QPropertyAnimation(btn, b"geometry")
                self.anim3.setDuration(650)
                self.anim3.setStartValue(QtCore.QRect(565, y, 21, 21))
                self.anim3.setEndValue(QtCore.QRect(535, y, 21, 21))
                self.anim3.start()

                if config_key != 'rememberaccount':
                    if config_key != 'start':
                        self.anim3.finished.connect(lambda: query.edit_config("SETTINGS", config_key, "False"))
                    else:
                        self.anim3.finished.connect(lambda: query.edit_config("SETTINGS", config_key, "True"))
                else:
                    self.anim3.finished.connect(lambda: query.edit_config("SETTINGS", config_key, "False", self.logged))
                self.anim3.finished.connect(lambda: btn.setStyleSheet("border-radius: 10px;min-height: 20px;min-width: 20px;background-color: rgb(255, 255, 255);"))

            secondary_label.setText(secondary_text[1])

            label.setStyleSheet("border: 1px solid black;border-top-left-radius : 20px;border-top-right-radius : 20px; border-bottom-left-radius : 60px; border-bottom-right-radius : 60px;")
            if anim is False:
                btn.setGeometry(535, y, 21, 21)
                btn.setStyleSheet("border-radius: 10px;min-height: 20px;min-width: 20px;background-color: rgb(255, 255, 255);")


    def hover_change_image(self, object, leave: bool = False):  
        if self.selected == object:
            return

        image_location = {
            'homeButton': ("home.jpg", "home_selected.jpg"),
            'helpButton': ("help.jpg", "help_selected.jpg"),
            'quizButton': ("quiz.jpg", "quiz_selected.jpg"),
            'settingsButton': ("settings.jpg", "settings_selected.jpg")
        } #Container of the name of button associated with their respective images

        if leave:
            object.setIcon(QIcon(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", image_location[object.objectName()][0])))
            return

        object.setIcon(QIcon(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", image_location[object.objectName()][1])))


    def frame_page(self, widget, page, load: str = ''):
        """
        Changes the Icon image and the frame of the widget.

        Parameters:
            widget : The instance of widget changing
            page : The page to be changed into
            load [str] [Default: ''] : Loads the frame (settings, help, home)
        """

        #Prevents page reload except for home
        if self.stack.currentWidget() == page and load != 'home':
            return
        
        #Asks for confirmation
        if self.register:
            if not self.confirm("Do you want to leave?"):
                return
        
        self.register = False

        if self.myquiz_selected:
            if not self.confirm("Do you want to leave the quiz?\n\nYou won't be able to continue!"):
                return
        
        self.myquiz_selected = False
        self.timer = False
        self.quiz_time.setText('10:00')

        #Loads the logged in assets
        if self.logged:
            value = query.salt_decode(query.read_config()['LOGIN']['accountlogin'])
            username = query.sql_query(
                get_query='select Username from accounts where AutoLogin = %s;',
                get_query_values=(value,)
            )
            if username:
                self.account_access.setText(username[0][0])
                self.account_stack.setCurrentWidget(self.log_pg)
                self.logger.debug('User LOGGED IN')
            else:
                self.logged = False
                self.account_access.setText('')
                self.account_stack.setCurrentWidget(self.notlog_pg)
                self.logger.debug('User LOGGED OUT')
        else:
            self.account_access.setText('')
            self.account_stack.setCurrentWidget(self.notlog_pg)
            self.logger.debug('User LOGGED OUT')

        image_location = {
            'homeButton': ("home.jpg", "home_selected.jpg"),
            'helpButton': ("help.jpg", "help_selected.jpg"),
            'quizButton': ("quiz.jpg", "quiz_selected.jpg"),
            'settingsButton': ("settings.jpg", "settings_selected.jpg")
        } #Container of the name of button associated with their respective images

        name = self.selected.objectName() #Gets the name of the button, aldready selected
        sel_widget = widget.objectName() #Gets the name of the button, to be clicked

        if name in image_location:
            non_select = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", image_location[name][0]) #Unselects the previous button
        
        if sel_widget in image_location:
            select = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Resources\\", image_location[sel_widget][1]) #Selects the new button

        self.selected.setIcon(QIcon(non_select)) #Updates the icon of previous button
        self.selected = widget #Assigns the new clicked button as selected
        self.selected.setIcon(QIcon(select)) #Updates the icon of the new button

        if load == 'settings':
            self.settings_stack.setCurrentWidget(self.home_settings_pg) #Resets the settings frame
            #Resets scroll of license page
            self.license_scroll.verticalScrollBar().setValue(0)
            self.license_scroll.horizontalScrollBar().setValue(0)
        elif load == 'help':
            self.help_scroll.verticalScrollBar().setValue(0)
            self.help_scroll.horizontalScrollBar().setValue(0)
        elif load == 'home':
            self.home_search.setText('')
            self.home_difficulty.setCurrentText('Any')
            self.home_question_number.setCurrentText('10')
            self.home_data_dict = dict()

            for btn in self.home_scroll_area.findChildren(QPushButton):
                btn.deleteLater()

            #Trending
            top_three = query.sql_query(
                get_query='select Username, UniqueKey, QuizTitle, Difficulty from quizzes where UniqueKey is not %s order by Popularity desc',
                get_query_values=(None,),
                rows=3
            )
            if top_three:
                trending = [self.home_trending_one, self.home_trending_two, self.home_trending_three]

                for num, t in enumerate(trending):
                    t.setText('')
                    t.setToolTip('')

                for num, value in enumerate(top_three):
                    user_name, key, title, difficulty = value

                    trending[num].setText(title)
                    trending[num].setObjectName(key)
                    trending[num].setToolTip(f'Trending #{num+1}. By {user_name}. Difficulty: {difficulty}')

                #For Community
                self.home_scroll_area.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

                all_quiz = query.sql_query(
                    get_query='select Username, UniqueKey, QuizTitle, Difficulty, Data from quizzes where UniqueKey is not %s',
                    get_query_values=(None,)
                )
                self.home_add_button(all_quiz)

        self.stack.setCurrentWidget(page) #Changes the frame


    def home_changed_question(self, number: str):
        """
        Changes the button according to number of questions.

        Parameters:
            number [str] : The number of questions changed to
        """

        new_list_data = list()

        for button in self.home_scroll_area.findChildren(QPushButton):
            button.deleteLater()

        for _, filter_list in self.filter_home_data_dict.items():
            num = len(filter_list[0][2])

            if str(num) == number or number == 'Any':
                new_list_data.append(filter_list[1])

        self.home_add_button(new_list_data, False)


    def home_changed_difficulty(self, diff: str):
        """
        Changes the button according to difficulty.

        Parameters:
            diff [str] : The difficulty changed to
        """

        new_list_data = list()

        for button in self.home_scroll_area.findChildren(QPushButton):
            button.deleteLater()

        for _, filter_list in self.filter_home_data_dict.items():
            difficulty = filter_list[0][1]

            if difficulty == diff or diff == 'Any':
                new_list_data.append(filter_list[1])

        self.home_add_button(new_list_data, False)


    def home_changed_search(self):
        """Changes the button according to search list"""

        new_list_data = list()
        self.home_difficulty.setCurrentText('Any')
        self.home_question_number.setCurrentText('10')

        for button in self.home_scroll_area.findChildren(QPushButton):
            button.deleteLater()

        for _, filter_list in self.home_data_dict.items():
            title = filter_list[0][0].lower()

            if self.home_search.text() in title:
                new_list_data.append(filter_list[1])
        self.filter_home_data_dict = dict()
        self.home_add_button(new_list_data, False, True)


    def home_add_button(self, data: list, alter_data: bool = True, home: bool = False):
        """
        Adds button and sets dictionary with all the data.

        Parameters:
            data [list] : The list returned by sql
            alter_data [bool] [Default: False] : Determines altering of data
            home [bool] [Default: False] : Gives search box in home priority in search
        """

        for button in self.home_scroll_area.findChildren(QPushButton):
            button.deleteLater()

        for user_name, key, title, difficulty, question_data in data:
            p_btn = QPushButton(title, self, objectName=key)
            p_btn.setMinimumHeight(25)
            p_btn.setToolTip(f'By {user_name}. Difficulty: {difficulty}')
            p_btn.setStyleSheet(" background-color: rgb(255, 255, 255);")
            p_btn.setFont(QFont('MS Shell Dlg 2', 9))
            p_btn.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

            self.home_quiz_buttongroup.addButton(p_btn)
            self.home_scroll_area.layout().addWidget(p_btn)
            if alter_data:
                self.filter_home_data_dict[p_btn] = self.home_data_dict[p_btn] = ((title, difficulty, json.loads(question_data)), (user_name, key, title, difficulty, question_data))
            elif home:
                self.filter_home_data_dict[p_btn] = ((title, difficulty, json.loads(question_data)), (user_name, key, title, difficulty, question_data))


    def trending_start_quiz(self):
        """Checks and starts the trending quiz"""

        btn = self.sender()

        if btn.text() != '':
            self.start_quiz(btn)


    def add_text_logo(self):
        """Adds text in an animated style"""

        text_list = ['', 'U', 'I', 'Z', 'B', 'O', 'X'] #List of text to be added
        text = '' #Initial text

        for i in text_list:
            text += i #Appends the text from the list
            self.logo_text.setText(text) #Sets the text in the logo
            self.wait(1)
        
        self.wait(5)
        self.anim.start() #Starts the last logo animation


    def remove_blur(self, val: int = 10):
        """
        Removes blur from the main window in an animated style.

        Parameters:
            val [int] : The value of blur provided
        """

        self.bg_frame.setEnabled(True) #Enables the main frame

        for i in reversed(range(val)):
            self.blur_effect.setBlurRadius(i) #Lowers blur intensity
            self.wait(1) #Waits for .1 seconds

        self.bg_frame.setGraphicsEffect(None) #Finally, sets graphic effect to None, removing blur


if __name__ == '__main__':
    #Writes to system log
    with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__)) + "\\QuizBoxClient\\Logs\\"), "System.log"), 'w') as f:
        for i in [str(item.split("\r")[:-1]) for item in subprocess.check_output(['systeminfo'], stderr=subprocess.DEVNULL).decode('utf-8').split('\n')]:
            f.write(f'{i[2:-2]}\n')

    sys.excepthook = except_hook #Configues exception handling
    APP = QApplication(sys.argv) #Initializes QApplication with sys
    WIN = Loading() #Instance for Loading class
    WIN.show() #Shows the Loading screen
    sys.exit(APP.exec()) #exec() calls the event loop to prevent app exit automatically
