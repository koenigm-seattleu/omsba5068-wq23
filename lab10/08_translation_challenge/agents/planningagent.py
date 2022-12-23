from constants import ACTION_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
from constants import ACTION_STOP, ACTION_NOP
from constants import ACTION_SUCK

from constants import DIRT
from constants import NORTH, SOUTH, EAST, WEST

from agents.vacuumagent import VacuumAgent
from agents.agentworldmodel import AgentWorldModel

from agents.shortestpath import shortest_path

class OmniscientAgent(VacuumAgent):
    def __init__(self, log):
        self.version = "OmniscientAgent"
        super().__init__(self.version, log, self.execute)
        self.world_model = AgentWorldModel()
        self.next_actions = []
        self.path = []
    
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
                if self.next_actions[0] == ACTION_STOP:
                    self.display_execution_status(force=True)
                action = self.next_actions.pop(0)
            elif len(self.path) > 0:
                action = self.continue_path()
            elif self.world_model.ask_state_here() == DIRT:
                action = ACTION_SUCK
            else:
                path = self.path_to_dirt()
                if path:
                    #self.log(f"About to get the dirt at {path[-1]}")
                    return self.begin_path(path)
                else:
                    #self.log(f"No more dirt, stopping")
                    #self.display_execution_status(force=True)
                    return ACTION_STOP
        return action
    
    ########
    
    def path_to_home(self):
        return self.path_to((1,1))
    
    def path_to_dirt(self):
        for dirt in self.world_model.ask_squares_with_type(DIRT):
            p = self.path_to(dirt)
            if p:
                return p
        return None
        
    def path_to(self, location):
        return shortest_path(self.world_model.ask_current_location(), 
                         location, 
                         self.world_model.ask_free_squares())
        
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
        current_heading = self.world_model.heading
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

    #########
    
    def begin_path(self, path):
        if path == None:
            self.log("Trying to begin a null plan -- stopping!")
            return ACTION_STOP
        if len(path) == 0:
            self.path = []
            return ACTION_NOP
        firstpos = path.pop(0)
        self.path = path
        return self.move_to_adjacent_square(firstpos)
    
    def continue_path(self):
        if len(self.path) == 0:
            return ACTION_NOP
        else:
            return self.move_to_adjacent_square(self.path.pop(0))