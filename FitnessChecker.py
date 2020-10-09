"""
FitnessChecker.py - WIP
Author: Kevin Dabu

a program to read excel files using pandas, containing methods to check the fitness parameters of a schedule

NOTE: the column headings in the schedule excel files start at row 1 which is
the row that contains 'Cyclotron', 'BL2A', 'ISAC' etc.. so the values/axes in pandas
include the actual column headings: 'Data', 'Exp. #', 'Facility' etc...
THIS IS NOT THE SAME FOR THE REQUESTS
"""

import getpass
import os.path
import pandas as pd
import ExcelFileManager as efm


def main():
    """Main function"""
    # gets the current logged in user's name
    user = getpass.getuser()

    # Grabs filename input from user
    schedule_name, requests_name = efm.ask_file_names()

    # I placed my excel files in C:\Users\USERNAME\Documents. Note: depending on where the file is *change*
    schedule_path = os.path.join("C:\\Users", user, "Documents", schedule_name)
    requests_path = os.path.join("C:\\Users", user, "Documents", requests_name)

    # assign the excel data frame to schedule variable
    schedule = efm.read_file(schedule_path)
    requests = efm.read_file(requests_path)

    # Find unique scheduled experiments and requested experiments w/priorities
    scheduled_experiments = get_unique_experiments(schedule)
    exp_priorities = get_experiments_and_priorities(requests)
    num_priorities, exp_not_listed = check_priorities(scheduled_experiments, exp_priorities)

    # Call output function to display fitness
    output_fitness(exp_not_listed, exp_priorities, num_priorities, scheduled_experiments)


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


def output_fitness(exp_not_listed, exp_priorities, num_priorities, scheduled_experiments):
    print("-" * 200)
    print("OVERVIEW OF SCHEDULE FITNESS")
    print("-" * 200)
    print("Experiments Scheduled: " + str(len(scheduled_experiments)))
    print("Beam requests satisfied: %d/%d, %0.2f"
          % (len(scheduled_experiments), len(exp_priorities), (len(scheduled_experiments)/len(exp_priorities))))
    print("There are %d high priority experiment(s) and %d medium priority experiment(s) scheduled."
          % (num_priorities['H'], num_priorities['M'],))
    print("High Priority Experiments / Total Experiments: %d/%d, %0.2f"
          % (num_priorities['H'], len(scheduled_experiments), (num_priorities['H']/(len(scheduled_experiments)))))
    if len(exp_not_listed) > 0:
        print("Experiments:", end="")
        for i in exp_not_listed:
            print(" " + i, end="")
        print(" are not listed in the requests file so their priority is not accounted for.")


if __name__ == "__main__":
    main()
