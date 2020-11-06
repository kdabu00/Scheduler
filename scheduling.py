import getpass
import os.path
import pandas as pd
from datetime import datetime
import calendar
from Schedule import Schedule
from Request import Request
import FileManager as fm
import numpy as np
from random import random

def main():
    """Main function"""
    request_file = fm.get_files('Requests')
    requests = fm.read_file('Requests', request_file[0])
    requests = Request(request_file[0], requests)
    requests_sort_by_tb = requests.request.request_sort_by_tb
    # Outputs - Will probably be made into a separate function and saved for future use
    print("-" * 100)
    print("OVERVIEW OF REQUEST")
    print("-" * 100)
    print(requests_sort_by_tb)
    # write_to_excel(requests)
    
'''    
def get_required_shifts(requests: object, row_number):
    required_shifts = requests.values[row_number-2][4]    
    return required_shifts 
    request.required_shifts

def get_expirment_number(requests: object, row_number):
    exp_num = requests.values[row_number-2][0]
    return exp_num
    request.expirment_number

def sort_by_target_block(requests: object):
    """group by source then group by target type"""
    requests_sort_by_tb = requests.request.sort_values(by=['Ion Source', 'Target'])
    return requests_sort_by_tb
'''
def set_ts_tm():
    combo = "west2_east4"
    # combo = "west4_east2"
    random_num = random.randint(0, 1)
    if random_num == 0 and combo == "west2_east4":
        ts = "West"
        tm = 2
    elif random_num == 1 and combo == "west2_east4":
        ts = "East"
        tm = 4
    elif random_num == 0 and combo == "west4_east2":
        ts = "West"
        tm = 4
    elif random_num == 1 and combo == "west4_east2":
        ts = "East"
        tm = 2
    
    return ts,tm

def set_date(row_number):
    # year_now = datetime.datetime.now().year
    date_list = []
    if row_number == 1 or row_number == 2 or row_number == 3:
        string_2021 = "25/4/2021"
        string_2022 = "25/4/2022"
        string_2023 = "25/4/2023"
        string_2024 = "25/4/2024"
        string_2025 = "25/4/2025"
        string_2026 = "25/4/2026"
        string_2027 = "25/4/2027"
        string_2028 = "25/4/2028"
        string_2029 = "25/4/2029"
        string_2030 = "25/4/2030"
        date_2021 = datetime.strptime(string_2021, "%d/%m/%Y")
        date_2022 = datetime.strptime(string_2022, "%d/%m/%Y")
        date_2023 = datetime.strptime(string_2023, "%d/%m/%Y")
        date_2024 = datetime.strptime(string_2024, "%d/%m/%Y")
        date_2025 = datetime.strptime(string_2025, "%d/%m/%Y")
        date_2026 = datetime.strptime(string_2026, "%d/%m/%Y")
        date_2027 = datetime.strptime(string_2027, "%d/%m/%Y")
        date_2028 = datetime.strptime(string_2028, "%d/%m/%Y")
        date_2029 = datetime.strptime(string_2029, "%d/%m/%Y")
        date_2030 = datetime.strptime(string_2030, "%d/%m/%Y")
        present = datetime.now()
        if present.date() < date_2021():
            date = datetime.datetime(2021, 4, 6)
            date_list.append(date, date, date)
        elif present.date() < date_2022():
            date = datetime.datetime(2022, 4, 5)
            date_list.append(date, date, date)
        elif present.date() < date_2023():
            date = datetime.datetime(2023, 4, 11)
            date_list.append(date, date, date)
        elif present.date() < date_2024():
            date = datetime.datetime(2024, 4, 9)
            date_list.append(date, date, date)
        elif present.date() < date_2025():
            date = datetime.datetime(2025, 4, 8)
            date_list.append(date, date, date)
        elif present.date() < date_2026():
            date = datetime.datetime(2026, 4, 7)
            date_list.append(date, date, date)
        elif present.date() < date_2027():
            date = datetime.datetime(2027, 4, 6)
            date_list.append(date, date, date)
        elif present.date() < date_2028():
            date = datetime.datetime(2028, 4, 11)
            date_list.append(date, date, date)
        elif present.date() < date_2029():
            date = datetime.datetime(2029, 4, 10)
            date_list.append(date, date, date)
        elif present.date() < date_2030():
            date = datetime.datetime(2030, 4, 9)
            date_list.append(date, date, date)
    else:
        previous_date = date_list[row_number-4]
        date = pd.to_datetime(previous_date) + pd.DateOffset(days=1)
        date_list.append(date, date, date)
    return date


def add_shift(row_number):
    df_shift_list = []
    if row_number == 1:
        shift_name = "DAY"
        df_shift_list.append("DAY")
    else:
        if df_shift_list[row_number-2] == "DAY":
            df_shift_list.append("EVE")
            shift_name = "EVE"
        elif df_shift_list[row_number-2] == "EVE":
            df_shift_list.append("OWL")
            shift_name = "EVE"
        elif df_shift_list[row_number-2] == "OWL":
            df_shift_list.append("DAY")
            shift_name = "EVE"
    return shift_name

def create_data_frame(class_name):
    """Import values from excel file and creates a dataframe in python based on imported values"""
    data_array = []
    for i in range (546):
        row = [[i],set_date(i),add_shift(i), '', '', '', class_name.expirment_number[i], class_name.facilitie[i], '', set_ts_tm()[0], class_name.beam[i], '', class_name.target_type[i], class_name.source[i], set_ts_tm()[1]],
        data_array.append(row)     
    df =  pd.DataFrame(data_array, columns = ['','Date','Shift','Offine','current (uA)', 'Offline', 'Exp. #', 'Facility', 'Note', 'West / East', 'Beam', 'Energy (keV)', 'Tgt', 'Source', 'Mod'])  
    return df

def write_to_excel(class_name):
    df = create_data_frame(class_name)
    df.to_excel ("initial_schedule.xlsx", index = False, header=True)

if __name__ == "__main__":
    main()