"""
Schedule.py
Author: Kevin Dabu
Date: OCT.29 2020
This file contains the basic methods and attributes of a schedule for the TRIUMF Scheduler
Refactors each schedule inputted to have proper column values to be able to read them using pandas functions
"""
import pandas as pd
import FileManager as fm
# Ignores setting with copy warning
pd.options.mode.chained_assignment = None


class Schedule:

    def __init__(self, name, schedule):
        """Creates an object instance of the schedule class"""
        self.name = name
        self.schedule = refactor_schedule(schedule)
        self.priorities = None
        self.fields = None
        self.acc = None
        self.output = None
        self.fitness = None
        self.parameters = None
        self.is_valid = False

    @property
    def file_name(self):
        return self.name + ".xlsx"

    @property
    def experiments(self):
        """Finds the number of different scheduled experiments, returns these experiments"""
        # Ignores values in Exp. # that are equal to Exp. #,
        # Test, Setup or empty, IGNORING Experiment S2000 *Filler exp*
        self.schedule = self.schedule.loc[(self.schedule['I_Exp.#'] != '') & (self.schedule['I_Exp.#'] != 'TEST')
                                          & (self.schedule['I_Exp.#'] != 'SETUP') & (
                                                      self.schedule['I_Exp.#'] != 'S2000')]

        # Make a list of each row with ISAC experiment #, Facility, Target, and Source
        unique_exp = self.schedule[['I_Exp.#', 'I_Facility', 'I_Tgt', 'I_Source']].values.tolist()
        scheduled_exp = set()
        # Store each experiment as a tuple inside of a set
        for exp in unique_exp:
            scheduled_exp.add(tuple(exp))
        return scheduled_exp

    @property
    def facilities(self):
        """Returns all ISAC facilities and amount of times they are scheduled"""
        self.schedule = self.schedule.loc[(self.schedule['I_Exp.#'] != '') & (self.schedule['I_Exp.#'] != 'TEST')
                                          & (self.schedule['I_Exp.#'] != 'SETUP') & (
                                                      self.schedule['I_Exp.#'] != 'S2000')]
        facilities = set(self.schedule['I_Facility'].tolist())
        return facilities

    @property
    def shifts(self):
        """Returns all available shifts"""
        self.schedule = self.schedule.loc[
            (self.schedule['Cyclotron_Offline'] != 'Shutdown') & (self.schedule['Cyclotron_Offline'] != 'Maintenance') &
            (self.schedule['Cyclotron_Offline'] != 'Beam Development') & (
                        self.schedule['Cyclotron_Offline'] != 'Mini Shutdown') &
            (self.schedule['BL2A_Offline'] != 'Maintenance') & (self.schedule['BL2A_Offline'] != 'Startup')]
        return self.schedule.index.size

    @property
    def isvalid(self):
        return self.is_valid

    @property
    def date(self):
        return self.schedule['Date'].tolist()

    @property
    def target(self):
        return self.schedule['I_Tgt'].tolist()

    @property
    def source(self):
        return self.schedule['I_Source'].tolist()

    @property
    def module(self):
        return self.schedule['I_Mod'].tolist()

    @property
    def station(self):
        return self.schedule['I_West/East'].tolist()

    @property
    def shift(self):
        return self.schedule['Shift'].tolist()

    @property
    def size(self):
        size = len(self.schedule.index)
        return size

    def set_fitness_parameters(self, total_exp, priority, requests, fields, acc, fac):
        self.parameters = {'total_exp': total_exp,
                           'priority': priority,
                           'requests': requests,
                           'fields': fields,
                           'acc': acc,
                           'fac': fac}

    def set_priorities(self, var):
        self.priorities = var

    def set_fields(self, var):
        self.fields = var

    def set_acc(self, var):
        self.acc = var

    def set_output(self, var):
        self.output = var

    def validate(self):
        """Changes is_valid to true"""
        self.is_valid = True

    def set_fitness(self, var):
        self.fitness = var

    def update_fields(self) -> None:
        """
        This should only be ran when an experiment meets required fitness levels,
        and is chosen as a schedule to be used - WIP
        """
        old_fields = fm.read_data('fields.csv', 'field')
        for key in self.fields:
            old_fields[key] += self.fields[key]
        fm.save_data(old_fields, 'fields.csv')

    def __repr__(self):
        return self.name


def refactor_schedule(schedule):
    """Adjusts schedule columns to proper titles, ignores empty cells,
    fixes SIS/RILIS to just RILIS, changes Source, Facility, Exp.# and Tgt values to upper case"""
    # Rename the column names to the appropriate values
    schedule.columns = ['Date', 'Shift', 'Cyclotron_Offline', 'current(uA)', 'BL2A_Offline',
                        'I_Exp.#', 'I_Facility', 'I_Note', 'I_West/East', 'I_Beam', 'I_Energy (keV)', 'I_Tgt',
                        'I_Source', 'I_Mod',
                        'O_Exp.#', 'O_Facility', 'O_Note', 'O_Beam', 'O_Energy (keV)', 'O_Source', 'O_Offline']
    # drop all rows in dataframe that had the values of index 0/row 2 in excel file
    schedule = schedule.drop(schedule.index[0])
    # Change nan values into empty string
    schedule = schedule.fillna('')
    # Change SIS/RILIS to just RILIS
    schedule['I_Source'] = schedule['I_Source'].replace(['SIS/RILIS'], 'RILIS')
    schedule.loc[:, 'I_Source'] = schedule.loc[:, 'I_Source'].str.upper()
    schedule.loc[:, 'I_Facility'] = schedule.loc[:, 'I_Facility'].str.upper()
    schedule.loc[:, 'I_Exp.#'] = schedule.loc[:, 'I_Exp.#'].str.upper()
    schedule.loc[:, 'I_Tgt'] = schedule.loc[:, 'I_Tgt'].str.upper()
    # Strip trailing and leading whitespace from facility column
    schedule['I_Facility'] = schedule['I_Facility'].str.strip()
    return schedule
