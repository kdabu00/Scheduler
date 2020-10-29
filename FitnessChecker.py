"""
FitnessChecker.py - WIP (REQUIRES MORE COMMENTS/Refactoring)
Author: Kevin Dabu

a program to read excel files using pandas, containing methods to check the fitness parameters of a schedule

NOTE: the column headings in the schedule excel files start at row 1 which is
the row that contains 'Cyclotron', 'BL2A', 'ISAC' etc.. so the values/axes in pandas
include the actual column headings: 'Data', 'Exp. #', 'Facility' etc...
THIS IS NOT THE SAME FOR THE REQUESTS
"""

import os
import FileManager as fm
from typing import List


def main():
    """Main function"""
    # gets the current logged in user's name

    schedule_files = [f for f in os.listdir(os.path.join(os.getcwd(), 'Schedules'))
                                  if os.path.isfile(os.path.join(os.getcwd(), 'Schedules', f))]
    request_file = [f for f in os.listdir(os.path.join(os.getcwd(), 'Requests'))
                                  if os.path.isfile(os.path.join(os.getcwd(), 'Requests', f))]

    # keeps track of fitness of each schedule
    fitness_dict = {}

    for schedule_name in schedule_files:
        # assign the excel data frame to respective variable
        schedule = fm.read_file(os.path.join(os.getcwd(), 'Schedules', schedule_name))
        requests = fm.read_file(os.path.join(os.getcwd(), 'Requests', request_file[0]))

        # Find unique scheduled experiments and requested experiments w/priorities
        schedule_experiments, schedule_facilities = get_unique_experiments(schedule)

        # Find total shifts
        total_shifts = get_total_available_shifts(schedule)

        # Fitness checks
        exp_requested, request_facilities = get_experiments_requested(requests)
        num_priorities = check_priorities(schedule_experiments, exp_requested)
        schedule_fields = check_fields(schedule_experiments, exp_requested)
        schedule_acc = check_acc(schedule_experiments, exp_requested)
        new_exps = check_new(schedule_experiments)

        acc_fitness = find_balance(schedule_acc, 'acc')
        field_fitness = find_balance(schedule_fields, 'field')
        time_fitness = find_balance(schedule_experiments, 'old_new')

        total_fitness = calculate_total_fitness(schedule_experiments, exp_requested, num_priorities, schedule_facilities,
                                request_facilities, field_fitness, acc_fitness, time_fitness, total_shifts)

        text = output_fitness(schedule_name.replace('.xlsx', ''), exp_requested, num_priorities, schedule_experiments,
                       schedule_fields, field_fitness, schedule_acc, acc_fitness,
                       schedule_facilities, request_facilities, new_exps, time_fitness, total_fitness)

        fitness_dict[schedule_name.replace('.xlsx', '')] = [total_fitness, text, schedule_experiments, schedule_fields]

    # takes top 5 schedules!
    fitness_dict = {k: v for k, v in sorted(fitness_dict.items(), key=lambda item: item[1][0], reverse=True)[:5]}
    print("Test to see if fitness is sorted properly")
    for schedule in fitness_dict:
        fm.write_fitness(fitness_dict[schedule][1], schedule + ".xlsx")
        print(schedule + ': ', fitness_dict[schedule][0])

    # When a schedule is selected? not quite sure how yet update data stored in csv files
    # update_data(fitness_dict[schedule_name][2], fitness_dict[schedule_name][3])


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
    # Make a list of each row with ISAC experiment #, Facility, Target, and Source
    unique_exp = schedule[['I_Exp.#', 'I_Facility', 'I_Tgt', 'I_Source']].values.tolist()
    scheduled_exp = set()
    # Store each experiment as a tuple inside of a set
    for exp in unique_exp:
        scheduled_exp.add(tuple(exp))
    return scheduled_exp, facilities


def get_total_available_shifts(schedule: object):
    # Rename the column names to the appropriate values
    schedule.columns = ['Date', 'Shift', 'Cyclotron_Offline', 'current(uA)', 'BL2A_Offline',
                        'I_Exp.#', 'I_Facility', 'I_Note', 'I_West/East', 'I_Beam', 'I_Energy (keV)', 'I_Tgt',
                        'I_Source', 'I_Mod',
                        'O_Exp.#', 'O_Facility', 'O_Note', 'O_Beam', 'O_Energy (keV)', 'O_Source', 'O_Offline']
    # drop all rows in dataframe that had the values of index 0/row 2 in excel file
    schedule = schedule.drop(schedule.index[0])
    # Change nan values into empty string
    schedule = schedule.fillna('')
    schedule = schedule.loc[(schedule['Cyclotron_Offline'] != 'Shutdown') & (schedule['Cyclotron_Offline'] != 'Maintenance') &
                            (schedule['Cyclotron_Offline'] != 'Beam Development') & (schedule['Cyclotron_Offline'] != 'Mini Shutdown') &
                            (schedule['BL2A_Offline'] != 'Maintenance') & (schedule['BL2A_Offline'] != 'Startup')]
    return schedule.index.size


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
    # Create a list of unique experiments with values Experiment, Facility, Target, and Ion Source
    unique_exp = unique_exp[['Experiment', 'Facility', 'Target', 'Ion Source']].values.tolist()
    exp_requested = {}
    for i in range(len(unique_exp)):
        # Turn each experiment into a tuple, this tuple will be used as a key
        # to find unique experiments and their values
        exp_requested[tuple(unique_exp[i])] = [priority[i], field[i], acc[i]]
    return exp_requested, facilities


def check_priorities(scheduled_experiments: set, exp_priorities: dict) -> object:
    """Checks the priority of the scheduled experiments returns the number of H or M and experiments not listed"""
    num_priorities = {'H': 0, 'M': 0}
    for i in scheduled_experiments:
        if i in exp_priorities:
            if exp_priorities[i][0] == 'H':
                num_priorities['H'] += 1
            else:
                num_priorities['M'] += 1
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
    return num_acc


def find_balance(schedule_obj, use_case):
    """Finds the balance of acc areas used or fields used, desired fractions: LEBT = 50%, MEBT = 25%, SEBT = 25%"""
    if use_case == 'acc':
        total_acc = schedule_obj['LEBT'] + schedule_obj['MEBT'] + schedule_obj['SEBT']
        deltas = [(schedule_obj['LEBT'] / total_acc - 0.5), (schedule_obj['MEBT'] / total_acc - 0.25),
                  (schedule_obj['SEBT'] / total_acc - 0.25)]
        for i in range(len(deltas)):
            if deltas[i] < 0:
                deltas[i] *= -1
        product = (1-deltas[0])*(1-deltas[1])*(1-deltas[2])
        return product
    elif use_case == 'field':
        old_fields = fm.read_data('fields.csv', 'field')
        total_fields_past = old_fields['ASTRO'] + old_fields['STRUC'] + old_fields['FSYMM']
        total_fields_current = schedule_obj['ASTRO'] + schedule_obj['FSYMM'] + schedule_obj['STRUC']
        deltas = [(schedule_obj['ASTRO'] / total_fields_current - old_fields['ASTRO'] / total_fields_past),
                  (schedule_obj['FSYMM'] / total_fields_current - old_fields['FSYMM'] / total_fields_past),
                  (schedule_obj['STRUC'] / total_fields_current - old_fields['STRUC'] / total_fields_past)]
        for i in range(len(deltas)):
            if deltas[i] < 0:
                deltas[i] *= -1
        product = (1-deltas[0])*(1-deltas[1])*(1-deltas[2])
        return product
    elif use_case == 'old_new':
        new_exp = check_new(schedule_obj)
        return new_exp/len(schedule_obj)
        # past_values = efm.read_data('old_new.csv', 'old_new')
        # past_totals = 0
        # past_new = 0
        # # add up all the total experiments from previous schedules
        # for val in past_values:
        #     past_totals += val[1]
        #     past_new += val[0]
        # current = check_new(schedule_obj)
        # current[0] += past_new
        # current[1] += past_new


def check_new(schedule_exp: set) -> List:
    old_exp = fm.read_data('past_experiments.csv', 'exp')
    new_exp = 0
    for exp in schedule_exp:
        if exp not in old_exp:
            new_exp += 1
    return new_exp


def update_data(exps: set, fields: dict) -> None:
    """This should only be ran when an experiment meets required fitness levels, and is chosen as a schedule to be used"""
    old_exp = fm.read_data('past_experiments.csv', 'exp')
    old_fields = fm.read_data('fields.csv', 'field')
    # old_new = efm.read_data('old_new.csv', 'old_new')
    # old_new.append(check_new(exps))

    for exp in exps:
        old_exp.add(exp)

    for key in fields:
        old_fields[key] += fields[key]

    fm.save_data(old_exp, 'past_experiments.csv')
    fm.save_data(old_fields, 'fields.csv')
    # efm.save_data(old_new, 'old_new.csv')


def calculate_total_fitness(schedule_experiments, exp_requested, num_priorities, schedule_facilities,
                            request_facilities, field, acc, time, shifts):
    t = len(schedule_experiments)
    h = num_priorities['H'] / t
    req = t / len(exp_requested)
    d = len(schedule_facilities) / len(request_facilities)
    fitness = ((6*t/shifts) * h * req * field * acc * time * d)
    return fitness


def output_fitness(filename, exp_requested, num_priorities, scheduled_experiments,
                   schedule_fields, field_fitness, schedule_acc, acc_fitness,
                   schedule_facilities, request_facilities, new_exps, old_new_fitness, total_fitness):
    """Outputs fitness values to the console, TODO Make this look better...."""
    text = ''
    text += "%s\nFITNESS OVERVIEW: %s\n%s\nParameter 1: Total Experiments\nExperiments Scheduled: %d\n" %\
            (('-' * 60), filename, ('-' * 60), len(scheduled_experiments))
    text += "\nParameter 2: High-Priority vs Experiments Scheduled\nThere are %d high priority experiment(s) " %\
            num_priorities['H']
    text += "and %d medium priority experiment(s) scheduled.\n" % num_priorities['M']
    text += "High Priority Experiments / Total Experiments: %d/%d, Fitness: %0.2f\n" %\
            (num_priorities['H'], len(scheduled_experiments), (num_priorities['H']/len(scheduled_experiments)))
    text += "\nParameter 3: Fraction of Beam Requests Satisfied\nBeam requests satisfied: "
    text += "%d/%d, Fitness: %0.2f\n\nParameter 4: Balance of Research Fields\n" %\
            (len(scheduled_experiments), len(exp_requested), (len(scheduled_experiments) / len(exp_requested)))
    text += "Fields Scheduled:\nASTRO: %d\nFSYMM: %d\nSTRUC: %d" %\
            (schedule_fields['ASTRO'], schedule_fields['FSYMM'], schedule_fields['STRUC'])
    text += "\nFitness: %0.2f\n\nParameter 5: Balance of Accelerator" %\
            field_fitness
    text += " Areas\nAccelerator Areas Scheduled:\nLEBT: %d\nMEBT: %d\nSEBT: %d" %\
            (schedule_acc['LEBT'], schedule_acc['MEBT'], schedule_acc['SEBT'])
    text += "\nFitness: %0.2f\n\nParameter 6: Diversity of Facilities\n" %\
            acc_fitness
    text += "There are %d different facilities scheduled out of %d, Fitness: %0.2f\n" %\
            (len(schedule_facilities), len(request_facilities), (len(schedule_facilities)/len(request_facilities)))
    text += "\nParameter 7: Balance Between Old and New Experiments\nTotal new experiments: %d\n" %\
            new_exps
    text += "Fitness: %0.2f\n\nTOTAL FITNESS: %0.2f" % (old_new_fitness, total_fitness)
    return text


if __name__ == "__main__":
    main()
