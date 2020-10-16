"""
constraint.py - WIP
Author: Leo Liu, Kevin Dabu

a program to read excel files using pandas, containing methods to check the fitness parameters of a schedule

NOTE: the column headings in the schedule excel files start at row 1 which is
the row that contains 'Cyclotron', 'BL2A', 'ISAC' etc.. so the values/axes in pandas
include the actual column headings: 'Data', 'Exp. #', 'Facility' etc...
THIS IS NOT THE SAME FOR THE REQUESTS
"""

import getpass
import os.path
import pandas as pd
import datetime
import calendar

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
    valid_schedule = check_targetblock(schedule)

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

def findDay(date): 
	weekday = datetime.datetime.strptime(date, '%m/%d/%Y').weekday() 
	return (calendar.day_name[weekday]) 

"""Checks rule #4 Target blocks start and end on a Tuesday DAY shift"""
def check_start_date(schedule: object):
    start_date = schedule.values[2][0]
    end_date = schedule.values[2][0]
    start_shift = schedule.values[2][1]
    end_shift = schedule.values[2][1]

    if findDay(start_date) == "Tuesday" and start_shift == "DAY" and findDay(end_date) == "Tuesday" and end_shift == "DAY":
        valid_schedule = True
    else:
        valid_schedule = False
        constrain_log = 'Target blocks start and end on a Tuesday DAY shift'
    return valid_schedule, constrain_log


def check_targetblock(schedule: object):
    """find the target block in a schedule"""
    target_block = ''
    target_block_list = list()
    target_block_shifts = 0
    constrain_log = ''
    combo_list = list()
    total_shifts_in_schedule = schedule.index.size
   
    """Checks rule #1 target station and target module"""
    for i in range(schedule.index.size):
        if (schedule.values[i][8] != "West / East") and (pd.notnull(schedule.values[i][8])):
            combo = schedule.values[i][8] + str(schedule.values[i][13])
            combo_list.append(combo)
            combo_list_2 = list(dict.fromkeys(combo_list))
    
    target_combo_list = (combo_list_2[0], combo_list_2[1])
    for i in range(len(combo_list)):
        if combo_list[i] in target_combo_list:
            valid_schedule = True
        else:
            valid_schedule = False
            constrain_log = 'The Target Station/Target Module combination is fixed'
            


    """Generate a list of all target blocks"""
    for i in range(schedule.index.size):  # schedule.index.size gets the amount of rows within the excel file
        if (schedule.values[i][11] != "Tgt") and (pd.notnull(schedule.values[i][11])):
            # Ignores values in Tgt that are equal Tgt or empty
            target_block = schedule.values[i][11]+schedule.values[i][12]+str(schedule.values[i][13])
            target_block_list.append(target_block)
            target_block_set = list(dict.fromkeys(target_block_list))
   
    """checks rule #2 if the combination of Target Station/Target Module alternates for each target block"""
    for i in range(len(target_block_set) -1):
        if 'West' in target_block_set[i] and 'East' in target_block_set[i+1]:
            valid_schedule = True
        elif 'East' in target_block_set[i] and 'West' in target_block_set[i+1]:
            valid_schedule = True
        else:
            valid_schedule = False
            constrain_log = 'The Target Station/Target Module combination should alternate for each target block'

    """Checks rule #3 & #5 for the schedule except the final target block"""
    for i in range(len(target_block_list)-43):  
        if ('UCx' in target_block_list[i]) and (target_block_list[i] == target_block_list[i+1]):
            target_block_shifts += 1.25
        elif (target_block_list[i] == target_block_list[i+1]):
            target_block_shifts += 1
        else:
            if target_block_shifts < 63 or target_block_shifts > 105:
                valid_schedule = False
                constrain_log = 'The maximum length of a target block with UCx is 4 weeks, and other target block is 5 weeks. The minimum length of a target block is 3 weeks'
                target_block_shifts = 0
    
    """Checks rule #6 The minimum length of the final target block in a schedule is 2 weeks """
    for i in range(len(target_block_list)-1):
        if (target_block_list[i] == target_block_list[i+1]):
            target_block_shifts += 1
        else:
            if target_block_shifts < 42 :
                valid_schedule = False
                constrain_log = 'The minimum length of the final target block in a schedule is 2 weeks'
            target_block_shifts = 0
    
    """Checks rule #10"""
    if (total_shifts_in_schedule-2) % 21 == 0:
        valid_schedule = True
    else:
        valid_schedule = False
        constrain_log = 'The schedule should be a fixed integernumber of weeks'

    return valid_schedule, constrain_log

if __name__ == "__main__":
    main()
