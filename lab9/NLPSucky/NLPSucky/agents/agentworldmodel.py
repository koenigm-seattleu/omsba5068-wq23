# -*- coding: utf-8 -*-
from vacuumenvironment import ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD
from vacuumenvironment import ACTION_SUCK, ACTION_UNSUCK, ACTION_NOP, ACTION_STOP
from vacuumenvironment import ACTION_MINE_GOLD, ACTION_UNLOAD_GOLD
from headings import NORTH, SOUTH, EAST, WEST

# Each square is in one of these states
UNKNOWN = "Unknown"
WALL = "Wall"
CLEAN = "Clean"
DIRT = "Dirt"
GOLD = "Gold"

# Direction (turn)
FORWARD = "Forward"
LEFT = "Left"
RIGHT = "Right"

"""
Internal world model of a vacuum agent
"""

# Agent world is the world dimensions, the agent's current position and heading, 
# and the state of every square in the world.

class AgentWorldModel:

    def __init__(self, width, height):
        self.world = None
        self.last_action = ACTION_NOP
        self.total_actions = 0
        self.heading = None
        self.current_position = None
        self.width = None
        self.height = None
        self.num_golds = 0
        self.num_dirts = 0
   
    ###########  Access / set state of squares #########################
    
    def inbounds(self, pos):
        x, y = pos
        return x > 0 and x < self.width-1 and y > 0 and y < self.height - 1
    
    def get_world_state(self, pos):
        x, y = pos
        return self.world[x][y]
    
    def set_world_state(self, pos, newstate):
        x, y = pos
        self.world[x][y] = newstate
     
   ##### Initialization / Prep / Reconaissance
   ##  This is called prior to execution to provide information about the 
   ##  world.  It should at least include the size of the world, and the 
   ##  agent's initial position and heading.
   ##  It might contain full or partial information about square status
   
    def prep(self, recon):
        # These are required
        self.width = recon["width"]
        self.height = recon["height"]
        self.current_position = recon["position"]
        self.heading = recon["heading"]
        
        self.world = [[UNKNOWN for _ in range(self.height)] for _ in range(self.width)]
		
        # This is recon for total information agent -- state of 
        # all walls, dirt, and gold is given, so every other square
        # is known to be CLEAN
        
        if "walls" in recon:
            for p in recon["walls"]:
                self.world[p[0]][p[1]] = WALL
        if "dirt" in recon:
            for p in recon["dirt"]:
                self.world[p[0]][p[1]] = DIRT
        if "gold" in recon:
            for p in recon["gold"]:
                self.world[p[0]][p[1]] = GOLD
        #FIXME:  this is the wrong way to say "I know about everything that could be in a square"
        if "dirt" in recon and "walls" in recon and "gold" in recon:
            for x in range(0, self.width):
                for y in range(0, self.height):
                    if self.world[x][y] == UNKNOWN:
                        self.world[x][y] = CLEAN
    
    ##########  Update model based on actions #####################
    
    # This method must be prior to action selection to update world model
    # based on latest percepts

    def update(self, dirt, bump):
        if self.last_action in [ACTION_NOP, ACTION_STOP]:
            pass
        elif self.last_action == ACTION_SUCK:
            self.num_dirts += 1
            self.set_world_state(self.current_position, CLEAN)
        elif self.last_action == ACTION_UNSUCK:
            if self.num_dirt > 0:
                self.num_dirts -= 1
                self.set_world_state(self.current_position, DIRT)
        elif self.last_action == ACTION_TURN_LEFT:
            self.update_heading(LEFT)
        elif self.last_action == ACTION_TURN_RIGHT:
            self.update_heading(RIGHT)
        elif self.last_action == ACTION_FORWARD:
            self.forward(dirt, bump)
        elif self.last_action == ACTION_MINE_GOLD:
            if self.state() == GOLD and self.num_golds < 2:
                self.num_golds += 1
                self.set_world_state(self.current_position, CLEAN)
        elif self.last_action == ACTION_UNLOAD_GOLD:
            if self.num_golds > 0:
                self.num_golds -= 1
        else:
            raise(Exception(f"Bad last action {self.last_action}"))
            
     # This method must be called after an action is selected
    def update_action(self, action):
        self.total_actions += 1
        self.last_action = action
        
    # Helper: update position and square status for a FORWARD action        
    def forward(self, dirt, bump):
        new_pos = self.new_position(self.current_position, self.heading)
        if bump:
            self.set_world_state(new_pos, WALL)
        else:
            self.current_position = new_pos
            if self.get_world_state(new_pos) == UNKNOWN:
                self.set_world_state(self.current_position, DIRT if dirt else CLEAN)
                
    # Helper: update heading based on a TURN action
    def update_heading(self, direction):
        if direction == LEFT:
            self.heading = {NORTH: WEST, WEST: SOUTH, SOUTH: EAST, EAST:NORTH}[self.heading]
        elif direction == RIGHT:
            self.heading = {NORTH: EAST, EAST: SOUTH, SOUTH: WEST, WEST:NORTH}[self.heading]
        else:
            raise(f"Bad turn direction: {direction}")

    ######################################################################
    ##  These methods help the agent in action choice
   
    def state_at(self, pos):
        return self.get_world_state(pos)
    
    def state(self):
        return self.get_world_state(self.current_position)
    
    ###  Where will I be if I move forward given my heading and 
    ###  assuming no wall
          
    def new_position(self, pos, heading):
        x,y = pos
        new_x = {NORTH: x-1, SOUTH: x+1, WEST: x, EAST: x}[heading]
        new_y = {NORTH: y, SOUTH: y, WEST: y - 1, EAST: y + 1}[heading]
        return (new_x, new_y)
 
    # What is the state of the square if I move in a direction
    def state_in_direction(self, direction):
        new_heading = self.heading_in_direction(direction)
        newpos = self.new_position(self.current_location, new_heading)
        return self.get_world_state(newpos)
    
    def state_in_heading(self, heading):
        newpos = self.new_position(self.current_position, heading)
        return self.get_world_state(newpos)
    
    # What is the state of the square if I move forward?
    def state_forward(self):
        return self.state_in_direction(FORWARD)
    
    def heading_in_direction(self, direction):
        if direction == FORWARD:
            return self.heading
        elif direction == LEFT:
            return {NORTH: WEST, WEST: SOUTH, SOUTH: EAST, EAST: NORTH}[self.heading]
        elif direction == RIGHT:
            return {NORTH: EAST, EAST: SOUTH, SOUTH: WEST, WEST: NORTH}[self.heading]
        else:
            raise (f"Bad direction {direction}")
            
    ##########################################################
 
    def squares_with_state(self, state):
        squares = []
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.world[x][y] == state:
                    squares.append((x,y))
        return squares
    
    def squares_without_walls(self):
        squares = []
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.world[x][y] != WALL:
                    squares.append((x,y))
        return squares
                
        

 