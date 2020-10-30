"""
Schedule.py
Author: Kevin Dabu
Date: OCT.29 2020
This file contains the basic methods and attributes of a schedule for the TRIUMF Scheduler
- WIP
"""


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
        self.is_valid = False

    @property
    def file_name(self):
        return self.name + ".xlsx"

    @property
    def experiments(self):
        """Finds the number of different scheduled experiments, returns these experiments"""
        # Ignores values in Exp. # that are equal to Exp. #,
        # Test, Setup or empty, IGNORING Experiment S2000 *Filler exp*
        self.schedule = self.schedule.loc[(self.schedule['I_Exp.#'] != '') & (self.schedule['I_Exp.#'] != 'Test')
                                & (self.schedule['I_Exp.#'] != 'Setup') & (self.schedule['I_Exp.#'] != 'S2000')]

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
        self.schedule = self.schedule.loc[(self.schedule['I_Exp.#'] != '') & (self.schedule['I_Exp.#'] != 'Test')
                                & (self.schedule['I_Exp.#'] != 'Setup') & (self.schedule['I_Exp.#'] != 'S2000')]
        facilities = set(self.schedule['I_Facility'].tolist())
        return facilities

    @property
    def shifts(self):
        """Returns all available shifts"""
        self.schedule = self.schedule.loc[
            (self.schedule['Cyclotron_Offline'] != 'Shutdown') & (self.schedule['Cyclotron_Offline'] != 'Maintenance') &
            (self.schedule['Cyclotron_Offline'] != 'Beam Development') & (self.schedule['Cyclotron_Offline'] != 'Mini Shutdown') &
            (self.schedule['BL2A_Offline'] != 'Maintenance') & (self.schedule['BL2A_Offline'] != 'Startup')]
        return self.schedule.index.size

    @property
    def isvalid(self):
        return self.is_valid

    @property
    def total_experiments(self):
        """Returns the total amount of experiments in the schedule"""
        return len(self.experiments)

    @property
    def get_fitness_parameters(self):
        return {'priority': self.priorities,
                'fields': self.fields,
                'acc': self.acc,
                'exp': self.experiments,
                'facilities': self.facilities,
                'shifts': self.shifts}

    def set_priorities(self, var):
        self.priorities = var

    def set_fields(self, var):
        self.fields = var

    def set_acc(self, var):
        self.acc = var

    def set_output(self, var):
        self.output = var

    def validate(self):
        """Changes valid boolean attribute"""
        self.is_valid = True

    def set_fitness(self, var):
        self.fitness = var

    def __repr__(self):
        return self.name


def refactor_schedule(schedule):
    """Adjusts schedule columns to proper titles, ignores empty cells, fixes SIS/RILIS to just RILIS"""
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
    # Strip trailing and leading whitespace from facility column
    schedule['I_Facility'] = schedule['I_Facility'].str.strip()
    return schedule

