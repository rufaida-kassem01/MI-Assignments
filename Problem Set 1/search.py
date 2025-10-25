from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use
import heapq
from queue import Queue
from queue import LifoQueue

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    current_node=(initial_state,[]) # (state, path)

    frontier=Queue()              # FIFO frontier to store nodes (state, path)
    frontier.put(current_node)

    explored=set()

    frontier_set=set()
    frontier_set.add(initial_state)  # frontier set to store states name only this decreases search time

    if problem.is_goal(current_node[0]) :
        return current_node[1]

    while (not frontier.empty()):
        current_node=frontier.get()
        
        for action in problem.get_actions(current_node[0]):
            child=(problem.get_successor(current_node[0],action),current_node[1] +[action])
            if (not (child[0] in frontier_set)) and (not (child[0] in explored)):
                if problem.is_goal(child[0]) :
                    return child[1]
                frontier.put(child)
                frontier_set.add(child[0])

        explored.add(current_node[0]) 
    return None

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    current_node=(initial_state,[]) # (state, path)

    frontier=[]              # LIFO frontier to store nodes (state, path)
    frontier.append(current_node)

    explored=set()

    frontier_set=set()
    frontier_set.add(initial_state)  # frontier set to store states name only this decreases search time


    while frontier:
        current_node=frontier.pop()
        explored.add(current_node[0]) 

        if problem.is_goal(current_node[0]) :
            return current_node[1]
        
        for action in problem.get_actions(current_node[0]):
            child=problem.get_successor(current_node[0],action),current_node[1] +[action]
            if (not (child[0] in frontier_set)) and (not (child[0] in explored)):
                frontier.append(child)
                frontier_set.add(child[0])

    return None

    

def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()