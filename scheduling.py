import getpass
import os.path
import pandas as pd
import datetime
import calendar

def main():
    """Main function"""

    # gets the current logged in user's name
    user = getpass.getuser()

    # Grabs filename input from user
    requests_name = ask_file_names()

    # I placed my excel files in C:\Users\USERNAME\Documents. Note: depending on where the file is *change*
    requests_path = os.path.join("C:\\Users", user, "Documents", requests_name)

    # assign the excel data frame to schedule variable
    requests = read_file(requests_path)
    row14_requested_shift = get_required_shifts(requests,14)
    # Outputs - Will probably be made into a separate function and saved for future use
    print("-" * 100)
    print("OVERVIEW OF REQUEST")
    print("-" * 100)
    print(row14_requested_shift)

def read_file(path: str) -> object:
    """Open excel requests, displays contents turns excel file into a data frame: requests"""
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    excel_file = pd.read_excel(path)  # first index: row, second index: column ex. schedule.values[0][0] == 'Date'
    return excel_file


def ask_file_names() -> object:
    """Prompts user for file names for requests and schedules, then returns them"""
    requests_name = input("Input requests file name (Schedule 138 Beam Requests.xlsx): ")
    return requests_name

def get_expirment_from_isac(requests: object):
    """"""
    return
    
def get_required_shifts(requests: object, row_number):
    required_shifts = requests.values[row_number-2][4]    
    return required_shifts 

def set_ts_tm(requests: object):
    return

if __name__ == "__main__":
    main()