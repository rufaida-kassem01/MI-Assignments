from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

#TODO: Import any modules and write any functions you want to use
from itertools import permutations

# calculate if a state is in deadlock
# A simple deadlock detection: if a box is in a corner (not on a goal) it is a deadlock
# this is a helper function used in the strong_heuristic function
def is_deadlock(problem: SokobanProblem, state: SokobanState) -> bool:
    # a dead-end is a position where the stone can't be moved anymore
    # so we will check if the stones are in a dead-end
    # we will do that by checking if the stone is surrounded by walls or stones
    
    
    # create lists to reserve goals along the walls
    left_wall_goals_reserved = [] # list of goals that are reserved for the crates along the left wall
    right_wall_goals_reserved = [] # list of goals that are reserved for the crates along the right wall
    bottom_wall_goals_reserved = [] # list of goals that are reserved for the crates along the lower wall
    top_wall_goals_reserved = [] # list of goals that are reserved for the crates along the upper wall

    goals_flag = False
    
    # check each box for deadlock
    for box in state.crates:
        
        # check the first case --> 
        # if the crate is along a wall and there is no goal along that wall for it
        
        goals_flag = False # flag to check if there is a goal along the wall for this stone
        
        # check for each wall
        # left wall
        if box.x == 1:
            if box in problem.layout.goals:  # if the crate is in a goal position then this goal is reserved for it
                left_wall_goals_reserved.append(box)
                continue
            for goal in problem.layout.goals: # loop over the goals and check if there is a goal along the wall that is not reserved for another stone
                if goal. x == box.x and goal not in state.crates and goal not in left_wall_goals_reserved:
                    goals_flag = True
                    left_wall_goals_reserved.append(goal)
            if goals_flag == False: # if there is no goal along the wall that is not reserved for another stone then it is a dead-end
                return True
            
        goals_flag = False # reset the flag
        
        # right wall
        if box.x == problem.layout.width - 2:
            if box in problem.layout.goals:
                right_wall_goals_reserved.append(box)
                continue
            for goal in problem.layout.goals:
                if goal. x == box.x and goal not in state.crates and goal not in right_wall_goals_reserved:
                    goals_flag = True
                    right_wall_goals_reserved.append(goal)
            if goals_flag == False:
                return True
            
        goals_flag = False # reset the flag
        # top wall
        if box.y == 1:
            if box in problem.layout.goals:
                top_wall_goals_reserved.append(box)
                continue
            for goal in problem.layout.goals:
                if goal. y == box.y and goal not in state.crates and goal not in top_wall_goals_reserved:
                    goals_flag = True
                    top_wall_goals_reserved.append(goal)
            if goals_flag == False:
                return True
            
        goals_flag = False # reset the flag
        
        # bottom wall
        if box.y == problem.layout.height - 2: 
            if box in problem.layout.goals:
                bottom_wall_goals_reserved.append(box)
                continue
            for goal in problem.layout.goals:
                if goal. y == box.y and goal not in state.crates and goal not in bottom_wall_goals_reserved:
                    goals_flag = True
                    bottom_wall_goals_reserved.append(goal)
            if goals_flag == False:
                return True
            
        
        # check if this crate not in a goal position, if it is then it is not a dead-end
        if box in problem.layout.goals: continue
        
        # get the surrounding stones
        l = Point(box.x - 1, box.y) # left
        r = Point(box.x + 1, box.y) # right
        d = Point(box.x, box.y - 1) # down
        u = Point(box.x, box.y + 1) # up

        # check the second case -->
        
        # if it is in a corner (i.e., there are walls in two perpendicular directions)

        if(l not in problem.layout.walkable and 
            u not in problem.layout.walkable and 
            l != state.player and 
                u != state.player and 
            l not in problem.layout.goals and 
            u not in problem.layout.goals): # the top-left corner
            return True
        if(l not in problem.layout.walkable and 
        d not in problem.layout.walkable and
        l != state.player and
        d != state.player and
        l not in problem.layout.goals and
        d not in problem.layout.goals): # the bottom-left corner
            return True
        if(r not in problem.layout.walkable and
            
        u not in problem.layout.walkable and
        r != state.player and
        u != state.player and
        r not in problem.layout.goals and
        u not in problem.layout.goals): # the top-right corner
            return True
        if(r not in problem.layout.walkable and 
        d not in problem.layout.walkable and
        r != state.player and
        d != state.player and
        r not in problem.layout.goals and
        d not in problem.layout.goals): # the bottom-right corner
            return True

        
        # the following conditions check for more complex deadlock scenarios
        # they decrease the expanded nodes in the test cases provided
        # for example:
        #  without these conditions:
            # 1: Level 2 :: time-limit = 1.8743850588798523 sec
            # Result: PASS 2/2 - Expanded 1104 nodes in 0.04249000549316406 seconds
            # 2: Level 3 :: time-limit = 1.2495900392532349 sec
            # Result: PASS 4/4 - Expanded 6874 nodes in 0.5320863723754883 seconds
            # 3: Level 4 :: time-limit = 4.685962647199631 sec
            # Result: PASS 6/6 - Expanded 49285 nodes in 2.419755697250366 seconds
            # Total 12/12       
        # with these conditions:
            # 1: Level 2 :: time-limit = 1.8743850588798523 sec
            # Result: PASS 2/2 - Expanded 1082 nodes in 0.04236650466918945 seconds
            # 2: Level 3 :: time-limit = 1.2495900392532349 sec
            # Result: PASS 4/4 - Expanded 5945 nodes in 0.5081934928894043 seconds
            # 3: Level 4 :: time-limit = 4.685962647199631 sec
            # Result: PASS 6/6 - Expanded 49285 nodes in 2.599449872970581 seconds
            # Total 12/12
            
            
        # when there is a wall near the box and there are obstacles in the diagonal and one of the adjacent sides
        
        #########
        #       #
        # #     #
        #       #
        #    #  #
        ## #### #
        # $*.   #  --> this $ crate is in deadlock
        # *  @$ #
        #########

        if box.x == 2: # check if the box is near the left wall
            # get the upper left diagonal point
            u_l_diag = Point(box.x - 1, box.y + 1)
            if u_l_diag not in problem.layout.walkable and \
                (d not in problem.layout.walkable or
                 d not in problem.layout.walkable):
                return True              
        
        # in case there is crate near its goal but cant move to it due to obstacles

        #. #  #
        #+$ * #
        #######
        if box.y == problem.layout.height - 2:
            # get the diagonal point
            diag = Point(box.x+1, box.y-1)
            if diag not in problem.layout.walkable:
                # check if the path from this crate to the end of the wall doesn't contain a goal for it
                goals_n = 0
                crates_n = 0
                for i in range(box.x+1, problem.layout.width-1):
                    # if a wall is found before finding a goal, then dead-end
                    if Point(i, box.y) not in problem.layout.walkable:
                        if goals_n == 0:
                            return True
                    if Point(i, box.y) in problem.layout.goals:
                        goals_n += 1
                    if Point(i, box.y) in state.crates:
                        crates_n += 1
                if goals_n <= crates_n:
                    return True
                
        # in case there is a crate near the right wall but cant move to its goal due to obstacles
        ########
        #   #  #
        #   #$$#  --> deadlock
        #   @..#
        #   #$$# --> deadlock
        #   #  #
        ########
        if box.x == problem.layout.width - 2:
            obstacle = False
            goal_found = False
            all_walls = True
            for i in range(box.x-1, 0, -1):
                if Point(i, box.y) in problem.layout.walkable and \
                Point(i, box.y) not in state.crates:
                    break
                elif Point(i, box.y) not in state.crates:
                    obstacle = True
                    obstacle_point = Point(i, box.y)
                    for j in range(obstacle_point.y-1, 0, -1):
                        if Point(obstacle_point.x, j) in problem.layout.walkable:
                            all_walls = False
                            break
                    break
                
            if obstacle == True and all_walls == True:
                # check for a goal possible for this crate
                for i in range(box.y-1, 0, -1):
                    if Point(box.x, i) in problem.layout.goals:
                        goal_found = True
                if goal_found == False:
                    return True
            
        # there are other deadlock cases that are covered in the above conditions
        # like  #########
                # $     #  --> tunnel (it may move left only)
                # # $   #
                #   $   #
                #    #  #
                ## #### #
                #  ..   #
                # +     #
                #########
        # this case is covered in the first condition 
        # where there is no goal along the wall for the crate

        # and more complex cases that are not covered here
        # but for the sake of simplicity and the given test cases
        # we will stop here
        
    return False  # No deadlock detected



# calculate minimum distance from each box to any goal
# this function is used in the strong_heuristic function
# it uses caching to avoid redundant calculations

# Helper function to get the best combination of box-goal assignments
# This function calculates the minimum total distance for assigning boxes to goals
def get_best_box_goal_assignment(state: SokobanState) -> int:

    # get goals and boxes as lists
    goals = list(state.layout.goals)
    boxes = list(state.crates)
    
    # Initialize minimum total distance as infinity
    min_total_distance = float('inf')
    
    # Generate all permutations of goals for the boxes
    # we use permutations from itertools to generate all possible assignments
    # where each box is assigned to a unique goal and vice versa
    goal_permutations = permutations(state.layout.goals, len(state.crates))
    # now goal_permutations is an iterator that generates all possible assignments of goals to boxes

    # Evaluate each permutation to find the one with the minimum total distance
    for goal_permutation in goal_permutations:
        # for each permutation, calculate the total distance
        total_distance = 0
        for box, goal in zip(boxes, goal_permutation):
            total_distance += manhattan_distance(box, goal)
            
        # Update the minimum total distance if the current one is lower
        if total_distance < min_total_distance:
            min_total_distance = total_distance

    return min_total_distance

    

# Stronger heuristic that considers deadlocks and 
# gets the minimum distance from each box to any goal
# and the weak heuristic
def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    #TODO: ADD YOUR CODE HERE
    #IMPORTANT: DO NOT USE "problem.get_actions" HERE.
    # Calling it here will mess up the tracking of the expanded nodes count
    # which is the number of get_actions calls during the search
    #NOTE: you can use problem.cache() to get a dictionary in which you can store information that will persist between calls of this function
    # This could be useful if you want to store the results heavy computations that can be cached and used across multiple calls of this function
    # Heuristic: sum of minimum distances from each crate to any goal
    # NotImplemented()

    if problem.is_goal(state):
        return 0.0  # The state is already a goal state
    
    # # Check for deadlocks
    # if is_deadlock(problem, state):
    #     return float('inf')  # Return a large value if there is a deadlock
    
    # try:
    if is_deadlock(problem, state):
        return float('inf')  # Return a large value if there is a deadlock
    # except:
    #     if dead_end(problem, state):
    #         return float('inf')  # Return a large value if there is a deadlock
    # in case there is no deadlock, calculate the total minimum distance from each box to any goal
    # and the weak heuristic using the helper functions defined above
    return get_best_box_goal_assignment(state) + weak_heuristic(problem, state)