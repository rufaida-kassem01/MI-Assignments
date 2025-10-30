from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented
import itertools

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

#TODO: Import any modules and write any functions you want to use


def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    #TODO: ADD YOUR CODE HERE
    #IMPORTANT: DO NOT USE "problem.get_actions" HERE.
    # Calling it here will mess up the tracking of the expanded nodes count
    # which is the number of get_actions calls during the search
    #NOTE: you can use problem.cache() to get a dictionary in which you can store information that will persist between calls of this function
    # This could be useful if you want to store the results heavy computations that can be cached and used across multiple calls of this function
    
    # # robust target lookup + caching
    
    # cache = problem.cache()
    # if "sokoban_targets" in cache:
    #     targets = cache["sokoban_targets"]
    # else:
    #     targets = None
    #     # try common places for targets/goals
    #     if hasattr(problem, "targets"):
    #         targets = problem.targets
    #     elif hasattr(problem, "goals"):
    #         targets = problem.goals
    #     elif hasattr(problem, "layout"):
    #         layout = problem.layout
    #         if hasattr(layout, "targets"):
    #             targets = layout.targets
    #         elif hasattr(layout, "goals"):
    #             targets = layout.goals
    #         elif hasattr(layout, "get_targets"):
    #             targets = layout.get_targets()
    #     # sometimes targets are stored on the state.layout
    #     if targets is None and hasattr(state, "layout"):
    #         layout = state.layout
    #         if hasattr(layout, "targets"):
    #             targets = layout.targets
    #         elif hasattr(layout, "goals"):
    #             targets = layout.goals
    #         elif hasattr(layout, "get_targets"):
    #             targets = layout.get_targets()
    #     if targets is None:
    #         raise AttributeError("Could not find sokoban target/goal locations on problem or state")
    #     # ensure it's a tuple/list of Points
    #     targets = tuple(targets)
    #     cache["sokoban_targets"] = targets

    # # If no crates, heuristic is zero
    # if not state.crates:
    #     return 0.0

    # # Sum of distances from each crate to its nearest target (allows reuse -> admissible but weaker)
    # total_crate_to_target = 0
    # for crate in state.crates:
    #     dmin = min(manhattan_distance(crate, t) for t in targets)
    #     total_crate_to_target += dmin

    # # distance from player to nearest crate
    # player_to_crate = min(manhattan_distance(state.player, crate) for crate in state.crates)

    # # Combine as a lower-bound estimate
    # return float(total_crate_to_target + player_to_crate)

    
    cache = problem.cache()
    if "sokoban_targets" in cache:
        targets = cache["sokoban_targets"]
    else:
        targets = None
        # try common places for targets/goals
        if hasattr(problem, "targets"):
            targets = problem.targets
        elif hasattr(problem, "goals"):
            targets = problem.goals
        elif hasattr(problem, "layout"):
            layout = problem.layout
            if hasattr(layout, "targets"):
                targets = layout.targets
            elif hasattr(layout, "goals"):
                targets = layout.goals
            elif hasattr(layout, "get_targets"):
                targets = layout.get_targets()
        # sometimes targets are stored on the state.layout
        if targets is None and hasattr(state, "layout"):
            layout = state.layout
            if hasattr(layout, "targets"):
                targets = layout.targets
            elif hasattr(layout, "goals"):
                targets = layout.goals
            elif hasattr(layout, "get_targets"):
                targets = layout.get_targets()
        if targets is None:
            raise AttributeError("Could not find sokoban target/goal locations on problem or state")
        targets = tuple(targets)
        cache["sokoban_targets"] = targets

    # normalize crates list
    crates = tuple(state.crates) if not isinstance(state.crates, (set, frozenset)) else tuple(state.crates)

    # If no crates, heuristic is zero
    if not crates:
        return 0.0

    # If all crates already on targets -> heuristic must be zero (goal w.r.t. crates)
    if all(crate in targets for crate in crates):
        return 0.0


    # Compute minimal sum of crate->target distances (optimal assignment)
    key = (targets, len(crates))
    # We cannot reuse across different crate positions, but we can compute per-state below; keep cache for other helpers if needed.
    # Use branch-and-bound over permutations (usually small number of crates)
    best = float("inf")
    # quick lower bound: sum of min distance per crate (independent)
    lb = 0
    for crate in crates:
        lb += min(manhattan_distance(crate, t) for t in targets)
    best = min(best, lb)  # use as starting bound

    # enumerate permutations of distinct targets for crates (if targets >= crates)
    if len(targets) >= len(crates):
        for perm in itertools.permutations(targets, r=len(crates)):
            s = 0
            # branch and bound
            for c, t in zip(crates, perm):
                s += manhattan_distance(c, t)
                if s >= best:
                    break
            else:
                # completed permutation with cost s < best
                best = s
                if best == 0:
                    break

    total_crate_to_target = float(best)

    # distance from player to nearest crate (ignore crates already on targets as they don't need pushing)
    movable_crates = [c for c in crates if c not in targets]
    if movable_crates:
        player_to_crate = min(manhattan_distance(state.player, crate) for crate in movable_crates)
    else:
        player_to_crate = 0
    # Combine as a lower-bound estimate
# -    return float(total_crate_to_target + player_to_crate)
    # Use max to keep the heuristic consistent: a single action can reduce
    # either the crate->target assignment cost by at most 1 (a push) or the
    # player->crate distance by at most 1 (a move), so max(...) decreases by ≤1.
    return float(max(total_crate_to_target, player_to_crate))
