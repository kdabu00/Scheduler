"""
constraint.py - WIP
Author: Leo Liu, Kevin Dabu
a program to read excel files using pandas, containing methods to check the fitness parameters of a schedule
NOTE: the column headings in the schedule excel files start at row 1 which is
the row that contains 'Cyclotron', 'BL2A', 'ISAC' etc.. so the values/axes in pandas
include the actual column headings: 'Data', 'Exp. #', 'Facility' etc...
THIS IS NOT THE SAME FOR THE REQUESTS
"""

import pandas as pd
import datetime
import calendar
from Schedule import Schedule


def run_check(schedule):
    """Main function"""

    constraint_log_set = set()

    logs = (check_tb_length(schedule.schedule)[1], check_tb_start_time(schedule.schedule)[1], 
            check_integer_weeks(schedule.schedule)[1], check_target_station(schedule.schedule)[1], 
            check_ts_tm_alternates(schedule.schedule)[1], check_minimum_length_of_tb(schedule.schedule)[1])
    constraint_log_set.add(logs)

    bools_list = (check_tb_length(schedule.schedule)[0], check_tb_start_time(schedule.schedule)[0], 
            check_integer_weeks(schedule.schedule)[0], check_target_station(schedule.schedule)[0], 
            check_ts_tm_alternates(schedule.schedule)[0], check_minimum_length_of_tb(schedule.schedule)[0])

    valid_schedule = all(bools_list)

    if valid_schedule:
        return True
    else:
        return False


def findDay(date): 
    """Find a weekdays of a date"""
    weekday = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').weekday() 
    return (calendar.day_name[weekday]) 



def get_target_block_set(schedule):
    """Generate a list of all target blocks"""
    target_block_list = list()
    for i in range(schedule.schedule.index.size):  # schedule.index.size gets the amount of rows within the excel file
        if (schedule.schedule.values[i][11] != "Tgt") and (pd.notnull(schedule.schedule.values[i][11])):
            # Ignores values in Tgt that are equal Tgt or empty
            target_block = schedule.schedule.values[i][11]+schedule.schedule.values[i][12]+str(schedule.schedule.values[i][13])

            target_block_list.append(target_block)
            target_block_set = list(dict.fromkeys(target_block_list))
    return target_block_set, target_block_list

def get_ts_tm_combo(schedule):
    """Get the list of the Target Station/Target Module combination"""
    combo_list = list()
    for i in range(schedule.schedule.index.size):
        if (schedule.schedule.values[i][8] != "West / East") and (pd.notnull(schedule.schedule.values[i][8])):
            combo = schedule.schedule.values[i][8] + str(schedule.schedule.values[i][13])
            combo_list.append(combo)
            combo_list_2 = list(dict.fromkeys(combo_list))
    return combo_list, combo_list_2


def get_number_of_unsatisfied_constraints(bools_list):
    num_unsatisfied_constraints = 0
    for i in range(len(bools_list)):
        if not bools_list[i]:
            num_unsatisfied_constraints += 1
    return num_unsatisfied_constraints
            

def check_tb_start_time(schedule):
    """Checks rule #4 Target blocks start and end on a Tuesday DAY shift"""
    start_date = str(schedule.schedule.values[2][0])
    end_date = str(schedule.schedule.values[549][0])
    start_shift = schedule.schedule.values[2][1]
    end_shift = schedule.schedule.values[549][1]
    constraint_log = ""
    if findDay(start_date) == "Tuesday" and start_shift == "DAY" and findDay(end_date) == "Tuesday" and end_shift == "DAY":
        valid_schedule = True
    else:
        valid_schedule = False
        constraint_log = 'Target blocks start and end on a Tuesday DAY shift'
    return valid_schedule, constraint_log


def check_integer_weeks(schedule):
    """Checks rule #10 Each schedule has a fixed start date, and runs for a fixed integer number of weeks"""
    total_shifts_in_schedule = schedule.schedule.index.size

    constraint_log = ""
    if (total_shifts_in_schedule-1) % 21 == 0:
        valid_schedule = True
    else:
        valid_schedule = False
        constraint_log = 'The schedule should be a fixed integer weeks'

    return valid_schedule, constraint_log

def check_target_station(schedule):
    """Checks rule #1 The location of the Target Station and Target module at the schedule start is fixed"""
    combo_list_2 = get_ts_tm_combo(schedule)[1]
    combo_list = get_ts_tm_combo(schedule)[0]
    target_combo_list = (combo_list_2[0], combo_list_2[1])
    constraint_log = ""
    for i in range(len(combo_list)):
        if combo_list[i] in target_combo_list:
            valid_schedule = True
        else:
            valid_schedule = False
            constraint_log = 'The Target Station/Target Module combination is fixed'

    return valid_schedule, constraint_log


def check_ts_tm_alternates(schedule):
    """checks rule #2 if the combination of Target Station/Target Module alternates for each target block"""
    target_block_set = get_target_block_set(schedule)[0]
    constraint_log = ""
    for i in range(len(target_block_set) -1):
        if 'West' in target_block_set[i] and 'East' in target_block_set[i+1]:
            valid_schedule = True
        elif 'East' in target_block_set[i] and 'West' in target_block_set[i+1]:
            valid_schedule = True
        else:
            valid_schedule = False
            constraint_log = 'The Target Station/Target Module combination should alternate for each target block'
    return valid_schedule, constraint_log


def check_tb_length(schedule):
    """Checks rule #3 & #5 for the schedule except the final target block"""
    target_block_list = get_target_block_set(schedule)[1]
    target_block_shifts = 0
    constraint_log = ""
    for i in range(len(target_block_list)-43):  
        if ('UCx' in target_block_list[i]) and (target_block_list[i] == target_block_list[i+1]):
            target_block_shifts += 1.25
        elif (target_block_list[i] == target_block_list[i+1]):
            target_block_shifts += 1
        else:
            if target_block_shifts < 63 or target_block_shifts > 105:
                valid_schedule = False
                constraint_log = 'The maximum length of a target block with UCx is 4 weeks, and other target block is 5 weeks. The minimum length of a target block is 3 weeks'
                target_block_shifts = 0
    return valid_schedule, constraint_log


def check_minimum_length_of_tb(schedule):
    """Checks rule #6 The minimum length of the final target block in a schedule is 2 weeks """
    target_block_list = get_target_block_set(schedule)[1]
    target_block_shifts = 0
    constraint_log = ""
    for i in range(len(target_block_list)-1):
        if (target_block_list[i] == target_block_list[i+1]):
            target_block_shifts += 1
        else:
            if target_block_shifts < 42 :
                valid_schedule = False
                constraint_log = 'The minimum length of the final target block in a schedule is 2 weeks'
            target_block_shifts = 0
    return valid_schedule, constraint_log

