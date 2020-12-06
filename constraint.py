"""
constraint.py - WIP
Author: Leo Liu, Kevin Dabu
a program to read excel files using pandas, containing methods to check the fitness parameters of a schedule
"""

import datetime
import calendar

"""
   p1 = Target block length (Violated by current ancestor schedule I suggest to leave it off)
   p2 = Target block start on Tuesday day shift (Violated by current ancestor schedule I suggest to leave it off)
   p3 = Schedule with integer weeks
   p4 = Target Station and Target module at the schedule start is fixed
   p5 = Target Station/Target Module alternates for each target block
   p6 = The minimum length of the final target block in a schedule is 2 weeks (Violated by current ancestor schedule I suggest to leave it off)
"""

p1 = False
p2 = False
p3 = True
p4 = True
p5 = True
p6 = False


def run_check(schedule):
    """Runs the constraint check on the schedule object"""
    constraint_output = check_schedule(schedule)
    return constraint_output


def check_schedule(schedule):
    """Runs check depending on which parameters are True"""
    logs = ''
    bools = []

    if p1:
        logs += check_tb_length(schedule)[1]
        bools.append(check_tb_length(schedule)[0])
    if p2:
        logs += check_tb_start_time(schedule)[1]
        bools.append(check_tb_start_time(schedule)[0])
    if p3:
        logs += check_integer_weeks(schedule)[1]
        bools.append(check_integer_weeks(schedule)[0])
    if p4:
        logs += check_target_station(schedule)[1]
        bools.append(check_target_station(schedule)[0])
    if p5:
        logs += check_ts_tm_alternates(schedule)[1]
        bools.append(check_ts_tm_alternates(schedule)[0])
    if p6:
        logs += check_minimum_length_of_tb(schedule)[1]
        bools.append(check_minimum_length_of_tb(schedule)[0])

    valid_schedule = all(bools)
    return logs, valid_schedule


def findDay(date):
    """Find a weekdays of a date"""
    weekday = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').weekday()
    return (calendar.day_name[weekday])


def get_target_block_set(schedule):
    """Generate a list of all target blocks"""
    target_block_list = list()
    target_block_set = list()
    for i in range(len(schedule.schedule.index)):  # schedule.index.size gets the amount of rows within the excel file
        if schedule.target[i] != '':
            # Ignores values in Tgt that are equal Tgt or empty
            target_block = schedule.target[i]+schedule.source[i]+str(schedule.module[i])
            target_block_list.append(target_block)
            #target_block_set = list(dict.fromkeys(target_block_list))
    for i in range(len(target_block_list)-1):
        if target_block_list[i] != target_block_list[i+1]:
            target_block_set.append(target_block_list[i])
    return target_block_set, target_block_list


def get_ts_tm_combo(schedule):
    """Get the list of the Target Station/Target Module combination"""
    combo_list = list()
    for i in range(len(schedule.schedule.index)):
        if schedule.station[i] != '':
            combo = schedule.station[i] + str(schedule.module[i])
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
    start_date = str(schedule.date[2])
    end_date = str(schedule.date[547])
    start_shift = schedule.shift[2]
    end_shift = schedule.shift[547]
    constraint_log = ""
    if findDay(start_date) == "Tuesday" and start_shift == "DAY" and findDay(end_date) == "Tuesday" and end_shift == "DAY":
        valid_schedule = True
    else:
        valid_schedule = False
        constraint_log = 'Target blocks start and end on a Tuesday DAY shift\n'
    return valid_schedule, constraint_log


def check_integer_weeks(schedule):
    """Checks rule #10 Each schedule has a fixed start date, and runs for a fixed integer number of weeks"""
    total_shifts_in_schedule = schedule.size
    constraint_log = ""
    if (total_shifts_in_schedule-2) % 21 == 0:
        valid_schedule = True
    else:
        valid_schedule = False
        constraint_log = 'The schedule should be a fixed integer weeks\n'

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
            constraint_log = 'The Target Station/Target Module combination is fixed\n'

    return valid_schedule, constraint_log


def check_ts_tm_alternates(schedule):
    """checks rule #2 if the combination of Target Station/Target Module alternates for each target block"""
    target_block_set = get_target_block_set(schedule)[0]
    constraint_log = ""
    for i in range(len(target_block_set) -1):
        if '2' in target_block_set[i] and '4' in target_block_set[i+1]:
            valid_schedule = True
        elif '4' in target_block_set[i] and '2' in target_block_set[i+1]:
            valid_schedule = True
        else:
            valid_schedule = False
            constraint_log = 'The Target Station/Target Module combination should alternate for each target block\n'
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
        elif target_block_shifts < 63 or target_block_shifts > 105:
            valid_schedule = False
            constraint_log = 'The maximum length of a target block with UCx is 4 weeks, and other target block is 5 weeks. The minimum length of a target block is 3 weeks\n'
            target_block_shifts = 0
        else:
            valid_schedule = False

    return valid_schedule, constraint_log


def check_minimum_length_of_tb(schedule):
    """Checks rule #6 The minimum length of the final target block in a schedule is 2 weeks """
    target_block_list = get_target_block_set(schedule)[1]
    target_block_shifts = 0
    constraint_log = ""
    for i in range(len(target_block_list)-1):
        if target_block_list[i] == target_block_list[i+1]:
            target_block_shifts += 1
        else:
            if target_block_shifts < 42 :
                valid_schedule = False
                constraint_log = 'The minimum length of the final target block in a schedule is 2 weeks\n'
            target_block_shifts = 0
    return valid_schedule, constraint_log