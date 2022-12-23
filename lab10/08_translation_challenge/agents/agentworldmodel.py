from constants import UNKNOWN, WALL, CLEAN, DIRT, GOLD
from constants import NORTH, SOUTH, EAST, WEST
from constants import LEFT, RIGHT, FORWARD, BACKWARD
from constants import ACTION_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
from constants import ACTION_MINE_GOLD, ACTION_UNLOAD_GOLD
from constants import ACTION_SUCK
                
class AgentWorldModel:
    def __init__(self):
        self.current_location = None
        self.heading = None
        self.last_action = None
        self.num_gold = 0
    
    def tell_recon(self, recon):
        height = recon['height']
        width = recon['width']
        self.current_location = recon['position']
        self.heading = recon['heading']
        self.squares = [[UNKNOWN for _ in range(height)] for _ in range(width)]
        if 'walls' in recon:
            for square in recon['walls']:
                r, c = square
                self.squares[r][c] = WALL
        if 'gold' in recon:
            for square in recon['gold']:
                r, c = square
                self.squares[r][c] = GOLD
        if 'dirt' in recon:
            for square in recon['dirt']:
                r, c = square
                self.squares[r][c] = DIRT
        
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
        elif self.last_action == ACTION_MINE_GOLD and self.ask_state_at(self.current_location) == GOLD:
            r,c = self.current_location
            self.squares[r][c] = CLEAN
            self.num_gold += 1
        elif self.last_action == ACTION_UNLOAD_GOLD and self.current_location == (1,1):
            self.num_gold -= 1
        r,c = self.current_location
        if dirt:
            self.squares[r][c] = DIRT 
        if self.squares[r][c] == UNKNOWN and not dirt:
            self.squares[r][c] = CLEAN
 
    def tell_action(self, action):
        self.last_action = action
        if action == ACTION_SUCK:
            r,c = self.current_location
            self.squares[r][c] = CLEAN
        
    def ask_last_action(self):
        return self.last_action
    
    def ask_state_here(self):
        return self.ask_state_at(self.current_location)
    
    def ask_adjacent_squares(self):
        r,c = self.current_location
        return [(r, c+1), (r, c-1), (r+1, c), (r-1, c)]
    
    def ask_state_at(self, location):
        return self.squares[location[0]][location[1]]
    
    def ask_state_in_direction(self, direction):
        return self.ask_state_at(self.square_in_direction(direction))
    
    def ask_current_location(self):
        return self.current_location
    
    def ask_current_heading(self):
        return self.heading
    
    def ask_num_gold(self):
        return self.num_gold
    
    def ask_squares_with_type(self, sqtype):
        squares = []
        height = len(self.squares)
        width = len(self.squares[0])
        for r in range(0, height):
            for c in range(0, width):
                if self.squares[r][c] == sqtype:
                    squares.append((r,c))
        return squares  
    
    def ask_free_squares(self):
        squares = []
        height = len(self.squares)
        width = len(self.squares[0])
        for r in range(0, height):
            for c in range(0, width):
                if self.squares[r][c] != WALL:
                    squares.append((r,c))
        return squares
    
    def square_in_direction(self, direction):
        return square_at_heading(self.current_location,
                                 heading_in_direction(self.heading, direction))
    
#######################################################
# Helpers for navigating the grid

def heading_in_direction(heading, direction):
    if direction == FORWARD:
        return heading
    headings = {NORTH: {LEFT: WEST, RIGHT: EAST, BACKWARD: SOUTH},
                SOUTH: {LEFT: EAST, RIGHT: WEST, BACKWARD: NORTH},
                EAST:  {LEFT: NORTH, RIGHT: SOUTH, BACKWARD: WEST},
                WEST:  {LEFT: SOUTH, RIGHT: NORTH, BACKWARD: EAST}}
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
