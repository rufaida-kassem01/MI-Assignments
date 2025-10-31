from typing import Any, Dict, Set, Tuple, List
from problem import Problem
from mathutils import Direction, Point
from helpers.utils import NotImplemented

#TODO: (Optional) Instead of Any, you can define a type for the parking state
ParkingState = List[Point] # the state list of cars positions

# An action of the parking problem is a tuple containing an index 'i' and a direction 'd' where car 'i' should move in the direction 'd'.
ParkingAction = Tuple[int, Direction]

# This is the implementation of the parking problem
class ParkingProblem(Problem[ParkingState, ParkingAction]):
    passages: Set[Point]    # A set of points which indicate where a car can be (in other words, every position except walls).
    cars: Tuple[Point]      # A tuple of points where state[i] is the position of car 'i'. 
    slots: Dict[Point, int] # A dictionary which indicate the index of the parking slot (if it is 'i' then it is the lot of car 'i') for every position.
                            # if a position does not contain a parking slot, it will not be in this dictionary.
    width: int              # The width of the parking lot.
    height: int             # The height of the parking lot.

    # This function should return the initial state
    def get_initial_state(self) -> ParkingState:
        # the initial state is the starting positions of all cars
        return list(self.cars) 
    
    # This function should return True if the given state is a goal. Otherwise, it should return False.
    def is_goal(self, state: ParkingState) -> bool:
        for slot_point,car_index in self.slots.items():
        # if any car is not parked in its correct slot, this is not a goal state
            if (slot_point!=state[car_index]): 
                return False 
        
        # If we checked all slots and every car is in its correct place,
        # then the goal is achieved
        return True
    
    # This function returns a list of all the possible actions that can be applied to the given state
    def get_actions(self, state: ParkingState) -> List[ParkingAction]:
        actions=[]

        # loop through every car and its position in the current state
        for car_index,car_pos in enumerate(state):
            # try moving the car in each possible direction (Up, Down, Left, Right)
            for d in Direction:
                new_pos:Point = car_pos+d.to_vector()
                
            # Check if the new position is valid:
            # 1. it must be a passage cell
            # 2. it must stay within the parking lot boundaries
            # 3. it must be free slot
                if new_pos in self.passages and new_pos.x>-1 and new_pos.y>-1 and new_pos.x<self.width and new_pos.y<self.height and new_pos not in state:
                    actions.append((car_index,d))  
        return actions
    
    # This function returns a new state which is the result of applying the given action to the given state
    def get_successor(self, state: ParkingState, action: ParkingAction) -> ParkingState:
        new_state=list(state)
        car_index,direction=action
        # update the car’s position by moving it one step in the chosen direction
        new_state[car_index]=state[car_index]+direction.to_vector()
        return new_state
    
    # This function returns the cost of applying the given action to the given state
    def get_cost(self, state: ParkingState, action: ParkingAction) -> float:
        car_index,direction=action
        cost = 26.0 - car_index # cost increases linearly with rank 
        return cost
    
     # Read a parking problem from text containing a grid of tiles
    @staticmethod
    def from_text(text: str) -> 'ParkingProblem':
        passages =  set()
        cars, slots = {}, {}
        lines = [line for line in (line.strip() for line in text.splitlines()) if line]
        width, height = max(len(line) for line in lines), len(lines)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != "#":
                    passages.add(Point(x, y))
                    if char == '.':
                        pass
                    elif char in "ABCDEFGHIJ":
                        cars[ord(char) - ord('A')] = Point(x, y)
                    elif char in "0123456789":
                        slots[int(char)] = Point(x, y)
        problem = ParkingProblem()
        problem.passages = passages
        problem.cars = tuple(cars[i] for i in range(len(cars)))
        problem.slots = {position:index for index, position in slots.items()}
        problem.width = width
        problem.height = height
        return problem

    # Read a parking problem from file containing a grid of tiles
    @staticmethod
    def from_file(path: str) -> 'ParkingProblem':
        with open(path, 'r') as f:
            return ParkingProblem.from_text(f.read())