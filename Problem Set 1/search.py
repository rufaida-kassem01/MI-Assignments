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

def _get_successors(problem, state):
    """Return iterable of (action, next_state, cost) using the Problem API.
    Supports Problem implementations that expose either:
      - get_actions(state) + get_successor(state, action) + get_cost(state, action)
      - or a get_successors(state) / successors(state) that already yields the triples.
    """
    # If problem already provides triple-producing method, prefer it
    if hasattr(problem, "get_successors"):
        return problem.get_successors(state)
    if hasattr(problem, "successors"):
        return problem.successors(state)
    # Otherwise build successors from get_actions/get_successor/get_cost
    if not hasattr(problem, "get_actions") or not hasattr(problem, "get_successor"):
        raise AttributeError(f"{problem.__class__.__name__} has no successors/get_actions/get_successor")
    actions = problem.get_actions(state)
    # Convert to list/generator of triples
    def _iter():
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
    if problem.is_goal(initial_state):
        return []
    counter = itertools.count()
    frontier = []  # (cost, tie, state, path)
    g_cost = {initial_state: 0}
    heapq.heappush(frontier, (0, next(counter), initial_state, []))
    while frontier:
        cost, _, state, path = heapq.heappop(frontier)
        # skip stale entries
        if cost != g_cost.get(state, float('inf')):
            continue
        if problem.is_goal(state):
            return path
        for action, next_state, step_cost in _get_successors(problem, state):
            new_cost = cost + step_cost
            if new_cost < g_cost.get(next_state, float('inf')):
                g_cost[next_state] = new_cost
                heapq.heappush(frontier, (new_cost, next(counter), next_state, path + [action]))
    return None

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    if problem.is_goal(initial_state):
        return []
    counter = itertools.count()
    frontier = []  # (f, tie, state, path, g)
    g_cost = {initial_state: 0}
    heapq.heappush(frontier, (heuristic(problem, initial_state), next(counter), initial_state, [], 0))
    while frontier:
        f, _, state, path, g = heapq.heappop(frontier)
        # skip stale entries
        if g != g_cost.get(state, float('inf')):
            continue
        if problem.is_goal(state):
            return path
        for action, next_state, step_cost in _get_successors(problem, state):
            tentative_g = g + step_cost
            if tentative_g < g_cost.get(next_state, float('inf')):
                g_cost[next_state] = tentative_g
                heapq.heappush(frontier, (tentative_g + heuristic(problem, next_state), next(counter), next_state, path + [action], tentative_g))
    return None

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    if problem.is_goal(initial_state):
        return []
    counter = itertools.count()
    frontier = []  # (h, tie, state, path)
    visited = set()
    heapq.heappush(frontier, (heuristic(problem, initial_state), next(counter), initial_state, []))
    while frontier:
        _, _, state, path = heapq.heappop(frontier)
        if state in visited:
            continue
        visited.add(state)
        if problem.is_goal(state):
            return path
        for action, next_state, step_cost in _get_successors(problem, state):
            if next_state not in visited:
                heapq.heappush(frontier, (heuristic(problem, next_state), next(counter), next_state, path + [action]))
    return None