# TRIUMF-Scheduler
Constraint and Fitness evaluation program for TRIUMF Beam Accelerator Schedules.
Coded in Python, uses pandas and numpy libraries.
Can be used in all Operating Systems.

Prerequisites:
* Python 3 downloaded and installed
* install the pandas and numpy libraries
* Either using cmd/terminal to run FitnessChecker.py or using a Python IDE (I suggest PyCharm).
* an Ancestor Schedule excel file
* a Beam Request excel file

HOW TO USE:
* Place Ancestor Schedule in the Ancestor directory
* Place Request File in the Request directory
* Place Schedules to be evaluated in the Schedules directory
* Run FitnessChecker.py either using an IDE or CMD/Terminal (make sure to be in the proper directory)
* Fitness evaluations for each schedule in the Schedule Folder are generated as text files within the Fitness folder.