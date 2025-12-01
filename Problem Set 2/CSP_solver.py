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
        if other_variable not in domains:
            continue
        
        # Create a new set for the filtered domain
        new_other_domain = set()
        
        # Iterate over the current domain of the other variable
        for other_value in domains[other_variable]:
            # Create a temporary assignment to check if the constraint is satisfied
            temp_assignment = {assigned_variable: assigned_value, other_variable: other_value}
            if constraint.is_satisfied(temp_assignment):
                new_other_domain.add(other_value)
        
        # Update the domain of the other variable
        domains[other_variable] = new_other_domain
        
        # Check if the domain of the other variable became empty
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
    x = variable_to_assign
    x_domain = list(domains[x])  # convert domain of x to a list for deterministic ordering

    # Step 1: Collect binary constraints involving x, grouped by neighbor variable
    constraints_by_neighbor: Dict[str, List[BinaryConstraint]] = {}
    for c in problem.constraints:
        if not isinstance(c, BinaryConstraint) or x not in c.variables:
            continue  # skip non-binary constraints or those not involving x
        y = c.get_other(x)  # get the other variable in this binary constraint
        constraints_by_neighbor.setdefault(y, []).append(c)  # group constraints by neighbor

    results = []  # will store tuples of (value, number_of_pruned_values)

    # Step 2: For each value in x's domain, count how many values it would prune in neighbors
    for val in x_domain:
        pruned_count = 0  # count of values pruned in neighbors if x is assigned 'val'
        for y, constraints in constraints_by_neighbor.items():
            # skip neighbors that are already assigned (not in domains)
            if y not in domains:
                continue
            y_domain = domains[y]
            for yv in y_domain:
                # check if the current neighbor value yv would be removed
                rejected = False
                for c in constraints:
                    # test if the binary constraint is satisfied with x=val, y=yv
                    if not c.is_satisfied({x: val, y: yv}):
                        rejected = True
                        break  # no need to check other constraints for this neighbor value
                if rejected:
                    pruned_count += 1  # increment count of pruned neighbor values

        # record how "restrictive" this value is
        results.append((val, pruned_count))

    # Step 3: Sort by least-restraining (smallest pruned_count first), tie-break by value
    results.sort(key=lambda p: (p[1], p[0]))

    # Step 4: Return just the values in the sorted order
    return [v for v, _ in results]

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



    