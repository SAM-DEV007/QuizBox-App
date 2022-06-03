if __name__ != '__main__':  
    #Imports
    from mysql.connector import errorcode
    from cryptography.fernet import Fernet, InvalidToken
    from hashlib import sha3_512

    import mysql.connector as sql
    import shutil
    import os
    import sys
    import logging
    import subprocess
    import random
    import math
    import string
    import secrets
    import csv
    import json

    #Global Variables
    USER = PASSWORD = '' #Encryptd Username and Password
    CONNECTED = FIRST = False #Connection status with SQL; First is for checking first launch

    #Functions
    def except_hook(exc_type, exc_value, exc_traceback):
        """
        Except hook to catch unexpected exceptions.

        exc_type : The type of error
        exc_value : The error message
        exc_traceback : Traceback of the exception
        """

        logger = logging.getLogger(__name__) #Gets logger
        logger.critical(f"[Uncaught Exception]\n", exc_info=(exc_type, exc_value, exc_traceback)) #Logs the exception


    def salt_hash(txt: str) -> str:
        """
        Generates salted hashed password to store in database.

        Parameters:
            txt [str] : The password in plain text
        
        Returns:
            hashed_pass [str] : The salted hashed password to store in database
        """

        return sha3_512(f'QuIzBoX@#{txt}#@DaTaSaLt'.encode()).hexdigest()


    def random_key(quiz: bool = False) -> str:
        """
        Generates random alphanumeric key.

        Parameters:
            quiz [bool] [Default: False] : The value to get key for quiz

        Returns:
            key [str] : The generated key
        """

        if not quiz:
            val = sql_query(get_query='select AutoLogin, Auth from accounts;')
        else:
            val = sql_query(get_query='select UniqueKey from quizzes;')
        
        key = str("".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(30)]))

        if val:
            for value in val:
                if key in value:
                    key = str("".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(30)]))
                    random_key()

        return key


    def salt_encode(s: str) -> str:
        """
        Encodes the string in a specific algorithm.

        Parameters:
            s [str] : The string to be encoded
        
        Returns:
            txt [str] : Returns the encoded string
        """

        the_list = list() #Empty list

        for letter in s:
            ascii = ord(letter) #Gets ascii of the letter
            value = random.randint(1, 2) #Gets a random number
    
            #Algorithm-1 for False, and second for True
            ascii = (str(ascii*ascii*ord('b')+ord('2')) + str(ord('b')*2), str(ascii*ascii*ord('a')*ord('1')) + str(ord('a')))[value == 1]
            the_list.append(ascii) #Adds to the list

        return '-'.join(the_list) #Separates encoded letter with hyphen
    

    def salt_decode(s: str) -> str:
        """
        Decodes the encoded string with a specific algorithm.

        Parameters:
            s [str] : The string to be decoded
        
        Returns:
            txt [str] : The decoded string
        """

        new_list = list() #Empty list

        if s == '':
            return ''

        for ascii in s.split('-'): #Create a list of value separated by hyphen previously
            if ascii[::-1][0] == '6': #Algorithm 1
                ascii = int(ascii[:len(ascii)-3])
                ascii -= ord('2')
                ascii /= ord('b')
                ascii = math.sqrt(ascii)
            elif ascii[::-1][0] == '7': #Algorithm 2
                ascii = int(ascii[:len(ascii)-2])
                ascii /= ord('1')
                ascii /= ord('a')
                ascii = math.sqrt(ascii)
            new_list.append(chr(int(ascii))) #Adds the decoded letter to the list

        return ''.join(new_list) #Joins the letter and creates the decoded string


    def generate_keys():
        """Generates keys for encryption or decryption"""

        logger = logging.getLogger(__name__) #Gets logger
        logger.warning('Generation Triggered!')

        #Create empty file for data
        open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'w').close()

        if os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateAppData")):
            os.remove(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateAppData"))
        
        #Writes key
        key = Fernet.generate_key() #Generates key

        with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateAppData"), 'wb') as f:
            f.write(key)

        #Hides the file
        subprocess.check_call(["attrib", "+H", os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateAppData")])
        
        if os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateUserData")):
            os.remove(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateUserData"))
        
        #Writes key1
        key1 = Fernet.generate_key()

        with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateUserData"), 'wb') as f:
            f.write(key1)

        subprocess.check_call(["attrib", "+H", os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateUserData")])


    def save_to_file():
        """Saves SQL Username and Password to file"""

        try:
            #Writes decrypted username and password
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'w') as file:
                file.write('\n'.join([decrypt(USER), decrypt(PASSWORD)]))
            
            #Reads the File encryption key
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateAppData"), 'r') as read_file:
                key = read_file.readlines()
                fernet = Fernet(*key)
            
            #Reads the decrypted data
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'rb') as file:
                original = file.read()

            #Encrypts the file
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'wb') as file:
                file.write(fernet.encrypt(original))
        except FileNotFoundError as err:
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)

            generate_keys()
            save_to_file()


    def decrypt(txt: str) -> str:
        """
        This function is used to decrypt the :arg:

        Parameters:
            txt [str] : Encrypted bytecode
            store [bool] : Status for storing
        
        Returns:
            dec_text [str]: Decrypted UTF-8 character
        """

        try:
            #Reads the key
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateUserData"), 'r') as read_file:
                key = read_file.readlines()
            
            fernet = Fernet(*key) #Creates Instance

            return fernet.decrypt(txt).decode() #Decodes the encrypted bytecode
        except FileNotFoundError as err:
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)

            generate_keys()
            return decrypt(txt)  


    def encrypt(text: str) -> str:
        """
        This function is used to encrpt the :arg:

        Parameters:
            text [str] : UTF-8 character
        
        Returns:
            enc_text [str]: Encrypted bytecode
        """

        try:
            #Reads the file for the key
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateUserData"), 'r') as read_file:
                key = read_file.readlines()

            fernet = Fernet(*key)
            text = salt_encode(text)
            
            return fernet.encrypt(text.encode()) #Encrypted bytecode
        except FileNotFoundError as err:
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)

            generate_keys()
            return encrypt(text)


    def loading_presets():
        """Creates and loads data in SQL Database"""

        logger = logging.getLogger(__name__) #Gets logger
        logger.info('Loading presets...')

        #Creating database
        sql_query(query = ('use quizboxdata',
                        'create table accounts (Username varchar(255) primary key, Password varchar(255) not null, Fullname varchar(255) not null, Gender varchar(255) not null, DOB varchar(255) not null, AutoLogin varchar(255) not null, Auth varchar(255) not null, unique(AutoLogin, Auth));',
                        'create table quizzes (SNo int not null auto_increment primary key, Username varchar(255), QuizTitle varchar(255) not null, UniqueKey varchar(255), Data blob not null, Difficulty varchar(255) not null, Popularity int default 1, unique(UniqueKey), foreign key (Username) references accounts(Username) on update cascade on delete cascade);',
                        'create table feedbacks (SNo int auto_increment primary key, Username varchar(255), Feedback text, foreign key (Username) references accounts(Username) on update cascade on delete cascade);'
                    ))
        
        #Inserts account data
        account_data = [
            ('Aditya', salt_hash('aditya1234'), 'Aditya Tamhane', 'Male', '26-08-2004', random_key(), random_key()),
            ('Devansh', salt_hash('devansh1234'), 'Devansh Shrivastava', 'Male', '29-09-2004', random_key(), random_key()),
            ('Samyak', salt_hash('samyak1234'), 'Samyak Waghdhare', 'Male', '03-07-2005', random_key(), random_key()),
            ('Sankalp', salt_hash('sankalp1234'), 'Sankalp Gupta', 'Male', '02-11-2004', random_key(), random_key())
        ]

        for data in account_data:
            sql_query(
                insert_query='insert into accounts (Username, Password, Fullname, Gender, DOB, AutoLogin, Auth) values (%s, %s, %s, %s, %s, %s, %s)',
                insert_query_values=data
            )
        
        #Subject questions loading
        csv_files = {
            "Maths_Easy.csv": ["Maths", "Easy"],
            "Maths_Medium.csv": ["Maths", "Medium"],
            "Maths_Hard.csv": ["Maths", "Hard"],
            "Science_Easy.csv": ["Science", "Easy"],
            "Science_Medium.csv": ["Science", "Medium"],
            "Science_Hard.csv": ["Science", "Hard"],
            "GK_Easy.csv": ["GK", "Easy"],
            "GK_Medium.csv": ["GK", "Medium"],
            "GK_Hard.csv": ["GK", "Hard"],
            "Computers_Easy.csv": ["Computers", "Easy"],
            "Computers_Medium.csv": ["Computers", "Medium"],
            "Computers_Hard.csv": ["Computers", "Hard"]
        } #Filename with filedata

        for file_name, data_list in csv_files.items():
            file_location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Profile\\", file_name) #Location of the files, it will crash if not found
            name, difficulty = data_list #Name of the QuizTitle and difficulty
            file_data = {} #Empty dictionary

            with open(file_location, encoding='cp1252') as f: #cp1252 encoding
                reader = csv.DictReader(f) #Reads as a dictionary

                for rows in reader:
                    key = rows['Sno'] #Key of the dictionary
                    del rows['Sno'] #Removes Sno from the dictionary of rows
                    del rows['Option'] #Removes Option
                    file_data[key] = rows #Assigns key with rows as value
            
            sql_query(insert_query='insert into quizzes (QuizTitle, Difficulty, Data) values (%s, %s, %s)',
                        insert_query_values=(name, difficulty, json.dumps(file_data))) #Inserts the values in the database
        
        #Inserts Community Quiz
        #Aditya's
        csv_files = {
            "NASA.csv": ["NASA", "Medium"],
            "Wonder_Of_The_World.csv": ["Wonders of the World", "Medium"]
        } #Filename with filedata

        for file_name, data_list in csv_files.items():
            file_location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Profile\\", file_name) #Location of the files, it will crash if not found
            name, difficulty = data_list #Name of the QuizTitle and difficulty
            file_data = {} #Empty dictionary

            with open(file_location, encoding='cp1252') as f: #cp1252 encoding
                reader = csv.DictReader(f) #Reads as a dictionary

                for rows in reader:
                    key = rows['Sno'] #Key of the dictionary
                    del rows['Sno'] #Removes Sno from the dictionary of rows
                    del rows['Option'] #Removes Option
                    file_data[key] = rows #Assigns key with rows as value
            
            sql_query(insert_query='insert into quizzes (Username, QuizTitle, UniqueKey, Difficulty, Data) values (%s, %s, %s, %s, %s)',
                        insert_query_values=('Aditya', name, random_key(True), difficulty, json.dumps(file_data))) #Inserts the values in the database


        #Devansh's
        csv_files = {
            "Bhopal_Gas_Tragedy.csv": ["Bhopal Gas Tragedy", "Medium"],
            "Plastics.csv": ["Plastics", "Easy"]
        } #Filename with filedata

        for file_name, data_list in csv_files.items():
            file_location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Profile\\", file_name) #Location of the files, it will crash if not found
            name, difficulty = data_list #Name of the QuizTitle and difficulty
            file_data = {} #Empty dictionary

            with open(file_location, encoding='cp1252') as f: #cp1252 encoding
                reader = csv.DictReader(f) #Reads as a dictionary

                for rows in reader:
                    key = rows['Sno'] #Key of the dictionary
                    del rows['Sno'] #Removes Sno from the dictionary of rows
                    del rows['Option'] #Removes Option
                    file_data[key] = rows #Assigns key with rows as value
            
            sql_query(insert_query='insert into quizzes (Username, QuizTitle, UniqueKey, Difficulty, Data) values (%s, %s, %s, %s, %s)',
                        insert_query_values=('Devansh', name, random_key(True), difficulty, json.dumps(file_data))) #Inserts the values in the database

        logger.info('Loading presets SUCCESS!!')


    def check():
        """
        Checks the connection with SQL server.

        Returns:
            connection [bool] : SQL connection status
            description [str] : Error occured in SQL
        """

        global CONNECTED

        if USER == '' or PASSWORD == '': #If empty/no input is provided, initiate Timeout
            return None, 'Timeout'

        try:
            with sql.connect(
                host = "localhost",
                user = salt_decode(decrypt(USER)),
                password = salt_decode(decrypt(PASSWORD))
            ) as _:
                CONNECTED = True #Connected to SQL
            sql_query() #Used here for checking the loading first time
            return True, None
        except sql.Error as err:
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)
            
            return False, str(err) #Not connected


    def sql_query(query: tuple = (), insert_query: str = '', insert_query_values: tuple = (), get_query: str = '', get_query_values: tuple = (), rows: int = 0):
        """
        Connects to SQL and performs queries in :arg:

        Parameters:
            query [tuple] : The tuple of queries to be executed (without placeholder insert values)
            insert_query [str] : The query to be executed for inserting values
            insert_query_values [tuple] : The tuple of values to be added
            get_query_values [tuple] : The optional values to retrieve data
            get_query [str] : The query to get values
            rows [int] [Default: 0] : 0 -> fetchall() | 1 -> fetchone() | 2,3,4...n -> fetchmany(n)
        
        Returns:
            returned_query [tuple] : The query returned by the SQL
        """

        global FIRST

        with sql.connect(
            host = "localhost",
            user = salt_decode(decrypt(USER)),
            password = salt_decode(decrypt(PASSWORD))
        ) as connection:
            cur = connection.cursor() #Cursor for queries

            try:
                cur.execute("use quizboxdata") #Checks if the database exists
                if FIRST:
                    FIRST = False
                    cur.execute('drop database quizboxdata') #Query to delete/drop the database
                    cur.execute('create database quizboxdata')
                    cur.execute('use quizboxdata')
                    loading_presets() #Triggers presets load for database
            except sql.Error as err:
                logger = logging.getLogger(__name__) #Gets logger
                logger.warning(err)
                
                if err.errno == errorcode.ER_BAD_DB_ERROR: #If no database found
                    cur.execute('create database quizboxdata')
                    if FIRST:
                        FIRST = False
                    loading_presets() #Triggers the first time loading function

            if query: #If query is passed
                for q in query:
                    cur.execute(q) #Execute the queries
                connection.commit() #Save changes
                return #Only one type of query per call out of three
            
            if insert_query != '':
                cur.execute(insert_query, insert_query_values) #Placeholders will be there to prevent SQL Injection
                connection.commit()
                return #Only one type of query per call out of three
            
            if get_query != '':
                cur.execute(get_query, get_query_values)
                if rows == 0:
                    return cur.fetchall() #Gets all rows
                elif rows == 1:
                    return cur.fetchone() #Gets one row
                elif rows > 1:
                    return cur.fetchmany(size=rows) #Gets n-rows


    def auto_trigger():
        """
        Grabs username and password from the encrypted file.

        Returns:
            username [bytes] : Encrypted Username of SQL
            password [bytes] : Encrypted Password of SQL
        """

        try:
            try:
                #Opens the saved credential data file
                with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'rb') as file:
                    read_lines = file.readlines()
                    if not read_lines: 
                        return '', '' #If the file is empty
            except FileNotFoundError as err:
                logger = logging.getLogger(__name__) #Gets logger
                logger.warning(err)

                open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'w').close()
                return '', ''

            #Opens the File key
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Preinstall_Data\\", "PrivateAppData"), 'rb') as key_file:
                key = key_file.read()
            fernet = Fernet(key)
        except ValueError as err:
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)

            generate_keys()
            return auto_trigger()
        
        try:
            a = fernet.decrypt(*read_lines).decode() #Decrypts the bytecode
        except InvalidToken as err: #If someone changed the encrypted key
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)

            return '', '' #Sets to default
        i = 0 #0 -> Username; 1 -> Password in _list
        _list = ['', '']

        for letter in list(a):
            if ord(letter) != 10 and ord(letter) != 13: #letter should not be '\r' or '\n'
                _list[i] += letter
            else: #Indicates that the username has ended
                i = 1 #Switches to password

        return encrypt(salt_decode(_list[0])), encrypt(salt_decode(_list[1])) #Encrypts username and password


    def check_connection_auto():
        """
        Checks the connection with SQL with saved credentials.

        Returns:
            connected [bool] : Status of connection with SQL
        """

        try:
            if USER == '' or PASSWORD == '': #If username and password is empty
                raise sql.Error #Raises error -> sql.Error
            with sql.connect(
                host = "localhost",
                user = salt_decode(decrypt(USER)),
                password = salt_decode(decrypt(PASSWORD))
            ) as _:
                return True #Successful connection
        except sql.Error as err:
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)

            #Clears the file
            open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'w').close()
            return False #Unsuccessful connection
        except TypeError as err:
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)

            open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'w').close()
            return False
    

    def check_config(write_value: bool = False, passed_dict: dict = dict()):
        """
        Checks for the existance of config file, and when not found, writes the default data

        Parameters:
            write_value [bool] : The value to determine write to the file
            passed_dict [dict] : The dictionary to be used for writing data
        """

        #Checks if the config file exists
        if write_value or os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\Config\\", "QuizBoxSettings.ini")) is False:
            config_dictionary = passed_dict

            if write_value is False:
                config_dictionary["SETTINGS"] = {
                    "sql": salt_encode("True"),
                    "rememberaccount": salt_encode("True"),
                    "start": salt_encode("True")
                } #sql - SQL Data, rememberaccount - Auto-login in app account, start - Starting animation
                config_dictionary["LOGIN"] = {
                    "accountlogin": salt_encode(f'guest{str("".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(10)]))}'),
                    "first": salt_encode("True")
                } #accountlogin - The data for account data, first - First time app launch

            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\Config\\", "QuizBoxSettings.ini"), 'w') as CONF:
                for title in config_dictionary:
                    CONF.write(f'\n[{title}]\n') #Writes title for the config
                    for key, value in config_dictionary[title].items():
                        CONF.write(f'{key}={value}\n') #Writes the key and value of the data
    

    def edit_config(title: str, key: str, value: str, logged = None, username: str = ''):
        """
        Edits the configuration file

        Parameters:
            title [str] : Title in the config file
            key [str] : Key in the title
            value [str] : Value to be assigned
            logged : Only to be used for rememberaccount key
            username [str] : Only to be used with logged
        """

        config_data = read_config() #Gets the config dictionary
        config_data[title][key] = salt_encode(value) #Assigns the value
        check_config(True, config_data) #Writes the edited data

        if key == 'sql':
            if value == "False":
                if not os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\", "Cache")):
                    os.makedirs(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\", "Cache"))
                original = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat")
                target = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Cache\\", "PrivateQUIZBOXData.dat")

                shutil.copyfile(original, target)
                open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'w').close()
            elif value == "True":
                if os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\", "Cache")):
                    if os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Cache\\", "PrivateQUIZBOXData.dat")):
                        original = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat")
                        target = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Cache\\", "PrivateQUIZBOXData.dat")

                        shutil.copyfile(target, original)
        elif key == 'rememberaccount':
            if value == "False":
                #Changes the account login info back to guest
                edit_config('LOGIN', 'accountlogin', f'guest{str("".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(10)]))}')
            elif value == "True":
                #Changes the account login info to account, if logged in
                if logged:
                    returned = sql_query(get_query='select AutoLogin from accounts where Username = %s', get_query_values=(username,))
                    if returned:
                        edit_config('LOGIN', 'accountlogin', *returned[0])
        elif key == 'first' and value == 'True':
            #Removes the config file
            if os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\Config\\", "QuizBoxSettings.ini")):
                os.remove(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\Config\\", "QuizBoxSettings.ini"))
        elif key == 'accountlogin' and value == 'False':
            #Resets the account auto login data
            edit_config('LOGIN', 'accountlogin', f'guest{str("".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(10)]))}')


    def read_config() -> dict:
        """
        Reads the config file

        Returns:
            config_dict [dict] : The dictionary created by the config file
        """

        try:
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\Config\\", "QuizBoxSettings.ini"), 'r') as f:
                lines = f.readlines() #Reads all the lines
                prev_title = None #Placeholder for title
                config_dict = dict() #Empty dictionary

                for line in lines:
                    line = line.replace('\n', '')
                    if line != '': #If the line is not empty after filtration
                        if '[' in line: #Checks for title
                            line = line.replace('[', '')
                            line = line.replace(']', '')
                            config_dict[line] = dict() #Adds an empty dictionary
                            prev_title = line
                            continue
                        line = line.split('=') #Creates a list of key, value
                        config_dict[prev_title][line[0]] = line[1] #Assigns key with value
        except FileNotFoundError as err:
            logger = logging.getLogger(__name__) #Gets logger
            logger.warning(err)

            check_config()
            generate_keys()
            return read_config() #Returns the config after creating new file
        
        return config_dict #Returns the dictionary

    sys.excepthook = except_hook #Handles uncaught exceptions

    #Checks and create directories if not found
    FOLDER_NAMES = {
        "\\Data\\": ("Cache", "Preinstall_Data", "Saved"),
        "\\Data\\Saved\\": ("Config",),
        "": ("Logs",),
        }

    #Chcks for folder in the location
    for location in FOLDER_NAMES:
        for folder in FOLDER_NAMES[location]:
            if not os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + location, folder)):
                os.makedirs(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + location, folder))
    
    #Logger
    logging.basicConfig(filename=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__)) + "\\Logs\\"), "QuizAppLog.log"),
                    format='[%(asctime)s.%(msecs)03d] [%(levelname)s] : %(message)s',
                    datefmt="%d-%m-%Y %H:%M:%S",
                    filemode='w',
                    level=logging.DEBUG)
    
    if not os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat")):
        open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))) + "\\Data\\Saved\\", "PrivateQUIZBOXData.dat"), 'w').close()

    FIRST = salt_decode(read_config()["LOGIN"]["first"]) == "True" #Checks the value
    if FIRST:
        check_config()
        generate_keys()

    USER, PASSWORD = auto_trigger() #Assigns Username and Password found in the file
    CONNECTED = check_connection_auto() #Checks for the validation of the credentials

    check_config()
