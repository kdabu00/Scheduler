"""
constrain.py - WIP
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

def main():
    """Main function"""
    # gets the current logged in user's name
    user = getpass.getuser()

    # Grabs filename input from user
    schedule_name, requests_name = ask_file_names()

    # I placed my excel files in C:\Users\USERNAME\Documents. Note: depending on where the file is *change*
    schedule_path = os.path.join("C:\\Users", user, "Documents", schedule_name)
    requests_path = os.path.join("C:\\Users", user, "Documents", requests_name)

    # assign the excel data frame to schedule variable
    schedule = read_file(schedule_path)
    requests = read_file(requests_path)

    # Find unique scheduled experiments and requested experiments w/priorities
    scheduled_experiments = get_unique_experiments(schedule)
    exp_priorities = get_experiments_and_priorities(requests)
    num_priorities, exp_not_listed = check_priorities(scheduled_experiments, exp_priorities)

    # Outputs - Will probably be made into a separate function and saved for future use
    print("-" * 200)
    print("OVERVIEW OF SCHEDULE FITNESS")
    print("-" * 200)
    print("Experiments Scheduled: " + str(len(scheduled_experiments)))
    print("Beam requests satisfied: " + str(len(scheduled_experiments)) + '/' + str(len(exp_priorities)))
    print("There are " + str(num_priorities['H']) + " high priority experiment(s) and " +
                             str(num_priorities['M']) + " medium priority experiment(s) scheduled.")
    print("High Priority Experiments / Total Experiments: " + str(num_priorities['H'])
          + '/' + str(len(scheduled_experiments)))
    

    if len(exp_not_listed) > 0:
        print("Experiments:", end="")
        for i in exp_not_listed:
            print(" " + i, end="")
        print(" are not listed in the requests file so their priority is not accounted for.")


def read_file(path: str) -> object:
    """Open excel schedule, displays contents turns excel file into a data frame: schedule"""
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    excel_file = pd.read_excel(path)  # first index: row, second index: column ex. schedule.values[0][0] == 'Date'
    return excel_file


def get_unique_experiments(schedule: object) -> set:
    """Finds the number of experiments index: 5 == Exp. #"""
    scheduled_exp = set()
    for i in range(schedule.index.size):  # schedule.index.size gets the amount of rows within the excel file
        if (schedule.values[i][5] != "Exp. #") & ~(pd.isnull(schedule.values[i][5])) & \
                (schedule.values[i][5] != 'Test') & (schedule.values[i][5] != 'Setup'):
            # Ignores values in Exp. # that are equal to Exp. #, Test, Setup or empty
            scheduled_exp.add(schedule.values[i][5])
    return scheduled_exp


def get_experiments_and_priorities(requests: object) -> object:
    """Creates a dictionary with experiments as key, and priority as value"""
    exp_requests = requests['Experiment'].tolist()
    priority = requests['Priority'].tolist()
    exp_priorities = {}
    for i in range(len(exp_requests)):
        if exp_requests[i] != 'Test':
            exp_priorities[exp_requests[i]] = priority[i]
    return exp_priorities


def check_priorities(scheduled_experiments: set, exp_priorities: dict) -> object:
    """Checks the priority of the scheduled experiments returns the number of H or M and experiments not listed"""
    num_priorities = {'H': 0, 'M': 0}
    not_listed = []  # stores experiments not listed in the requests file, *not sure if this should happen*
    for i in scheduled_experiments:
        if i in exp_priorities:
            if exp_priorities[i] == 'H':
                num_priorities['H'] += 1
            else:
                num_priorities['M'] += 1
        else:
            not_listed.append(i)
    return num_priorities, not_listed


def ask_file_names() -> object:
    """Prompts user for file names for requests and schedules, then returns them"""
    schedule_name = input("Input schedule file name (Schedule 138 Ancestor.xlsx): ")
    requests_name = input("Input beam requests file (Schedule 138 Beam Requests.xlsx): ")
    return schedule_name, requests_name

def check_targetblock(schedule: object):
    """find the target block in a schedule"""
    target_block = ''
    target_block_list = list()
    target_block_shifts = 0
    valid_schedule = True

    """Generate a list of all target blocks"""
    for i in range(schedule.index.size):  # schedule.index.size gets the amount of rows within the excel file
        if (schedule.values[i][11] != "Tgt") and (pd.notnull(schedule.values[i][11])):
            # Ignores values in Tgt that are equal Tgt or empty
            target_block_list.add(schedule.values[i][11]+schedule.values[i][12]+schedule.values[i][13])
   
    """Check rule #3 & #5 for the schedule except the final target block"""
    for i in range(len(target_block_list)-43):  
        if ('UCx' in target_block[i]) and (target_block[i] == target_block[i+1]):
            target_block_shifts += 1.25
        elif (target_block[i] == target_block[i+1]):
            target_block_shifts += 1
        else:
            if target_block_shifts < 63 or target_block_shifts > 105:
                valid_schedule = False
                target_block_shifts = 0
    """Check rule #6"""
    for i in range(len(target_block_list)-1):
        if (target_block[i] == target_block[i+1]):
            target_block_shifts += 1
        else:
            if target_block_shifts < 42 :
                valid_schedule = False
            target_block_shifts = 0
    """check rule #10"""
    total_shifts_in_schedule = schedule.index.size 
    if (total_shifts_in_schedule-1) % 21 == 0
        valid_schedule = True
    else:
        alid_schedule = False

    return valid_schedule

if __name__ == "__main__":
    main()
