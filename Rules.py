import constraint
"""
Rule 1: The location of the Target Station at the schedule start is fixed and cannot change, and the corresponding
Target Module is also fixed
Rule 2: The Target Station/Target Module combination alternates for each target block
"""

problem = constraint.Problem()
# Target Station variable can only be East or West
problem.addVariable('Target_Station', ["East", "West"])
# Target Module can only be #2 or #4 (future - add #3 & #5)
problem.addVariable('Target_Module', ["#2", "#4"])

def constraint_rule_1 (Target_Station, Target_Module):
    if Target_Station == "East" or "West" and Target_Module == "#2" or "#4":
        return True

def constraint_rule_2 ():

problem.addConstraint(constraint_rule_1, ['Target_Station','Target_Module'])

solutions = problem.getSolutions()
