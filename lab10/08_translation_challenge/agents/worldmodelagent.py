from constants import ACTION_FORWARD, ACTION_SUCK, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
from constants import ACTION_STOP
from constants import WALL, DIRT, UNKNOWN
from constants import NORTH, SOUTH, EAST, WEST

from agents.vacuumagent import VacuumAgent
from random import choice
from agents.agentworldmodel import AgentWorldModel

class WorldModelAgent(VacuumAgent):
    def __init__(self, log):
        self.version = "WorldModelAgent"
        super().__init__(self.version, log, self.execute)
        self.world_model = AgentWorldModel()
        self.next_actions = []
    
    def prep(self, report):
        self.world_model.tell_recon(report)
        
    def execute(self, percept):
        self.pre_update(percept) 
        self.world_model.tell_percepts(percept)
        action = self.choose_action(percept)
        self.world_model.tell_action(action)
        self.post_update(action)
        return action
    
    def choose_action(self, percept):
        action = None
        if self.battery_depleted():
            #self.log(f"Battery depleted, score is {self.score()}")
            action = ACTION_STOP          
        else:
            if len(self.next_actions) > 0:
                 action = self.next_actions.pop(0)
            elif self.world_model.ask_state_here() == DIRT:
                action = ACTION_SUCK
            else:
                opens = [sq for sq in self.world_model.ask_adjacent_squares()\
                             if self.world_model.ask_state_at(sq) != WALL]
                new = [sq for sq in opens\
                             if self.world_model.ask_state_at(sq) == UNKNOWN]
                if len(new) > 0:
                    action = self.move_to_adjacent_square(choice(new))
                elif len(opens) > 0:
                    action = self.move_to_adjacent_square(choice(opens))
                else:
                    #self.log("No open squares! Stopping")
                    action = ACTION_STOP
                    
        return action
    
   ########
    
    def move_to_adjacent_square(self, pos):
        
        def heading_for_square(new_square):
            my_square = self.world_model.current_location
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
