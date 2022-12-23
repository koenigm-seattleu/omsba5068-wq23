from constants import NORTH, SOUTH, EAST, WEST
from constants import LEFT, RIGHT, FORWARD
from constants import ACTION_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
 
class AgentWorldModel:
    def __init__(self):
        self.current_location = None
        self.heading = None
        self.last_action = None
        self.ghost_found = False
        self.probes = {}
        self.busts = {}
        
    def tell_recon(self, recon):
        self.current_location = recon['position']
        self.heading = recon['heading']
        
    # Percepts are BUMP (should be impossible)
    #  PROBE  (color)
    #  BUST  (True or False whether the BUST succeeded)
    
    def tell_percepts(self, percepts):
        bump = percepts.attributes['bump']
        probe = percepts.attributes.get('probe', None)
        bust = percepts.attributes.get('bust', None)
        r,c = self.current_location
        if probe != None:
            self.probes[self.current_location] = probe
        if bust != None:
            self.busts[self.current_location] = bust
        if self.last_action == ACTION_FORWARD and bump:
            raise(Exception("Why did I bump into a wall?"))
        elif self.last_action == ACTION_FORWARD and not bump:
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
    
    # Probes is a dictionary.  Keys are locations (3,2) for example, values
    # are the values returned by the probe:  RED, ORANGE, YELLOW, GREEN
    def ask_probes(self):
        return self.probes
    
    # Busts is a dictionary.  Keys are locations (3,2) for example, value
    # is True or False depending on whether the bust succeeded
    
    def ask_busts(self):
        return self.busts
    
#######################################################
# Helpers for navigating the grid -- used to update 
# heading and position if the agent executes FORWARD or TURN

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
