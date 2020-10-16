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
    scheduled_experiments, schedule_facilities = get_unique_experiments(schedule)
    exp_priorities, request_facilities = get_experiments_requested(requests)
    num_priorities = check_priorities(scheduled_experiments, exp_priorities)

    schedule_fields = check_fields(scheduled_experiments, exp_priorities)

    schedule_acc = check_acc(scheduled_experiments, exp_priorities)

    # Call output function to display fitness
    output_fitness(exp_priorities, num_priorities, scheduled_experiments,
                   schedule_fields, schedule_acc, schedule_facilities, request_facilities)


def get_unique_experiments(schedule: object) -> set:
    """Finds the number of different scheduled experiments, returns these experiments, along with a set of different
    facilities scheduled
    """
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

    # Check the total amount of different facilities
    facilities = set(schedule['I_Facility'].tolist())

    # Make a list of each row with ISAC experiment #, Facility, Beam, Target, and Source
    unique_exp = schedule[['I_Exp.#', 'I_Facility', 'I_Beam', 'I_Tgt', 'I_Source']].values.tolist()

    scheduled_exp = set()
    # Store each experiment as a tuple inside of a set
    for exp in unique_exp:
        scheduled_exp.add(tuple(exp))
    return scheduled_exp, facilities


def get_experiments_requested(requests: object) -> dict:
    """Creates a dictionary with experiments as key, and priority & field as value, returns the dictionary along with a
    set of different facilities requested
    """
    # Check if a request is an ISAC experiment and if the Experiment # is Test
    unique_exp = requests.loc[(requests['Beam options'] == 'ISAC Target (RIB)') & (requests['Experiment'] != 'Test')]
    # Put all priorities, fields, accelerator areas in their own lists
    priority = unique_exp['Priority'].tolist()
    field = unique_exp['Field'].tolist()
    acc = unique_exp['Acc Area'].tolist()
    # Create a set of unique facilities scheduled
    facilities = set(unique_exp['Facility'].tolist())
    # change nan values into empty string
    unique_exp = unique_exp.fillna('')
    # Create a list of unique experiments with values Experiment, Facility, Beam, Target, and Ion Source
    unique_exp = unique_exp[['Experiment', 'Facility', 'Beam', 'Target', 'Ion Source']].values.tolist()
    exp_priorities = {}
    for i in range(len(unique_exp)):
        # Turn each experiment into a tuple that will be used to ID unique experiments
        exp_priorities[tuple(unique_exp[i])] = [priority[i], field[i], acc[i]]
    return exp_priorities, facilities


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
    #     else:
    #         print(i, end="")
    # print()
    return num_priorities


def check_fields(scheduled_experiments: set, exp_fields: dict) -> object:
    """Checks the # of fields scheduled"""
    num_fields = {'ASTRO': 0, 'FSYMM': 0, 'STRUC': 0, 'LS': 0}
    for i in scheduled_experiments:
        if i in exp_fields:
            if exp_fields[i][1] == 'ASTRO':
                num_fields['ASTRO'] += 1
            elif exp_fields[i][1] == 'FSYMM':
                num_fields['FSYMM'] += 1
            elif exp_fields[i][1] == 'STRUC':
                num_fields['STRUC'] += 1
            elif exp_fields[i][1] == 'Life Science':
                num_fields['LS'] += 1
    #     else:
    #         print(i, end="")
    # print()
    return num_fields


def check_acc(scheduled_experiments: set, exp_acc: dict) -> object:
    """Checks the # of Accelerator Areas scheduled"""
    num_acc = {'LEBT': 0, 'MEBT': 0, 'SEBT': 0}
    for i in scheduled_experiments:
        if i in exp_acc:
            if exp_acc[i][2] == 'LEBT':
                num_acc['LEBT'] += 1
            elif exp_acc[i][2] == 'MEBT':
                num_acc['MEBT'] += 1
            else:
                num_acc['SEBT'] += 1
    #     else:
    #         print(i, end="")
    # print()
    return num_acc


def output_fitness(exp_priorities, num_priorities, scheduled_experiments,
                   schedule_fields, schedule_acc, schedule_facilities, request_facilities):
    print("-" * 200)
    print("OVERVIEW OF SCHEDULE FITNESS")
    print("-" * 200)
    print('Parameter 1')
    print("Experiments Scheduled: %d\n" % len(scheduled_experiments))
    print('Parameter 2')
    print("Beam requests satisfied: %d/%d, %0.2f\n"
          % (len(scheduled_experiments), len(exp_priorities), (len(scheduled_experiments)/len(exp_priorities))))
    print('Parameter 3:')
    print("There are %d high priority experiment(s) and %d medium priority experiment(s) scheduled."
          % (num_priorities['H'], num_priorities['M'],))
    print("High Priority Experiments / Total Experiments: %d/%d, %0.2f\n"
          % (num_priorities['H'], len(scheduled_experiments), (num_priorities['H']/(len(scheduled_experiments)))))
    print('Parameter 4: - WIP')
    print('Fields Scheduled: - TODO equation to find final product\nASTRO: %d\nFSYMM: %d\nSTRUC: %d\n'
          % (schedule_fields['ASTRO'], schedule_fields['FSYMM'], schedule_fields['STRUC']))
    print('Parameter 5: - WIP')
    print('Accelerator Areas Scheduled: - TODO equation to find final product\nLEBT: %d\nMEBT: %d\nSEBT: %d\n'
          % (schedule_acc['LEBT'], schedule_acc['MEBT'], schedule_acc['SEBT']))
    print('Parameter 6:')
    print("There are %d different facilities scheduled out of %d, %0.2f\n"
          % (len(schedule_facilities), len(request_facilities), (len(schedule_facilities)/len(request_facilities))))
    print('Parameter 7: - WIP')  # BALANCE BETWEEN OLD AND NEW EXPERIMENTS TODO


if __name__ == "__main__":
    main()
