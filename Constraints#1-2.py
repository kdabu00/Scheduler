import constraint
"""
Author: David Chin
Rule 1: The location of the Target Station at the schedule start is fixed and cannot change, and the corresponding
Target Module is also fixed
Rule 2: The Target Station/Target Module combination alternates for each target block


problem = constraint.Problem()
# Target Station variable can only be East or West
problem.addVariable('Target_Station', ["East", "West"])
# Target Module can only be #2 or #4 (future - add #3 & #5)
problem.addVariable('Target_Module', ["#2", "#4"])

def constraint_rule_1 (Target_Station, Target_Module):
    if Target_Station == "East" or "West" and Target_Module == "#2" or "#4":
        return True

def constraint_rule_2 ():

problem.addConstraint(constraint_rule_1, ['Target_Station','Target_Module'])

solutions = problem.getSolutions()
"""

"""
constraint.py - WIP
Author: Leo Liu, Kevin Dabu, David Chin
a program to read excel files using pandas, containing methods to check the fitness parameters of a schedule
NOTE: the column headings in the schedule excel files start at row 1 which is
the row that contains 'Cyclotron', 'BL2A', 'ISAC' etc.. so the values/axes in pandas
include the actual column headings: 'Data', 'Exp. #', 'Facility' etc...
THIS IS NOT THE SAME FOR THE REQUESTS
"""

import getpass
import os.path
import pandas as pd


def main():
    """Main function"""

    # gets the current logged in user's name
    user = getpass.getuser()

    # Grabs filename input from user
    schedule_name = ask_file_names()

    # I placed my excel files in C:\Users\USERNAME\Documents. Note: depending on where the file is *change*
    schedule_path = os.path.join("C:\\Users", user, "Documents", schedule_name)

    # assign the excel data frame to schedule variable
    schedule = read_file(schedule_path)

    constrain_log = check_targetblock(schedule)[1]
    valid_schedule = check_targetblock(schedule)[0]

    # Outputs - Will probably be made into a separate function and saved for future use
    print("-" * 100)
    print("OVERVIEW OF SCHEDULE RULES")
    print("-" * 100)

    if valid_schedule == True:
        print("This is a valid schedule")
    else:
        print("This schedule is not valid: ", constrain_log)


def read_file(path: str) -> object:
    """Open excel schedule, displays contents turns excel file into a data frame: schedule"""
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    excel_file = pd.read_excel(path)  # first index: row, second index: column ex. schedule.values[0][0] == 'Date'
    return excel_file


def ask_file_names() -> object:
    """Prompts user for file names for requests and schedules, then returns them"""
    schedule_name = input("Input schedule file name (Schedule 138 Ancestor.xlsx): ")
    return schedule_name


def check_target_station(schedule: object):
    """Checks target station and target module (rule 1)"""
    target_combo_set = set{}
    for i in range(schedule.index.size):
        if (schedule.values[i][8] != "West / East") and (pd.notnull(schedule.values[i][8])):
        combo = schedule.values[i][8] + str(schedule.values[i][13])
        return True