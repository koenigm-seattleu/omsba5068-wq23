from constants import NORTH, SOUTH, EAST, WEST
from constants import LEFT, RIGHT, FORWARD
from constants import ACTION_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT

#  GhostProbs module
#    -- GhostProbs() 
from agents.ghostprobs import GhostProbs

class BayesianAgentWorldModel:
    def __init__(self):
        self.current_location = None
        self.heading = None
        self.last_action = None
        # All Bayesian updates happen in this module.  The module
        # can update and report on the ghost probably of all squares
        self.ghost_probs = GhostProbs(None, size=10)
        # Squares we have previously probed, and the color
        self.probes = {}
        # Squares we have previously busted, and whether or not the bust was successful
        self.busts = {}
    
    def sorted_coords(self):
        return self.ghost_probs.sorted_coords()
     
    def successful_bust(self):
        for loc, status in self.busts.items():
            if status:
                return loc
        return None
    
    def tell_recon(self, recon):
        self.current_location = recon['position']
        self.heading = recon['heading']
        
    def tell_percepts(self, percepts):
        probe = percepts.attributes.get('probe', None)
        bust = percepts.attributes.get('bust', None)
        r,c = self.current_location
        if probe != None:
            self.probes[self.current_location] = probe
            self.ghost_probs.update_probe((probe, self.current_location))
        if bust != None:
            self.busts[self.current_location] = bust
            self.ghost_probs.update_bust((bust, self.current_location))
        elif self.last_action == ACTION_FORWARD:
            self.current_location = square_at_heading(self.current_location, self.heading)
        elif self.last_action == ACTION_TURN_LEFT:
            self.heading = heading_in_direction(self.heading, LEFT)
        elif self.last_action == ACTION_TURN_RIGHT:
            self.heading = heading_in_direction(self.heading, RIGHT)
 
    def tell_last_action(self, action):
        self.last_action = action
           
    def ask_current_location(self):
        return self.current_location
    
    def ask_heading(self):
        return self.heading
    
#######################################################
# Helpers for navigating the grid.  Nothing new here

def heading_in_direction(heading, direction):
    if direction == FORWARD:
        return heading
    headings = {NORTH: {LEFT: WEST, RIGHT: EAST},
                SOUTH: {LEFT: EAST, RIGHT: WEST},
                EAST:  {LEFT: NORTH, RIGHT: SOUTH},
                WEST:  {LEFT: SOUTH, RIGHT: NORTH}}
    return headings[heading][direction]

def square_at_heading(square, heading):
    r, c = square
    if heading == NORTH:
        return (r-1, c)
    elif heading == SOUTH:
        return (r+1,c)
    elif heading == WEST:
        return (r, c-1)
    elif heading == EAST:
        return (r, c+1)
    else:
        raise(Exception(f"Bad heading {heading}"))
