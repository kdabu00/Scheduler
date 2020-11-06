"""
Request.py
Author: Kevin Dabu
Date: Oct.29 2020

Requests class object
"""
import numpy as np
import pandas as pd
import FileManager as fm

class Request:

    def __init__(self, name, request):
        """Creates an instance of the request class"""
        self.name = name
        self.request = refactor_request(request)
        self.request_sort_by_tb = sort_by_target_block(request)
        self.request_repeat = repeat_request_by_shift(request)

    @property
    def experiments(self):
        """Gets all ISAC experiment requests in the schedule"""
        # Put all priorities, fields, accelerator areas in their own lists
        priority = self.request['Priority'].tolist()
        field = self.request['Field'].tolist()
        acc = self.request['Acc Area'].tolist()
        # Create a set of unique facilities scheduled
        # Create a list of unique experiments with values Experiment, Facility, Target, and Ion Source
        request = self.request[['Experiment', 'Facility', 'Target', 'Ion Source']].values.tolist()
        exp_requested = {}
        for i in range(len(request)):
            # Turn each experiment into a tuple, this tuple will be used as a key
            # to find unique experiments and their values
            exp_requested[tuple(request[i])] = [priority[i], field[i], acc[i]]
        return exp_requested

    @property
    def facilities(self):
        return set(self.request['Facility'].tolist())
    
    @property
    def facilitie(self):
        return set(self.request_repeat['Facility'].tolist())
    
    @property
    def required_shifts(self):
        return set(self.request_repeat['Shifts requested'].tolist())
    
    @property
    def expirment_number(self):
        return set(self.request_repeat['Experiment'].tolist())

    @property
    def beam(self):
        return set(self.request_repeat['Beam'].tolist())

    @property
    def target_type(self):
        return set(self.request_repeat['Target'].tolist())
    
    @property
    def source(self):
        return set(self.request_repeat['Ion Source'].tolist())

def refactor_request(request):
    # Check if a request is an ISAC experiment and if the Experiment # is not Test
    request = request.loc[(request['Beam options'] == 'ISAC Target (RIB)') & (request['Experiment'] != 'Test')]
    # change nan values into empty string
    request = request.fillna('')
    return request

def sort_by_target_block(request):
    # Group by source then group by target type
    requests_sort_by_tb = request.sort_values(by=['Ion Source', 'Target'])
    return requests_sort_by_tb
'''
def repeat_request_by_shift(request):
    # Get request is an ISAC experiment
    request = request.loc[(request['Beam options'] == 'ISAC Target (RIB)') & (request['Experiment'] != 'Test')]
    request = request.fillna('')
    # Sort request by source and target type
    requests_sort_by_tb = request.sort_values(by=['Ion Source', 'Target'])
    # Get the request repeat by shift
    shift_requested_list = requests_sort_by_tb['Shifts requested'].tolist()
    for i in range(requests_sort_by_tb.index.size):
        df_row = np.array(requests_sort_by_tb.values[i+1])
        data_added = np.tile(df_row,(shift_requested_list-1,1))
    df = np.concatenate((requests_sort_by_tb.value, data_added))
    temporary_table = pd.DataFrame(data=df, columns=df[0])
    request_repeat = temporary_table.sort_values(by=['Ion Source', 'Target'])
    return request_repeat
'''
def repeat_request_by_shift(request):
    # Get request is an ISAC experiment
    request = request.loc[(request['Beam options'] == 'ISAC Target (RIB)') & (request['Experiment'] != 'Test')]
    request = request.fillna('')
    # Sort request by source and target type
    requests_sort_by_tb = request.sort_values(by=['Ion Source', 'Target'])
    # Get the request repeat by shift
    shift_requested_list = requests_sort_by_tb['Shifts requested'].tolist()
    for i in range(requests_sort_by_tb.index.size):
        df_row = requests_sort_by_tb.values[i]
        for j in range (int(shift_requested_list[i])):
            df_length = len(requests_sort_by_tb)
            requests_sort_by_tb.loc[df_length] = (df_row)
            #print(requests_sort_by_tb.values[0])
            #print(df_row)

    request_repeat = requests_sort_by_tb.sort_values(by=['Ion Source', 'Target'])
    # print(request_repeat)
    return request_repeat

'''
if __name__ == '__main__':
    request_file = fm.get_files('Requests')
    request = fm.read_file('Requests', request_file[0])
    request = Request(request_file[0], request)
'''