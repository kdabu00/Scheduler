"""
FileManager.py
Author: Kevin Dabu
This is a program that uses the pandas Library to read/write/update excel files
and has a prompt for file names

WIP
"""

import pandas as pd
import csv
import os


def read_file(folder_name: str, file_name: str) -> object:
    """Open excel schedule, displays contents turns excel file into a data frame: schedule"""
    excel_file = pd.read_excel(os.path.join(os.getcwd(), folder_name, file_name))
    return excel_file


def get_files(folder_name: str) -> list:
    """Returns the names of all files within in a folder located in the program directory"""
    files = [f for f in os.listdir(os.path.join(os.getcwd(), folder_name))
             if os.path.isfile(os.path.join(os.getcwd(), folder_name, f))]
    return files


def save_data(data, filename):
    """Saves file to csv, with parameters for data to be saved and name for the file"""
    with open('C:\\Users\\kevin\\Documents\\' + filename, 'w', newline='') as out:
        csv_out = csv.writer(out)
        if filename == 'past_experiments.csv':
            for tup in data:
                csv_out.writerow(tup)
        elif filename == 'fields.csv':
            for key in data:
                csv_out.writerow((key, data[key]))


def read_data(filename, use):
    """Reads csv, depending on use either reads data into a set or reads data into a dictionary"""
    with open(os.path.join(os.getcwd(),  filename)) as csvfile:
        read_csv = csv.reader(csvfile, delimiter=',')
        if use == 'exp':
            data = set()
            for row in read_csv:
                data.add(tuple(row))
        elif use == 'field':
            data = {}
            for row in read_csv:
                data[row[0]] = int(row[1])
        return data


def write_fitness(text, filename):
    with open(os.path.join(os.getcwd(), 'Schedules', 'Fitness', filename + '_FITNESS.txt'), 'w') as the_file:
        the_file.write(text)
