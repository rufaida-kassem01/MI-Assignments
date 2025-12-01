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
    # print("inside forward checking  function")
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
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    #TODO: Write this function

    # IMPORTANT: This function should not modify any of the given arguments.
    # We only READ from `problem` and `domains`, and never change them.

    # we don't need to create a copy of the domains 
    # as we are not modifying them, only reading from them.
    x = variable_to_assign
    x_domain = domains[x]

    # We extract only BinaryConstraints involving x.
    # This dictionary only stores references, we do not modify anything.
    x_constraints = {
        constraint.get_other(x): constraint
        for constraint in problem.constraints
        if isinstance(constraint, BinaryConstraint) and x in constraint.variables
    }

    # create the results list
    results = []

    # check each value of x
    # for each value, count how many values would be pruned from neighbors' domains
    # without actually pruning them and then store the count
    for value in x_domain:
        pruned_values_count = 0

        for y, constraint in x_constraints.items():

            # Because assigned vars don't appear in domains → skip.
            if y not in domains:
                continue
            
            # get the domain of neighbor y
            y_domain = domains[y]

            # check each value of the neighbor y
            for y_value in y_domain:
                # constraint check — if it fails, it would be pruned
                if not constraint.condition(value, y_value):
                    pruned_values_count += 1
                    # we do NOT prune or change anything — only count

        # store the value and its pruned count
        results.append((value, pruned_values_count))

    # sort the result based on the pruned values count first, then by the value itself
    # (to break ties in ascending order)
    results.sort(key=lambda pair: (pair[1], pair[0]))

    # return the sorted list of x values only
    return [val for val, _ in results]
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
    assignment={}

    #apply 1-consistency to the problem
    if not one_consistency(problem):
        return None
    
    return recursive_backtracking(problem,assignment,problem.domains)

def recursive_backtracking(problem, assignment, domains):
    #base case : check if the assignment is complete
    if problem.is_complete(assignment):
        return assignment
    

    var = minimum_remaining_values(problem,domains)
    ordered_values=least_restraining_values(problem,var,domains)

    #try each value in the ordered values
    for value in ordered_values:
        assignment[var]=value

        #create a deep copy of the domains to not modify the original one
        new_domains=deepcopy(domains)

        #remove the assigned variable from the domains because it is now assigned
        del new_domains[var]

        #apply forward checking to make sure the assignment is valid
        if forward_checking(problem,var,value,new_domains):
            result=recursive_backtracking(problem,assignment,new_domains)
            if result is not None:
                return result
        #backtrack by removing the assigned variable from the assignment
        del assignment[var]
    return None



    