from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use
import heapq
import itertools
from queue import Queue

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def _get_successors(problem, state, visited=None):
    
    """Return iterable of (action, next_state, cost) using the Problem API.
    If visited is provided, only yield successors that are not in visited."""
    actions = problem.get_actions(state)
    # Convert to list/generator of triples
    def _iter():
        # If visited is provided, filter out visited states
        if visited is not None:
            # Iterate through actions and yield only unvisited successors
            for action in actions:
                # get the successor state
                next_state = problem.get_successor(state, action)
                if next_state not in visited:
                    # get the cost of the action
                    # if the problem has a get_cost method, use it
                    # otherwise, assume cost is 1.0 for each action
                    cost = problem.get_cost(state, action) if hasattr(problem, "get_cost") else 1.0
                    yield (action, next_state, cost)
        else:
            for action in actions:
                next_state = problem.get_successor(state, action)
                cost = problem.get_cost(state, action) if hasattr(problem, "get_cost") else 1.0
                yield (action, next_state, cost)
    return _iter()

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    current_state,current_path=(initial_state,[]) # (state, path)

    frontier=Queue()              # FIFO frontier to store nodes (state, path)
    frontier.put((current_state,current_path))

    explored=set()

    frontier_set=set()
    frontier_set.add(initial_state)  # frontier set to store states name only this decreases search time

    if problem.is_goal(current_state) :
        return current_path

    while (not frontier.empty()):
        current_state,current_path=frontier.get()
        
        for action in problem.get_actions(current_state):
            child_state,child_path=(problem.get_successor(current_state,action),current_path +[action])
            if (not (child_state in frontier_set)) and (not (child_state in explored)):
                if problem.is_goal(child_state) :
                    return child_path
                frontier.put((child_state,child_path))
                frontier_set.add(child_state)

        explored.add(current_state) 
    return None

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    current_state,current_path=(initial_state,[]) # (state, path)

    frontier=[]              # LIFO frontier to store nodes (state, path)
    frontier.append((current_state,current_path))

    explored=set()

    frontier_set=set()
    frontier_set.add(initial_state)  # frontier set to store states name only this decreases search time


    while frontier:
        current_state,current_path=frontier.pop()
        explored.add(current_state) 

        if problem.is_goal(current_state) :
            return current_path
        
        for action in problem.get_actions(current_state):
            child_state,child_path=problem.get_successor(current_state,action),current_path +[action]
            if (not (child_state in frontier_set)) and (not (child_state in explored)):
                frontier.append((child_state,child_path))
                frontier_set.add(child_state)

    return None

    
    
def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    
    # check if the initial state is the goal state
    if problem.is_goal(initial_state):
        return []
    
    # using a count to break ties in the priority queue
    # this ensures that the order of insertion is preserved for states with the same cost
    # to make sure that the search is deterministic
    # using itertools.count() to create an infinite iterator
    # itertools.count() is implemented in C and is optimized for performance
    
    counter = itertools.count()
    
    # create a priority queue for the frontier
    # it's a min-heap based on the cost to reach the state
    frontier = []  # (cost, tie, state, path)
    # h -> heuristic value
    # tie -> to break ties
    # state -> current state
    # path -> path to reach current state

    # g_cost dictionary to store the cost to reach each state
    # initialized with the initial state cost as 0
    # it will be updated as we find better paths to states
    g_cost = {initial_state: 0}
    
    # create a set to keep track of visited states
    visited = set()
    
    # push the initial state to the frontier with cost 0
    heapq.heappush(frontier, (0, next(counter), initial_state, []))
    
    # main loop
    # continue until the frontier is empty    
    while frontier:
        
        # pop the state with the lowest cost
        cost, _, state, path = heapq.heappop(frontier)
        
        # skip stale entries
        # if the cost is not equal to the g_cost of the state, 
        # it means that we have already found a better path to this state
        if cost != g_cost.get(state, float('inf')):
            continue
        
        # add to visited set
        visited.add(state)        
        
        # check if the state is the goal state
        # if it is, return the path to reach the goal
        if problem.is_goal(state):
            return path
        
        # expand the state and explore (not means visiting) its successors
        for action, next_state, step_cost in _get_successors(problem, state, visited):
            # _get_successors returns (action, next_state, step_cost)
            
            # we calculate the new cost to reach the next_state
            # in UCS, the cost is simply the cost to 
            # reach the current state plus the step cost to the next state
            new_cost = cost + step_cost
            
            # if the new cost is less than the g_cost of the next_state
            if new_cost < g_cost.get(next_state, float('inf')):
                g_cost[next_state] = new_cost
                
                # we push the next_state to the frontier with the new cost
                # no need to check if it's already in the frontier
                # because if it is already in the frontier with a higher cost,
                # it will be skipped when popped
                # and not visited states are ensured by _get_successors
                # so we don't need to check for visited states here
                heapq.heappush(frontier, (new_cost, next(counter), next_state, path + [action]))
    return None


def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    
    # check if the initial state is the goal state
    if problem.is_goal(initial_state):
        return []
    
    # using a count to break ties in the priority queue
    
    counter = itertools.count()
    
    frontier = []  # (f, tie, state, path, g)
    # f -> g + h
    # tie -> to break ties
    # state -> current state
    # path -> path to reach current state
    # g -> cost to reach current state
    
    #  initialize g_cost dictionary with the initial state cost as heuristic value
    g_cost = {initial_state: heuristic(problem, initial_state)}
    
    
    # create a set to keep track of visited states
    visited = set()
    
    # push the initial state to the frontier with f = h(initial_state)
    heapq.heappush(frontier, (heuristic(problem, initial_state), next(counter), initial_state, [], 0))
    
    # main loop
    # continue until the frontier is empty
    while frontier:
        # pop the state with the lowest f value
        f, _, state, path, g = heapq.heappop(frontier)
        
        # skip stale entries
        if f != g + heuristic(problem, state):
            continue
        
        # check if the state has been visited
        if state in visited:
            continue
        
        # check if the state is the goal state
        if problem.is_goal(state):
            return path
        
        # add to visited set
        visited.add(state)

        # expand the state and explore (not visit, just explore) its successors
        for action, next_state, step_cost in _get_successors(problem, state, visited):
            # calculate the new g cost to reach the next_state
            new_g = g + step_cost
            # calculate the new f cost
            new_f = new_g + heuristic(problem, next_state)
            
            # if the new g cost is less than the g_cost of the next_state
            if new_g < g_cost.get(next_state, float('inf')):
                g_cost[next_state] = new_g
                
                # push the next_state to the frontier with its f value
                # no need to check if it's already in the frontier
                # because if it is already in the frontier with a higher cost,
                # it will be skipped when popped
                # and not visited states are ensured by _get_successors
                # so we don't need to check for visited states here
                heapq.heappush(frontier, (new_f, next(counter), next_state, path + [action], new_g))
    return None

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    # check if the initial state is the goal state
    if problem.is_goal(initial_state):
        return []
    # using a count to break ties in the priority queue
    counter = itertools.count()
    
    # create a priority queue for the frontier
    # it's a min-heap based on the heuristic value
    frontier = []  # (h, tie, state, path)    
    heapq.heappush(frontier, (heuristic(problem, initial_state), next(counter), initial_state, []))
    
    # create a set to keep track of visited states
    visited = set()
    
    # create a dictionary to store the cost to reach each state
     # initialized with the initial state cost as 0
    cost = {initial_state: 0}

    # main loop
    while frontier:
        # pop the state with the lowest heuristic value
        _, _, state, path = heapq.heappop(frontier)
        
        # check if the state is the goal state
        if problem.is_goal(state):
            return path
        
        # add to visited set
        visited.add(state)

        # expand the state and explore (not visit, just explore) its successors
        for action, next_state, _ in _get_successors(problem, state, visited):
            # push the next_state to the frontier with its heuristic value
            # no need to check if it's already in the frontier
            # because visited set ensures we don't revisit states
            # and we don't need to check for visited states here
            # as _get_successors already filters them out
            # check if we have found a better path to next_state
            
            # get(state, float('inf')) returns infinity if state is not in cost
            # so the condition is always true for new states
            # get(state, 0) returns 0 if state is not in cost
            
            if cost.get(next_state, float('inf')) > cost.get(state, 0):
                cost[next_state] = cost.get(state, 0)
                # the 0 cost is because Best First Search does not consider path cost
                # it only considers heuristic value
                heapq.heappush(frontier, (heuristic(problem, next_state), next(counter), next_state, path + [action]))
    return None
