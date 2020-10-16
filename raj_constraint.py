import constraint
"""
Author: David Chin
Rule 1: The location of the Target Station at the schedule start is fixed and cannot change, and the corresponding
Target Module is also fixed
Rule 2: The Target Station/Target Module combination alternates for each target block
Rule 3: The minimum length of the target block is 3 weeks.
Rule 4 : The target block starts and ends on Tuesday day shift.
Rule 5 : The maximum length of a target block is 4 weeks for UCx;5 weeks for anything else.
Rule 6: 

"""

problem = constraint.Problem()
# Target Station variable can only be East or West
problem.addVariable('Target_Station', ["East", "West"])
# Target Module can only be #2 or #4 (future - add #3 & #5)
problem.addVariable('Target_Module', ["#2", "#4"])
#The minimum lenght of target block is 3 weeks.
problem.addVariable('Target_length_min', range(22))
# Target block starts and ends on Tuesday day shift.
problem.addVariable('Target_block_day', ["Tuesday","tuesday"])
# Target's name.
problem.addVariable('Target',["UCx","Uranium"])
# The maximum length of a target block is 4 weeks for UCx;5 weeks for anything else.
problem.addVariable('Target_length_max', range(36))

def constraint_rule_1(Target_Station, Target_Module):
    if Target_Station == "East" or "West" and Target_Module == "#2" or "#4":
        return True

def constraint_rule_2():


def constraint_rule_3(Target_length_min):
    if Target_length_min >= 20:
        return True

def constraint_rule_4 (Target_block_day):
    if Target_block == "Tuesday" or "tuesday":
        return True

def constraint_rule_5(Target_length_max,Target):
    if Target == "UCx"  Target_length_max <=28: 
        return True 
    if Target =! "UCx" and Target_length_max <=35:
        return True




problem.addConstraint(constraint_rule_1, ['Target_Station','Target_Module'])
problem.addConstraint(constraint_rule_4, 'Target_block_day')
problem.addConstraint(constraint_rule_3, 'Target_length_min')
problem.addConstraint(constraint_rule_5, ['Target_length_max','Target'])




solutions = problem.getSolutions()        






