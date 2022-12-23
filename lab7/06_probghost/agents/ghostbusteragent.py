from random import randint

from constants import ACTION_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
from constants import ACTION_STOP, ACTION_NOP
from constants import ACTION_PROBE_GHOST, ACTION_BUST_GHOST
from constants import NORTH, SOUTH, EAST, WEST

from agents.vacuumagent import VacuumAgent
from agents.agentworldmodel import AgentWorldModel
   
class GhostBusterAgent(VacuumAgent):
    def __init__(self, log):
        self.version = "GhostBusterAgent"
        super().__init__(self.version, log, self.execute)
        self.world_model = AgentWorldModel()
        self.next_actions = []
        self.path = []
        self.num_probes = 0
        self.end_action = None
    
    def prep(self, report):
        self.world_model.tell_recon(report)
        
    def execute(self, percept):
        self.pre_update(percept) 
        self.world_model.tell_percepts(percept)
        action = self.choose_action(percept)
        self.world_model.tell_last_action(action)
        self.post_update(action)
        return action
   
    def choose_action(self, percept):
        action = None
        if self.battery_depleted():
            self.log(f"Battery depleted, score is {self.score()}")
            action = ACTION_STOP          
        elif len(self.next_actions) > 0:
            if self.next_actions[0] == ACTION_STOP:
                self.display_execution_status(force=True)
            action = self.next_actions.pop(0)
        elif len(self.path) > 0:
            action = self.continue_path()
        elif self.end_action:
            action = self.end_action
            self.end_action = None
        else:
            action = self.bust_strategy()
        return action
 
    ########################################################
    
    def bust_strategy(self):
        
        # Location of a successful bust, or None if there is none
        bustloc = self.find_good_bust()
        # Location of an Orange or Red probe that hasn't been busted,
        #  or None if there is one
        goodprobe = self.find_good_probe()
        
        if bustloc:
            self.log(f"Successfully busted at {bustloc}, score is {self.score()}")
            return ACTION_STOP
        elif goodprobe:
            return self.bust_at(goodprobe)
        else:
            return self.probe_at(self.random_probe_square())
    
    # Find a bust with status = True;  return the location
    def find_good_bust(self):
        for loc, status in self.world_model.ask_busts().items():
            if status:
                return loc
        return None

    # Find a red or orange probe that has not been busted;  return the location
    def find_good_probe(self):
        bustlocs = list(self.world_model.busts.keys())
        for loc, color in self.world_model.ask_probes().items():
            if color in ["red", "orange"] and loc not in bustlocs:
                return loc
        return None
    
    def random_probe_square(self):
        previous_probes = list(self.world_model.ask_probes().keys())
        while True:
            pos = (randint(1,10), randint(1,10))
            if not (pos in previous_probes):
                return pos
            
    #################################################################
    
    #  Initiate a probe at this location.  First go to the location, then 
    #  execute ACTION_PROBE
    def probe_at(self,loc):
        self.log(f"Going to probe at {loc}")
        self.end_action = ACTION_PROBE_GHOST
        return self.begin_path(self.path_to(loc))
    
    # Initiate a bust at this location.  First go to the location, then 
    #  execute ACTION_BUST
    
    def bust_at(self,loc):
        self.log(f"TRYING A BUST AT {loc}")
        self.end_action = ACTION_BUST_GHOST
        return self.begin_path(self.path_to(loc))

    ################################################################
    #  All code below is about building and following paths from 
    #  one location to another
    
    def path_to(self, location):
        cl = self.world_model.ask_current_location()
        squares = []
        if cl[0] < location[0]:
            squares += [(i, cl[1]) for i in range(cl[0] + 1, location[0]+1)]
        elif cl[0] > location[0]:
            squares += [(i, cl[1]) for i in reversed(range(location[0], cl[0]))]
        if cl[1] < location[1]:
            squares += [(location[0], j) for j in range(cl[1] + 1, location[1]+1)]
        elif cl[1] > location[1]:
            squares += [(location[0], j) for j in reversed(range(location[1], cl[1]))]
        return squares

    ########
    
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
        current_heading = self.world_model.ask_heading()
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