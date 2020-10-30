"""
FitnessChecker.py - WIP (REQUIRES MORE COMMENTS/Refactoring)
Author: Kevin Dabu

a program to read excel files using pandas, containing methods to check the fitness parameters of a schedule

NOTE: the column headings in the schedule excel files start at row 1 which is
the row that contains 'Cyclotron', 'BL2A', 'ISAC' etc.. so the values/axes in pandas
include the actual column headings: 'Data', 'Exp. #', 'Facility' etc...
THIS IS NOT THE SAME FOR THE REQUESTS
"""

from Schedule import Schedule
from Request import Request
from ScheduleManager import ScheduleManager
import FileManager as fm


def run_check():
    """Main function"""
    # defines ScheduleManager Class
    sm = ScheduleManager('Schedules')

    # Grabs all files in Schedules Directory
    schedule_files = fm.get_files('Schedules')

    # Grabs all files in the Requests Directory
    request_file = fm.get_files('Requests')

    for i in range(len(schedule_files)):

        # assign the excel data frame to respective variable
        schedule = fm.read_file('Schedules', schedule_files[i])
        request = fm.read_file('Requests', request_file[0])

        sm.add_schedule(Schedule(schedule_files[i].replace('.xlsx', ''), schedule))
        schedule = sm.schedules[i]
        request = Request(request_file[0], request)

        # Find schedule attributes
        schedule.set_priorities(check_priorities(schedule.experiments, request.experiments))
        schedule.set_fields(check_fields(schedule.experiments, request.experiments))
        schedule.set_acc(check_acc(schedule.experiments, request.experiments))

        # Fitness checks
        schedule.set_fitness(calculate_total_fitness(request, schedule))

        # Generates output
        schedule.set_output(output_fitness(schedule_files[i].replace('.xlsx', ''),
                            request.experiments, schedule.priorities, schedule.experiments,
                            schedule.fields, schedule.parameters['fields'], schedule.acc,
                            schedule.parameters['acc'], schedule.facilities, request.facilities, schedule.fitness))

    # sorts the schedules in the schedule manager by fitness values
    sm.sort_by_fitness()

    for schedule in sm.schedules[:5]:
         fm.write_fitness(schedule.output, schedule.file_name)


def calculate_total_fitness(request, schedule):
    """Calculates the total fitness using the formula given, sets each parameter to a dictionary in the schedule obj"""
    total_exp = (6 * len(schedule.experiments)) / schedule.shifts
    priority = schedule.priorities['H'] / len(schedule.experiments)
    s_exp_vs_r_exp = len(schedule.experiments) / len(request.experiments)
    fields = find_balance(schedule.fields, 'field')
    acc = find_balance(schedule.acc, 'acc')
    s_fac_vs_r_fac = len(schedule.facilities) / len(request.facilities)

    schedule.set_fitness_parameters(total_exp, priority, s_exp_vs_r_exp,
                                    fields, acc, s_fac_vs_r_fac)
    fitness = 1
    for key in schedule.parameters:
        fitness *= schedule.parameters[key]
    return fitness


def check_priorities(scheduled_experiments: set, exp_priorities: dict) -> object:
    """Checks the priority of the scheduled experiments returns the number of H or M and experiments not listed"""
    num_priorities = {'H': 0, 'M': 0}
    for exp in scheduled_experiments:
        if exp in exp_priorities:
            if exp_priorities[exp][0] == 'H':
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


def find_balance(schedule, use_case):
    """Finds the balance of acc areas used or fields used, desired fractions: LEBT = 50%, MEBT = 25%, SEBT = 25%"""
    if use_case == 'acc':
        total_acc = schedule['LEBT'] + schedule['MEBT'] + schedule['SEBT']
        deltas = [(schedule['LEBT'] / total_acc - 0.5), (schedule['MEBT'] / total_acc - 0.25),
                  (schedule['SEBT'] / total_acc - 0.25)]

        for i in range(len(deltas)):
            if deltas[i] < 0:
                deltas[i] *= -1
        product = (1-deltas[0])*(1-deltas[1])*(1-deltas[2])
        return product

    elif use_case == 'field':
        old_fields = fm.read_data('fields.csv', 'field')
        total_fields_past = old_fields['ASTRO'] + old_fields['STRUC'] + old_fields['FSYMM']
        total_fields_current = schedule['ASTRO'] + schedule['FSYMM'] + schedule['STRUC']
        deltas = [(schedule['ASTRO'] / total_fields_current - old_fields['ASTRO'] / total_fields_past),
                  (schedule['FSYMM'] / total_fields_current - old_fields['FSYMM'] / total_fields_past),
                  (schedule['STRUC'] / total_fields_current - old_fields['STRUC'] / total_fields_past)]

        for i in range(len(deltas)):
            if deltas[i] < 0:
                deltas[i] *= -1
        product = (1-deltas[0])*(1-deltas[1])*(1-deltas[2])
        return product


def update_data(exps: set, fields: dict) -> None:
    """
    This should only be ran when an experiment meets required fitness levels,
    and is chosen as a schedule to be used - WIP
    """
    old_exp = fm.read_data('past_experiments.csv', 'exp')
    old_fields = fm.read_data('fields.csv', 'field')

    for exp in exps:
        old_exp.add(exp)

    for key in fields:
        old_fields[key] += fields[key]

    fm.save_data(old_exp, 'past_experiments.csv')
    fm.save_data(old_fields, 'fields.csv')


def output_fitness(filename, exp_requested, num_priorities, scheduled_experiments,
                   schedule_fields, field_fitness, schedule_acc, acc_fitness,
                   schedule_facilities, request_facilities, total_fitness):
    """Outputs fitness values to the console, TODO Make this look better...."""
    text = "%s\nFITNESS OVERVIEW: %s\n%s\nParameter 1: Total Experiments\nExperiments Scheduled: %d\n" %\
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
    text += "\nTOTAL FITNESS: %0.2f" % total_fitness
    return text


if __name__ == "__main__":
    run_check()
