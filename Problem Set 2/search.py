from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state) 

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that 
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    # terminal state or depth limit reached
    terminal, values = game.is_terminal(state)
    if terminal:
        return values[0], None  # return the value for the player (max node)
    if max_depth == 0:
        return heuristic(game, state, 0), None  # return heuristic value for the player
    
    # determine next depth
    # if max_depth is negative, it means no depth limit
    # so we keep it negative
    if max_depth < 0:
        next_depth = -1  # no depth limit
    else:
        next_depth = max_depth - 1
        
    agent = game.get_turn(state)
    actions = game.get_actions(state)
    
    # player's turn (max node) or enemy's turn (min node)
    # our turn is always agent 0
    if agent == 0:  # max node
        max_value = float('-inf')
        best_action = None
        for action in actions:
            successor = game.get_successor(state, action)
            value, _ = minimax(game, successor, heuristic, next_depth)
            if value > max_value:
                max_value = value
                best_action = action
        return max_value, best_action
    else:  # min node
        min_value = float('inf')
        best_action = None
        for action in actions:
            successor = game.get_successor(state, action)
            value, _ = minimax(game, successor, heuristic, next_depth)
            if value < min_value:
                min_value = value
                best_action = action
        return min_value, best_action
    
# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    NotImplemented()

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    NotImplemented()

# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    # terminal state
    terminal, values = game.is_terminal(state)
    if terminal:
        return values[0], None  # return the value for the player (max node)
    
    # depth limit reached
    if max_depth == 0:
        return heuristic(game, state, 0), None  # return heuristic value for the player
    # determine next depth
    if max_depth < 0:
        next_depth = -1  # no depth limit
    else:
        next_depth = max_depth - 1
        
    # get current agent and actions
    agent = game.get_turn(state)
    
    # tree 2 has a tie problem (test case number 2 in the grader)
    #     root
    #  ├── A → expectimax value = 6
    #  └── B → expectimax value = 6
    # the grader expects action A to be chosen
    # but it chooses B although we use strict greater than comparison
    actions = game.get_actions(state)
    
    # # if there are no actions, return heuristic value
    # if not actions:
    #     return heuristic(game, state, 0), None
    
    # player's turn (max node) or enemy's turn (chance node)
    if agent == 0:  # max node
        max_value = float('-inf')
        best_action = None
        for action in actions:
            successor = game.get_successor(state, action)
            value, _ = expectimax(game, successor, heuristic, next_depth)
            if value > max_value:
                max_value = value
                best_action = action
        return max_value, best_action
    
    else:  # chance node
        # calculate expected value
        # create list of successors
        successors = [game.get_successor(state, action) for action in actions]
        # create list of values
        values = []
        
        expected_value = 0.0
        # probability = 1.0 / len(successors)
        for successor in successors:
            value, _ = expectimax(game, successor, heuristic, next_depth)
            values.append(value)
        # sum values
        total_value = sum(values)
        # calculate probability
        probability = 1.0 / len(values)
        
        expected_value = total_value * probability
        # for action in actions:
        #     successor = game.get_successor(state, action)
        #     value, _ = expectimax(game, successor, heuristic, next_depth)
        #     expected_value += value * probability
        return expected_value, None
            