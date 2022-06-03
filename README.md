# QuizBox-App
The app created for IP Project for Class 12th.

# System Requirements
  ## Minimum System Requirements
  - Processors: Intel Atom® processor or Intel® Core™ i3 processor
  - Operating systems: Windows 7 or later
  - [Python](https://www.python.org/downloads/) versions: 3.X
  - [MySQL](https://dev.mysql.com/downloads/installer/)
  
  ## Recommended System Requirements
  - Processors:Intel® Core™ i5 processor 4300M at 2.60 GHz or 2.59 GHz (1 socket, 2 cores, 2 threads per core), 8 GB of DRAMIntel® Xeon® processor E5-2698 v3 at 2.30 GHz (2 sockets, 16 cores each, 1 thread per core), 64 GB of DRAMIntel® Xeon Phi™ processor 7210 at 1.30 GHz (1 socket, 64 cores, 4 threads per core), 32 GB of DRAM, 16 GB of MCDRAM (flat mode enabled)
  - Operating systems: Windows 10
  - [Python](https://www.python.org/downloads/) versions: 3.X
  - [MySQL](https://dev.mysql.com/downloads/installer/)

# Installation
- Click on `Code` in top-right. And in the drop down list, and click on `Download ZIP`, and a ZIP file should be installed.
- Extract the contents of the ZIP folder.
- Open Command Prompt at the location of main directory, and type `pip install -r requirements.txt`. Alternately, you can do `pip install -r Path to main directory\requirements.txt`, where [Path to main directory] should be your path to the main directory of the folder.
- The app can be launched by launching `App.pyw` file.

# About
The app is on playing interesting quizzes in vast amount of subjects and topics, where the quizzes are either made by the developers or added by our very own community. The user can create account and can track the quizzes created. It also tracks the quizzes that are both being played more and less. The question length consists from 5 to 10, and the difficulty ranges from Easy, Medium to Hard. The algorithm chooses different questions based on the number of questons and difficulty specified. It also evaluates the results at the end and shows the user performance. Both logged in and logged out users are able to play infinite amount of quizzes.

# Working of the app [Backend]
The app's database is purely dependant on MySQL. The source code is written in Python language.

When the app is launched for the first time, or the SQL connection is failed, it asks the user to enter the Username and Password. The app stores the credentials in a triple encrypted format (encrypted three times), and are never stored in the script/memory as a plain text, but rather in an encrypted format. A key is provided to the user, if the username/password is forgotten to recover username/password. If the key is lost, there is currently no way to recover the account.

E-Mail services for feedback and forgot account password/username is not included intentionally, as it requires actual E-Mail Username and Password for it to work, which may/may not be misused.

`MySQL_Queries.py` is the module, used for processing SQL Queries and Data processing. `App.pyw` is the script, where the app can be launched. The app runs using [PyQt6](https://pypi.org/project/PyQt6/). The data of pre-loaded quiz is saved in multiple `.csv` files, and are added to database after first successful launch. `Resources` folder contains all the logos and the images in the app. `UI` folder consists of multiple UIs for the app, created using [QtDesigner](https://doc.qt.io/qt-5/qtdesigner-manual.html).

After creating account, the Username is saved as `Plain Text` in the database but the Password is saved using hash algorithm with custom salt. The database includes three tables, `accounts`, `quizzes` and `feedbacks`, which stores account information, quiz information and feedback information respectively. While inserting or updating values, placeholders are used in order to prevent SQL Injection.

The quiz data is saved as [JSON](https://www.json.org/json-en.html) in the database. The quiz is linked to the user with the help of `foreign key`, i.e., the quiz will get deleted if the user decides to delete the account. The same is used in `feedbacks`. When the quiz is started, its `Popularity` is increased by 1 and after successful completion, it raises by 5. `Popularity` determines the trending status of the quiz.

# Troubleshooting for errors
The app may take variable amount of time to start according to the system hardware and/or software.

If the app is not starting:
- Open Task Manager, in the `Processes` Tab in `Background processes` section.
- Search for `Python`, click on it, and click on `End Task`.\n
If the above doesn't work:
- Go to app's main directory.
- Open `QuizBoxClient` folder, and ZIP the `Logs` folder.
- Send the ZIPPED folder to the developer - Samyak.

If the app is crashing randomly, or not performing as intended:
- Go to app's main directory.
- Open `QuizBoxClient` folder, and ZIP the `Logs` folder.
- Send the ZIPPED folder to the developer - Samyak, along with the detailed description of the steps performed.

# Contributers
- Samyak Waghdhare: Programmer/Final changes with files provided.
- Devansh Shrivastava: Presenter/Created Questions for quiz.
- Aditya Tamhane: Designer/Created Questions for quiz.
- Sankalp Gupta: Designed App Logo.
