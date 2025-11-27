from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented
from copy import deepcopy

# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        new_domain = {value for value in problem.domains[variable] if constraint.condition(value)}
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable

# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument 
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic, 
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min((len(domains[variable]), index, variable) for index, variable in enumerate(problem.variables) if variable in domains)
    return variable

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    #TODO: Write this function
    # NotImplemented()

# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
    variables_to_check=[]
    checking_constrains=[]
    print("inside forward checking  function")
    for constraint in problem.constraints:
        #skip all unary constraints
        if not isinstance(constraint, BinaryConstraint):
            continue

        #skip all constraints that do not involve the assigned variable
        if assigned_variable not in constraint.variables:
            continue

        #get the other variable involved in the constraint
        other_variable=constraint.get_other(assigned_variable)  
        if other_variable not in domains.keys():
            continue
        
        #deep copy the domain of the other variable to avoid modifying the original domains while iterating
        tmp_domains=deepcopy(domains[other_variable])
        for value in tmp_domains:
            if not constraint.condition(assigned_value,value):
                #remove values that violates the constrain from the other variable's domain
                domains[other_variable].discard(value)

        #check if the domain of the other variable is empty
        if not domains[other_variable]:
            return False

    return True

        



def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    #TODO: Write this function
    # create a copy of the domains to not modify the given one
    import copy
    domains_copy = copy.deepcopy(domains)
    x = variable_to_assign
    x_domain = domains_copy[x]
    # y are the neighbors of x
    neighbors = [constraint.get_other(x) for constraint in problem.constraints if isinstance(constraint, BinaryConstraint) and x in constraint.variables]
    
    # create the results list
    result = []
    
    # loop over the values possible for the variable given to the function
    # assume each value and loop over the neighbors of x (the given variable)
    # and check each value in the domain of each neighbor y with the current assumed value of x
    # if not available ==> increase the pruned values counter
    # and return the possible values of x paired with their pruned counter
    # sorted ascending (the least is better)
    for value in x_domain:
        pruned_values_count = 0
        for y in neighbors:
            y_domain = domains_copy[y]
            for y_value in y_domain:
                # find the constraint between x and y
                constraint = next(constraint for constraint in problem.constraints if isinstance(constraint, BinaryConstraint) and set(constraint.variables) == {x, y})
                if not constraint.condition(value, y_value):
                    pruned_values_count += 1
                    # no need to actually prune since we are just counting
                    # y_domain.remove(y_value)
        result.append((value, pruned_values_count))
    # sort the result based on the pruned values count first, then by the value itself
    result.sort(key=lambda pair: (pair[1], pair[0]))
    
    # return the sorted list of x values only
    return [pair[0] for pair in result]
# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    #TODO: Write this function
    NotImplemented()