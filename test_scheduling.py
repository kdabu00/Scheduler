"""
test_scheduling.py
Schedule generation

testing out methods to modify the ancestor schedule to create new schedules based off of it. Then will make mutations as
planned.
Author: Kevin Dabu

TODO: Make modular, move code from main to own separate functions, finalize the generation, fix the rest of the code..
"""
from Request import Request
import FileManager as fm
from ScheduleManager import ScheduleManager
from Schedule import Schedule
import pandas as pd


def main():
    sm = ScheduleManager('Schedules')

    # Grabs ancestor schedule
    ancestor_file = fm.get_files('Ancestor')

    # Grabs requests file
    request_file = fm.get_files('Requests')

    # Read excels as dataframes
    ancestor = fm.read_file('Ancestor', ancestor_file[0])
    request = fm.read_file('Requests', request_file[0])

    # Assign to Schedule and Request Objects
    request = Request(request_file[0], request)

    schedule = Schedule(ancestor_file[0], ancestor)

    # uses find_exp_shifts to get the shifts in the schedule for each experiment, used in the commented code below
    schedule_shifts = find_exp_shifts(schedule.schedule)

    """This code compares the shifts of each experiment in the request to the ones in the schedule, I figured out it
     wont work because each Target block needs the same target..."""
    # print('Requested                         Scheduled')
    # for req_exp in request.experiments:
    #     for exp in schedule_shifts:
    #         if request.experiments[req_exp][3] == schedule_shifts[exp]:
    #             print(req_exp, request.experiments[req_exp][3], exp, schedule_shifts[exp])
    #             # req_exp.pop('key', None)

    """Finds the index of the Startup before each new target block, used to find the beginning of each block"""
    startups = schedule.schedule[['BL2A_Offline', 'Date']][(schedule.schedule['BL2A_Offline'] == 'Startup') & (schedule.schedule['Cyclotron_Offline'] != 'Shutdown')]
    startups = startups.index.values.tolist()
    for index in startups:
        if index + 1 in startups:
            startups.remove(index)
    print(startups)

    new_schedule = schedule.schedule[['BL2A_Offline', 'I_Exp.#', 'I_Facility', 'I_Tgt', 'I_Source']]
    # This is a test value, that uses the indexes from startup, Index 86 is the first startup,
    # Index 152 is the startup after the block. By subtracting the last index by 1 (152 - 1) you get the all the
    # experiments in the target block ex. [startups[0]:(startups[1] - 1)]
    tb_1 = new_schedule.iloc[86:151].values.tolist()
    # len(tb_1) is the total amount of shifts in the target block
    max = len(tb_1)
    # Target Dictionary
    tgt = {}
    tgt_exp = {}
    for req_exp in request.experiments:
        other_exp = {}
        # if target not in target dictionary
        if req_exp[2] not in tgt:
            # target equals shift amount
            tgt[req_exp[2]] = request.experiments[req_exp][3]
            tgt_exp[req_exp[2]] = [[req_exp, request.experiments[req_exp][3]]]
            # target shift amount is less than the target block size and adding another experiment
            # wont go over tb length
        elif tgt[req_exp[2]] < max \
            and tgt[req_exp[2]] + request.experiments[req_exp][3] <= max:
            # add shift amount to target
            tgt[req_exp[2]] += request.experiments[req_exp][3]
            tgt_exp[req_exp[2]].append([req_exp, request.experiments[req_exp][3]])

    # Finds the best fit out of all the Targets to be used in the block
    # Deletes the Targets that are not better
    best_fit = 0
    copy_tgt = list(tgt)
    for i in copy_tgt:
        if tgt[i] > best_fit:
            best_fit = tgt[i]
        else:
            tgt.pop(i, None)
            tgt_exp.pop(i, None)

    """This section below should be within a loop using the startups to find the start_index and loops to find the 
    values within the tgt_exp dictionary"""
    # index of the first startup indicating new target block, set as 86 for now, will be using the startups list later
    start_index = 86
    # finds the shift of the first experiment in with the target TA as TA was the best fit for this block (63/65)
    a = start_index + tgt_exp['TA'][0][1]
    # Sets the experiment from tgt_exp['TA'][0][0] which is L122 for
    new_schedule.loc[(start_index+1):a, 'I_Exp.#':'I_Source'] = tgt_exp['TA'][0][0]
    # move the starting index to the next point since the exp was only 5 shifts long (86 + 5) = 91,
    # the next starting index should be + 1
    start_index += (a + 1)
    # Testing to see the new dataframe and how it looks right now,
    # Need to change so we have all columns and rows not just exp.#, facility, tgt, source etc...
    pd.set_option('display.max_columns', None)
    pd.set_option('max_rows', None)
    print(new_schedule)

    """AFTER RUNNING THIS YOU WILL SEE SettingWithCopyWarning need to set up a try catch or something to ignore this
    Error as it doesnt effect the output.."""


def find_exp_shifts(schedule):
    """Finds the amount of shifts for each scheduled experiment"""
    schedule = schedule.loc[(schedule['I_Exp.#'] != '') & (schedule['I_Exp.#'] != 'TEST')
                            & (schedule['I_Exp.#'] != 'SETUP') & (schedule['I_Exp.#'] != 'S2000')]

    # Make a list of each row with ISAC experiment #, Facility, Target, and Source
    experiments = schedule[['I_Exp.#', 'I_Facility', 'I_Tgt', 'I_Source']]
    # Finds the amount of shifts for each expeiment
    experiments = experiments.groupby(['I_Exp.#', 'I_Facility', 'I_Tgt', 'I_Source']).size().reset_index(name='count')
    experiments = experiments.values

    e = {}
    # Add shifts for setup, if RILIS + 3 if not + 2
    for exp in experiments:
        if exp[3] == 'RILIS' or exp[3] == 'SIS/RILIS':
            e[tuple(exp[:4])] = exp[4] + 3
        else:
            e[tuple(exp[:4])] = exp[4] + 2
    return e


if __name__ == '__main__':
    main()
