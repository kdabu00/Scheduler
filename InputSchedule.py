"""
InputSchedule.py
Author: Kevin Dabu
Just a basic way to read excel files
*Displayed output was only to check if it was working*
WIP - This works assuming you have the file in your User/Documents folder
"""

import getpass
import os.path
import string
import pandas as pd

FILE_NAME = "Schedule 138 Ancestor.xlsx"


"""Might use this function later to help find file, not needed rn"""
# def find(fname:string, path:string):
#     """Finds first file matching the fname inside of a directory"""
#     for root, dirs, files in os.walk(path):
#         if fname in files:
#             return os.path.join(root, fname)


def open_file(path:string) -> None:
    """Open excel schedule, displays contents turns excel file into a data frame: schedule"""
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    schedule = pd.read_excel(path)
    print(schedule.head())  # take out .head() to display all contents
    print("\n" + "*"*100)
    for i in range(6):
        print()
        for k in range(6):
            print(schedule.values[k][i])  # first index: row, second index: column [0][0] == 'Date'

    # Now that we know the format we can use the values within the excel file


if __name__ == "__main__":
    # gets the current logged in user's name
    user = getpass.getuser()
    # I placed my excel file in C:\Users\USERNAME\Documents depending on where the file is *change*
    path = os.path.join("C:\\Users", user, "Documents", FILE_NAME)
    open_file(path)
