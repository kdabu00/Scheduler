"""
ScheduleManager.py
Author: Kevin Dabu
Date: Oct.29 2020
This class manages the schedules for the TRIUMF Scheduler
"""


class ScheduleManager:

    def __init__(self, name):
        """Creates an instance of a schedule manager"""
        self.name = name
        self.schedules = []

    def add_schedule(self, schedule):
        """Gets schedule names and adds it to the schedule manager"""
        self.schedules.append(schedule)

    def sort_by_fitness(self):
        """Sorts schedules in the ScheduleManager by fitness values"""
        self.schedules = sorted(self.schedules, key=lambda x: x.fitness, reverse=True)

