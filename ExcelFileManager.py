"""
ExcelFileManager.py
Author: Kevin Dabu
This is a program that uses the pandas Library to read/write/update excel files
and has a prompt for file names

WIP
"""

import pandas as pd


def read_file(path: str) -> object:
    """Open excel schedule, displays contents turns excel file into a data frame: schedule"""
    excel_file = pd.read_excel(path)  # first index: row, second index: column ex. schedule.values[0][0] == 'Date'
    return excel_file


def write_file():
    """Creates an excel file from a data frame"""
    pass


def update_file():
    """Updates an excel file's values"""
    pass


def ask_file_names() -> object:
    """Prompts user for file names for requests and schedules, then returns them"""
    schedule_name = input("Input schedule file name (Schedule 138 Ancestor.xlsx): ")
    requests_name = input("Input beam requests file (Schedule 138 Beam Requests.xlsx): ")
    return schedule_name, requests_name


"""Might use this function later to help find the files, not neccessary"""
# def find(fname:str, path:str):
#     """Finds first file matching the fname inside of a directory"""
#     for root, dirs, files in os.walk(path):
#         if fname in files:
#             return os.path.join(root, fname)

