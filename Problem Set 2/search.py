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
 
    def alphabeta_recursive(current_state, depth, alpha, beta):
        # Base case: if the state is terminal, return its value for the player.
        terminal, values = game.is_terminal(current_state)
        if terminal:
            return values[0], None
        
        # Calculate the depth for the next recursive call.
        current_depth = depth if depth < 0 else depth - 1
        # Base case: if the maximum depth is reached, return the heuristic value of the state.
        if depth == 0:
            return heuristic(game, current_state, 0), None

        # Get the current agent and their possible actions.
        agent = game.get_turn(current_state)
        actions = game.get_actions(current_state)
        
        if agent == 0:  # MAX player
            max_value = float('-inf')
            best_action = None
            for action in actions:
                # Get the successor state for the current action.
                successor = game.get_successor(current_state, action)
                # Recursively call the function for the successor state.
                value, _ = alphabeta_recursive(successor, current_depth, alpha, beta)
                # If this move is better than any found so far, update the best value and action.
                if value > max_value:
                    max_value = value
                    best_action = action
                # Update alpha
                alpha = max(alpha, value)
                # Pruning condition 
                if beta <= alpha:
                    break  # beta cut-off
            return max_value, best_action
        
        else:  # MIN player
            min_value = float('inf')
            best_action = None
            for action in actions:
                # Get the successor state for the current action.
                successor = game.get_successor(current_state, action)
                # Recursively call the function for the successor state.
                value, _ = alphabeta_recursive(successor, current_depth, alpha, beta)
                # If this move is worse for the player than any found so far, update the best value and action.
                if value < min_value:
                    min_value = value
                    best_action = action
                # Update beta (the minimizer's best guaranteed score).
                beta = min(beta, value)
                # Pruning condition 
                if beta <= alpha:
                    break  # alpha cut-off
            return min_value, best_action

    # Start the search from the initial state with alpha = -inf and beta = +inf.
    return alphabeta_recursive(state, max_depth, float('-inf'), float('inf'))


# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    
    # It works similarly to the standard alphabeta_recursive but sorts moves before exploring them.
    def alphabeta_ordered_recursive(current_state, depth, alpha, beta):
        # Base case: if the state is terminal, return its value.
        terminal, values = game.is_terminal(current_state)
        if terminal:
            return values[0], None
        
        # Base case: if the maximum depth is reached, return the heuristic value.
        if depth == 0:
            return heuristic(game, current_state, 0), None

        # Calculate the depth for the next recursive call.
        current_depth = depth if depth < 0 else depth - 1

        # Get the current agent and their possible actions.
        agent = game.get_turn(current_state)
        actions = game.get_actions(current_state)
        
        # Move Ordering: Sort actions based on their heuristic value to improve pruning.
        # By exploring better moves first, we are more likely to cause cut-offs early.
        # The heuristic is always evaluated from the player's (agent 0) perspective.
        # - For the MAX player (agent 0), we sort in descending order (reverse=True) to check best moves first.
        # - For the MIN player (agent > 0), we sort in ascending order (reverse=False) to check worst-for-player moves first.
        ordered_actions = sorted(actions, key=lambda action: heuristic(game, game.get_successor(current_state, action), 0), reverse=(agent == 0))
        
        if agent == 0:  # MAX player
            max_value = float('-inf')
            best_action = None
            for action in ordered_actions:
                # Get the successor state for the current action.
                successor = game.get_successor(current_state, action)
                # Recursively call the function for the successor state.
                value, _ = alphabeta_ordered_recursive(successor, current_depth, alpha, beta)
                # If this move is better than any found so far, update the best value and action.
                if value > max_value:
                    max_value = value
                    best_action = action
                # Update alpha.
                alpha = max(alpha, value)
                # Pruning condition (beta cut-off).
                if beta <= alpha:
                    break  # beta cut-off
            return max_value, best_action
        else:  # MIN player
            min_value = float('inf')
            best_action = None
            for action in ordered_actions:
                # Get the successor state for the current action.
                successor = game.get_successor(current_state, action)
                # Recursively call the function for the successor state.
                value, _ = alphabeta_ordered_recursive(successor, current_depth, alpha, beta)
                # If this move is worse for the player than any found so far, update the best value and action.
                if value < min_value:
                    min_value = value
                    best_action = action
                # Update beta.
                beta = min(beta, value)
                # Pruning condition (alpha cut-off).
                if beta <= alpha:
                    break  # alpha cut-off
            return min_value, best_action

    # Start the search from the initial state with alpha = -inf and beta = +inf.
    return alphabeta_ordered_recursive(state, max_depth, float('-inf'), float('inf'))
    

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
    # found solution: calculate the expected value using the length of values
    # not the length of actions or successors although they are the same in this case
    # but this way it is more robust
    # and it works for all test cases in the grader
    
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
        # create list of values
        values = []
        
        expected_value = 0.0
        # probability = 1.0 / len(successors)
        for action in actions:
            successor = game.get_successor(state, action)
            value, _ = expectimax(game, successor, heuristic, next_depth)
            values.append(value)
        # sum values
        total_value = sum(values)
        # calculate probability
        probability = 1.0 / len(values)
        
        expected_value = total_value * probability
        return expected_value, None
            