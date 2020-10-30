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


def refactor_request(request):
    # Check if a request is an ISAC experiment and if the Experiment # is Test
    request = request.loc[(request['Beam options'] == 'ISAC Target (RIB)') & (request['Experiment'] != 'Test')]
    # change nan values into empty string
    request = request.fillna('')
    return request
