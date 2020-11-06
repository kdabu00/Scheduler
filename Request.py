"""
Request.py
Author: Kevin Dabu
Date: Oct.29 2020

Requests class object
"""

class Request:

    def __init__(self, name, request):
        """Creates an instance of the request class"""
        self.name = name
        self.request = refactor_request(request)
        self.request_sort_by_tb= sort_by_target_block(request)
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
    def required_shifts(self):
        return set(self.request['Shifts requested'].tolist())
    
    @property
    def expirment_number(self):
        return set(self.request['Experiment'].tolist())

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

def repeat_request_by_shift(request):
    # Get request is an ISAC experiment
    request = request.loc[(request['Beam options'] == 'ISAC Target (RIB)') & (request['Experiment'] != 'Test')]
    request = request.fillna('')
    # Sort request by source and target type
    requests_sort_by_tb = request.sort_values(by=['Ion Source', 'Target'])
    # Get the request repeat by shift
    shift_requested_list = requests_sort_by_tb['Shifts requested'].tolist()
    for i in range(requests_sort_by_tb.index.size):
        df_row = requests_sort_by_tb[i+1]
        temporary_table = requests_sort_by_tb.append(df_row*shift_requested_list[i+1])
    request_repeat = temporary_table.sort_values(by=['Ion Source', 'Target'])
    return request_repeat
