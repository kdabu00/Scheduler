# TRIUMF-Scheduler
Constraint and Fitness evaluation program for TRIUMF Beam Accelerator Schedules.
Coded in Python, uses pandas and numpy libraries.
Can be used in all Operating Systems.

Prerequisites:
* Python 3.7.4 (The version we used) downloaded and installed
Download link: https://www.python.org/downloads/release/python-374/
* install the pandas and numpy 1.19.3 libraries
you can use terminal or cmd:
	* pip install pandas (This should install numpy as well but just incase you can use)
	* pip install numpy==1.19.3
* Either using cmd/terminal to run FitnessChecker.py or using a Python IDE (I suggest PyCharm Community Edition (Free version))
	* Download link: https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC
* an Ancestor Schedule excel file
* a Beam Request excel file
* Schedules to evaluate as excel files (can just use a copy of the Ancestor)

HOW TO USE:
* When using PyCharm, on the bottom right you have to choose an interpreter by clicking the section that says "<No interpreter>", so just make sure to have Python and the libraries installed first
* Place Ancestor Schedule in the Ancestor directory
* Place Request File in the Request directory
* Place Schedules to be evaluated in the Schedules directory
* Turn off parameters in the FitnessChecker.py or constraint.py to your liking Example: p1 = True (ON) or p1 = False (OFF)
* Run FitnessChecker.py either using an IDE or CMD/Terminal with the command: python FitnessChecker.py (make sure to be in the proper directory or use the full path)
* Fitness evaluations for each schedule in the Schedule Folder are generated as text files within the Schedule/Fitness folder.

<strong>WARNING:</strong>
There is a known error that can occur if you have one of the excel files open when running FitnessChecker.py, it is because of the temporary excel file that is created when the base file is open. To avoid this close all excel files before running the program.
