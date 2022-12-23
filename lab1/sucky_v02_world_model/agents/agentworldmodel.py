from constants import UNKNOWN, WALL, CLEAN, DIRT
from constants import NORTH, SOUTH, EAST, WEST
from constants import LEFT, RIGHT, FORWARD
from constants import ACTION_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
                
class AgentWorldModel:
    def __init__(self):
        self.current_location = None
        self.heading = None
        self.last_action = None
    
    def tell_recon(self, recon):
        height = recon['height']
        width = recon['width']
        self.current_location = recon['position']
        self.heading = recon['heading']
        self.squares = [[UNKNOWN for _ in range(height)] for _ in range(width)]
        
    def tell_percepts(self, percepts):
        dirt = percepts.attributes['dirt']
        bump = percepts.attributes['bump']
        if self.last_action == ACTION_FORWARD and bump:
            rn, cn = square_at_heading(self.current_location, self.heading)
            self.squares[rn][cn] = WALL
        elif self.last_action == ACTION_FORWARD and not bump:
            self.current_location = square_at_heading(self.current_location, self.heading)
        elif self.last_action == ACTION_TURN_LEFT:
            self.heading = heading_in_direction(self.heading, LEFT)
        elif self.last_action == ACTION_TURN_RIGHT:
            self.heading = heading_in_direction(self.heading, RIGHT)
        r,c = self.current_location
        self.squares[r][c] = DIRT if dirt else CLEAN
 
    def tell_action(self, action):
        self.last_action = action
        
    def ask_last_action(self):
        return self.last_action
    
    def ask_state_here(self):
        return self.ask_state_at(self.current_location)
    
    def ask_at_home(self):
        return self.current_location == (1,1)
    
    def ask_state_at(self, location):
        return self.squares[location[0]][location[1]]
    
    def ask_state_in_direction(self, direction):
        return self.ask_state_at(self.square_in_direction(direction))
    
    def square_in_direction(self, direction):
        return square_at_heading(self.current_location,
                                 heading_in_direction(self.heading, direction))
    
#######################################################
# Helpers for navigating the grid

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

        
        
        