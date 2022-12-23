from constants import ACTION_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
from constants import ACTION_STOP, ACTION_NOP
from constants import ACTION_PROBE_GHOST, ACTION_BUST_GHOST
from constants import NORTH, SOUTH, EAST, WEST

from agents.vacuumagent import VacuumAgent
from agents.bayesianagentworldmodel import BayesianAgentWorldModel

class BayesianGhostBusterAgent(VacuumAgent):
    def __init__(self, log):
        self.version = "BayesianGhostBustingAgent"
        super().__init__(self.version, log, self.execute)
        self.world_model = BayesianAgentWorldModel()
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
        else:
            if len(self.next_actions) > 0:
                if self.next_actions[0] == ACTION_STOP:
                    self.display_execution_status(force=True)
                action = self.next_actions.pop(0)
            elif len(self.path) > 0:
                action = self.continue_path()
            elif self.end_action:
                action = self.end_action
                self.end_action = None
            elif self.world_model.successful_bust():
                self.log(f"Successful bust!   Finished with score {self.score()}")
                return ACTION_STOP
            else:
                action = self.bust_strategy()
        return action
 
    ################################ 

   # If sucky should bust (somewhere), return that square.
   # If there is nowhere promising to bust, return None
    def suckyShouldBust(self):
        # Your code here
        return None
    
    def bust_strategy(self):
        sorted_coords = self.world_model.sorted_coords()
        busted_coords = self.world_model.busts
        probed_coords = self.world_model.probes
        
        # Define the variable busted here -- the list of unbusted coordinates, sorted in descending order of probability 
        unbusted = None
        # Define the variable unprobed here -- the list of unprobed coordinates, sorted in descending order of probability 
        unprobed = None
    
        bustSquare = self.suckyShouldBust()
        if bustSquare:
            self.log(f"GOING TO BUST at {unbusted[0][0]}, probability is " + "{:.2f}".format(unbusted[0][1]))
            return self.bust_at(bustSquare)
        if len(unprobed) > 0:
            self.log(f"Going to probe at {unprobed[0][0]}, probability is " + "{:.2f}".format(unprobed[0][1]))
            return self.probe_at(unprobed[0][0])
        if len(unbusted) > 0:
            self.log("No unprobed squares, and no good busts.  Busting at random!")
            return self.bust_at(unbusted[0][0])
        else:
            raise(Exception("No unbusted squares, WTF?"))
        
    def probe_at(self,loc):
        self.num_probes += 1
        self.end_action = ACTION_PROBE_GHOST
        return self.begin_path(self.path_to(loc))
    
    def bust_at(self,loc):
        self.end_action = ACTION_BUST_GHOST
        return self.begin_path(self.path_to(loc))      
  
    ########
 
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