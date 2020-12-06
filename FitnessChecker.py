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
import constraint as c

"""
   p1 = Total Experiments
   p2 = High Priority vs Experiments Scheduled
   p3 = Fraction of Beam Requests Satisfied
   p4 = Balance of Research Fields
   p5 = Balance of Accelerator Areas
   p6 = Diversity of Facilities
"""

p1 = True
p2 = True
p3 = True
p4 = True
p5 = True
p6 = True


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
        print(c.run_check(schedule)[0])
        # Find schedule attributes

        schedule.set_priorities(check_priorities(schedule.experiments, request.experiments))
        schedule.set_fields(check_fields(schedule.experiments, request.experiments))
        schedule.set_acc(check_acc(schedule.experiments, request.experiments))

        # Fitness checks
        output = calculate_total_fitness(request, schedule)
        schedule.set_fitness(output[0])

        # Generates output
        schedule.set_output(output[1])

    # sorts the schedules in the schedule manager by fitness values
    sm.sort_by_fitness()

    for schedule in sm.schedules[:]:
        fm.write_fitness(schedule.output, schedule.file_name)


def calculate_total_fitness(request, schedule):
    """Calculates the total fitness using the formula given, sets each parameter to a dictionary in the schedule obj"""

    total_exp = None
    priority = None
    s_exp_vs_r_exp = None
    fields = None
    acc = None
    s_fac_vs_r_fac = None

    text = "%s\nFITNESS OVERVIEW: %s\n%s" % (('-' * 60), schedule.file_name, ('-' * 60))

    if p1:
        total_exp = (6 * len(schedule.experiments)) / schedule.shifts
        text += "\nParameter 1: Total Experiments\nExperiments Scheduled: %d\n" % len(schedule.experiments)
    if p2:
        priority = schedule.priorities['H'] / len(schedule.experiments)
        text += "\nParameter 2: High Priority vs Scheduled Experiments\nH: %d Scheduled: %d" % (schedule.priorities['H'], len(schedule.experiments))
        text += " Fitness: %0.2f\n" % priority
    if p3:
        s_exp_vs_r_exp = len(schedule.experiments) / len(request.experiments)
        text += "\nParameter 3: Fraction of Beam Requests Satisfied\n"
        text += "Beam requests satisfied: %d/%d, Fitness: %0.2f\n" % (len(schedule.experiments), len(request.experiments), s_exp_vs_r_exp)
    if p4:
        fields = find_balance(schedule.fields, 'field')
        text += "\nParameter 4: Balance of Research Fields\nFields Scheduled:"
        text += "ASTRO: %d, FSYMM: %d, STRUC: %d\nFitness: %0.2f\n" % (schedule.fields['ASTRO'], schedule.fields['FSYMM'], schedule.fields['STRUC'], fields)
    if p5:
        acc = find_balance(schedule.acc, 'acc')
        text += "\nParameter 5: Balance of Accelerator Areas\nAccelerator Areas Scheduled:"
        text += "LEBT: %d, MEBT: %d, SEBT: %d\nFitness: %0.2f\n" % (schedule.acc['LEBT'], schedule.acc['MEBT'], schedule.acc['SEBT'], acc)
    if p6:
        s_fac_vs_r_fac = len(schedule.facilities) / len(request.facilities)
        text += "\nParameter 6: Diversity of Facilities\n"
        text += "Different Facilities: %d  Total Facilities: %d, Fitness: %0.2f\n" % (len(schedule.facilities), len(request.facilities), s_fac_vs_r_fac)

    schedule.set_fitness_parameters(total_exp=total_exp, priority=priority, requests=s_exp_vs_r_exp,
                                    fields=fields, acc=acc, fac=s_fac_vs_r_fac)
    fitness = 1
    for key in schedule.parameters:
        if schedule.parameters[key] is not None:
            fitness *= schedule.parameters[key]
    text += "\nTOTAL FITNESS: %0.2f" % fitness

    return fitness, text


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
        product = (1 - deltas[0]) * (1 - deltas[1]) * (1 - deltas[2])
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
        product = (1 - deltas[0]) * (1 - deltas[1]) * (1 - deltas[2])
        return product


def update_fields(fields: dict) -> None:
    """
    This should only be ran when an experiment meets required fitness levels,
    and is chosen as a schedule to be used - WIP
    """
    old_fields = fm.read_data('fields.csv', 'field')
    for key in fields:
        old_fields[key] += fields[key]
    fm.save_data(old_fields, 'fields.csv')


if __name__ == "__main__":
    run_check()
