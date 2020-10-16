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
    num_priorities = check_priorities(scheduled_experiments, exp_priorities)

    # Call output function to display fitness
    output_fitness(exp_priorities, num_priorities, scheduled_experiments)


def get_unique_experiments(schedule: object) -> set:
    """Finds the number of experiments index: 5 == Exp. #"""
    # Rename the column names to the appropriate values
    schedule.columns = ['Date', 'Shift', 'Cyclotron_Offline', 'current(uA)', 'BL2A_Offline',
                        'I_Exp.#', 'I_Facility', 'I_Note', 'I_West/East', 'I_Beam', 'I_Energy (keV)', 'I_Tgt',
                        'I_Source', 'I_Mod',
                        'O_Exp.#', 'O_Facility', 'O_Note', 'O_Beam', 'O_Energy (keV)', 'O_Source', 'O_Offline']

    # drop all rows in dataframe that had the values of index 0/row 2 in excel file
    schedule = schedule.drop(schedule.index[0])

    # Change nan values into empty string
    schedule = schedule.fillna('')

    # Ignores values in Exp. # that are equal to Exp. #, Test, Setup or empty, IGNORING Experiment S2000 *Filler exp*
    schedule = schedule.loc[(schedule['I_Exp.#'] != '') & (schedule['I_Exp.#'] != 'Test')
                            & (schedule['I_Exp.#'] != 'Setup') & (schedule['I_Exp.#'] != 'S2000')]

    # Change SIS/RILIS to just RILIS
    schedule['I_Source'] = schedule['I_Source'].replace(['SIS/RILIS'], 'RILIS')

    # Strip trailing and leading whitespace from facility column
    schedule['I_Facility'] = schedule['I_Facility'].str.strip()

    # Make a list of each row with ISAC experiment #, Facility, Beam, Target, and Source
    unique_exp = schedule[['I_Exp.#', 'I_Facility', 'I_Beam', 'I_Tgt', 'I_Source']].values.tolist()

    scheduled_exp = set()
    # Store each experiment as a tuple inside of a set
    for exp in unique_exp:
        scheduled_exp.add(tuple(exp))
    return scheduled_exp


def get_experiments_and_priorities(requests: object) -> dict:
    """Creates a dictionary with experiments as key, and priority as value"""
    # Check if a request is an ISAC experiment and if the Experiment # is Test
    unique_exp = requests.loc[(requests['Beam options'] == 'ISAC Target (RIB)') & (requests['Experiment'] != 'Test')]
    priority = unique_exp['Priority'].tolist()
    field = unique_exp['Field'].tolist()
    unique_exp = unique_exp.fillna('') # change nan values into empty string
    unique_exp = unique_exp[['Experiment', 'Facility', 'Beam', 'Target', 'Ion Source']].values.tolist()
    exp_priorities = {}
    for i in range(len(unique_exp)):
        exp_priorities[tuple(unique_exp[i])] = [priority[i], field[i]]
    return exp_priorities


def check_priorities(scheduled_experiments: set, exp_priorities: dict) -> object:
    """Checks the priority of the scheduled experiments returns the number of H or M and experiments not listed"""
    num_priorities = {'H': 0, 'M': 0}
    not_listed = []  # stores experiments not listed in the requests file, *not sure if this should happen*
    for i in scheduled_experiments:
        if i in exp_priorities:
            if exp_priorities[i][0] == 'H':
                num_priorities['H'] += 1
            else:
                num_priorities['M'] += 1
        else:
            print(i, end="")
    print()
    return num_priorities


def output_fitness(exp_priorities, num_priorities, scheduled_experiments):
    print("-" * 200)
    print("OVERVIEW OF SCHEDULE FITNESS")
    print("-" * 200)
    print("Experiments Scheduled: " + str(len(scheduled_experiments)))
    print("Beam requests satisfied: %d/%d, %d%%"
          % (len(scheduled_experiments), len(exp_priorities), (100*len(scheduled_experiments)/len(exp_priorities))))
    print("There are %d high priority experiment(s) and %d medium priority experiment(s) scheduled."
          % (num_priorities['H'], num_priorities['M'],))
    print("High Priority Experiments / Total Experiments: %d/%d, %d%%"
          % (num_priorities['H'], len(scheduled_experiments), (100*num_priorities['H']/(len(scheduled_experiments)))))


if __name__ == "__main__":
    main()
