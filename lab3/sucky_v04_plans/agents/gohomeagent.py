from constants import ACTION_FORWARD, ACTION_SUCK, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
from constants import ACTION_STOP
from constants import WALL, DIRT, UNKNOWN
from constants import NORTH, SOUTH, EAST, WEST

from agents.vacuumagent import VacuumAgent
from agents.agentworldmodel import AgentWorldModel
from random import randint, choice

# Not used at the moment, this will import your path-finding code
from agents.shortestpath import shortest_path

class GoHomeAgent(VacuumAgent):
    def __init__(self, log):
        global GO_HOME_BATTERY_THRESHOLD
        self.version = "GoHomeAgent"
        super().__init__(self.version, log, self.execute)
        self.world_model = AgentWorldModel()
        self.next_actions = []
        self.going_home = False
        self.go_home_battery_threshold = self.battery_capacity * 0.25
        self.displayed_going_home = False
    
    def prep(self, report):
        self.world_model.tell_recon(report)
        
    def execute(self, percept):
        self.pre_update(percept) 
        self.world_model.tell_percepts(percept)
        action = self.choose_action(percept)
        self.world_model.tell_action(action)
        self.post_update(action)
        return action
   
    def battery_low(self):
        return self.battery_level < self.go_home_battery_threshold
    
    def choose_action(self, percept):
        action = None
        if self.battery_depleted():
            self.log(f"Battery depleted, score is {self.score()}")
            action = ACTION_STOP          
        elif len(self.next_actions) > 0:
            action = self.next_actions.pop(0)
        elif self.battery_low() and self.world_model.ask_current_location() == (1,1):
            self.log(f"Arrived home with low battery;  stopping")
            action = ACTION_STOP
        elif self.battery_low():
            action = self.go_home_mode()
        else:
            action = self.explore_mode()
        return action
            
    def explore_mode(self):
        action = None
        if self.world_model.ask_state_here() == DIRT:
            action = ACTION_SUCK
        else:
            opens = [sq for sq in self.world_model.ask_adjacent_squares()\
                     if self.world_model.ask_state_at(sq) != WALL]
            new = [sq for sq in opens\
                   if self.world_model.ask_state_at(sq) == UNKNOWN]
            if len(new) == 0:
                action = self.move_to_adjacent_square(choice(opens))
            else:
                action = self.move_to_adjacent_square(choice(new))
        return action
    
    ########
    
    def go_home_mode(self):
        if not self.displayed_going_home:
            self.log(f"Going home, battery is {self.battery_level}, capacity is {self.battery_capacity}, threshold is {self.go_home_battery_threshold}")
            self.displayed_going_home = True
        action = None
        if self.world_model.ask_state_at_heading(NORTH) != WALL:
            action = self.move_to_heading(NORTH)
        elif self.world_model.ask_state_at_heading(WEST) != WALL:
            action = self.move_to_heading(WEST)
        else:
            r= randint(1,2)
            direction = None
            if r == 1:
               direction = "south" if self.world_model.ask_state_at_heading(SOUTH) != WALL else "east"
            else:
                direction = "east" if self.world_model.ask_state_at_heading(SOUTH) != WALL else "south"
            action = self.move_to_heading(SOUTH) if direction == "south" else self.move_to_heading(EAST)
        return action
  
    def move_to_adjacent_square(self, pos):   
        def heading_for_square(new_square):
            my_square = self.world_model.ask_current_location()
            if (my_square[0] < new_square[0]):
                return SOUTH
            elif (my_square[0] > new_square[0]):
                return NORTH
            elif (my_square[1] < new_square[1]):
                return EAST
            elif (my_square[1] > new_square[1]):
                return WEST 
            else:
                raise(Exception("Bad argument to heading_for_square"))         
        new_heading = heading_for_square(pos)
        action = None
        current_heading = self.world_model.ask_current_heading()
        if current_heading == new_heading:
            action = ACTION_FORWARD
        elif (current_heading, new_heading) in [(NORTH, EAST), (EAST, SOUTH), (SOUTH, WEST), (WEST, NORTH)]:
            self.next_actions = [ACTION_FORWARD]
            action =  ACTION_TURN_RIGHT
        elif (current_heading, new_heading) in [(NORTH, WEST), (WEST, SOUTH), (SOUTH, EAST), (EAST, NORTH)]:
            self.next_actions = [ACTION_FORWARD]
            action =  ACTION_TURN_LEFT
        else:
            self.next_actions = [ACTION_TURN_LEFT, ACTION_FORWARD]
            action = ACTION_TURN_LEFT
        return action
    
    def move_to_heading(self, heading):
        turns = self.turns_to_heading(heading)
        actions = turns + [ACTION_FORWARD]
        first_action = actions.pop(0)
        self.next_actions = actions
        return first_action
    
    def turns_to_heading(self, new_heading):
        turns = {(NORTH, NORTH): [], (NORTH, EAST): [ACTION_TURN_RIGHT], (NORTH, SOUTH): [ACTION_TURN_RIGHT, ACTION_TURN_RIGHT], (NORTH, WEST): [ACTION_TURN_LEFT],
                 (EAST, EAST): [], (EAST, NORTH): [ACTION_TURN_RIGHT], (EAST, WEST): [ACTION_TURN_RIGHT, ACTION_TURN_RIGHT], (EAST, SOUTH): [ACTION_TURN_LEFT],
                 (SOUTH, SOUTH): [], (SOUTH, WEST): [ACTION_TURN_RIGHT], (SOUTH, NORTH): [ACTION_TURN_RIGHT, ACTION_TURN_RIGHT], (SOUTH, EAST): [ACTION_TURN_LEFT],
                 (WEST, WEST): [], (WEST, NORTH): [ACTION_TURN_RIGHT], (WEST, EAST): [ACTION_TURN_RIGHT, ACTION_TURN_RIGHT], (WEST, SOUTH): [ACTION_TURN_LEFT]}
        return turns[(self.world_model.ask_current_heading(), new_heading)]
