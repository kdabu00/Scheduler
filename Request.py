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
        self.request_repeat = repeat_request_by_shift(request)

    @property
    def experiments(self):
        """Gets all ISAC experiment requests in the schedule"""
        # Put all priorities, fields, accelerator areas in their own lists
        priority = self.request['Priority'].tolist()
        field = self.request['Field'].tolist()
        acc = self.request['Acc Area'].tolist()
        shifts = self.request['Shifts requested'].tolist()
        # Create a set of unique facilities scheduled
        # Create a list of unique experiments with values Experiment, Facility, Target, and Ion Source
        request = self.request[['Experiment', 'Facility', 'Target', 'Ion Source']].values.tolist()
        exp_requested = {}
        for i in range(len(request)):
            # Turn each experiment into a tuple, this tuple will be used as a key
            # to find unique experiments and their values
            if request[i][3] == 'RILIS' or request[i][3] == 'SIS/RILIS':
                # Add shifts for setup
                exp_requested[tuple(request[i])] = [priority[i], field[i].upper(), acc[i].upper(), (shifts[i] + 3)]
            else:
                exp_requested[tuple(request[i])] = [priority[i], field[i].upper(), acc[i].upper(), (shifts[i] + 2)]
        return exp_requested

    @property
    def facilities(self):
        return set(self.request['Facility'].tolist())
    
    @property
    def facilitie(self):
        return self.request_repeat['Facility'].tolist()
    
    @property
    def required_shifts(self):
        return self.request_repeat['Shifts requested'].tolist()
    
    @property
    def expirment_number(self):
        return self.request_repeat['Experiment'].tolist()

    @property
    def beam(self):
        return self.request_repeat['Beam'].tolist()

    @property
    def target_type(self):
        return self.request_repeat['Target'].tolist()
    
    @property
    def source(self):
        return self.request_repeat['Ion Source'].tolist()

    @property
    def sort_by_target_block(self):
        # Group by source then group by target type
        requests_sort_by_tb = self.request.sort_values(by=['Ion Source', 'Target'])
        return requests_sort_by_tb

    @property
    def high_priority(self):
        return self.request.loc[self.request['Priority'] == 'H']

    @property
    def med_priority(self):
        return self.request.loc[self.request['Priority'] == 'M']


def refactor_request(request):
    # Check if a request is an ISAC experiment and if the Experiment # is not Test
    request = request.loc[(request['Beam options'] == 'ISAC Target (RIB)') & (request['Experiment'] != 'Test')]
    request.loc[:, 'Experiment'] = request.loc[:, 'Experiment'].str.upper()
    request.loc[:, 'Facility'] = request.loc[:, 'Facility'].str.upper()
    request.loc[:, 'Target'] = request.loc[:, 'Target'].str.upper()
    request.loc[:, 'Ion Source'] = request.loc[:, 'Ion Source'].str.upper()
    # change nan values into empty string
    request = request.fillna('')
    return request


def repeat_request_by_shift(request):
    # Get request is an ISAC experiment
    request = request.loc[(request['Beam options'] == 'ISAC Target (RIB)') & (request['Experiment'] != 'Test')]
    request = request.fillna('')
    # Sort request by source and target type
    requests_sort_by_tb = request.sort_values(by=['Ion Source', 'Target'])
    # Get the request repeat by shift
    shift_requested_list = requests_sort_by_tb['Shifts requested'].tolist()
    requests_sort_by_tb = requests_sort_by_tb.loc[requests_sort_by_tb.index.repeat(requests_sort_by_tb['Shifts requested'])].reset_index(
        drop=True)
    request_repeat = requests_sort_by_tb.sort_values(by=['Priority', 'Ion Source', 'Target'])
    return request_repeat
