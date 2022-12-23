from vacuumenvironment import ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD
from vacuumenvironment import ACTION_NOP
from headings import NORTH, SOUTH, WEST, EAST

###########################################################
#  A path is a sequence of positions whose first element
#   must be the agent's current position.  To follow a path
#   is to move the agent to the first element in the path,
#   then remove the first element and then continue to follow
    
def begin_path(self, path):
    # Edge case where agent asks for a path to where it is currently
    # located
    if len(path) == 0:
        self.path = []
        return ACTION_NOP
    firstpos = path.pop(0)
    self.path = path
    return move_to_position(self, firstpos)
    
def continue_path(self):
    if len(self.path) == 0:
        return ACTION_NOP
    else:
        return move_to_position(self, self.path.pop(0))
    
    ##################################
    #  Move to an adjacent position.  Depending
    #  on where the position is and the agent's current heading,
    #  this could be FORWARD, or one or two turns followed by FORWARD.
    #
    #  We can queue up all three actions by putting the second and 
    #  third actions on the next_actions list, then they will be
    #  executed next with highest priority in subsequent execute
    #  cycles
    
def move_to_position(self, pos):
    new_heading = heading_for_position(self, pos)
    action = None
    if self.worldmodel.heading == new_heading:
        action = ACTION_FORWARD
    elif (self.worldmodel.heading, new_heading) in [(NORTH, EAST), (EAST, SOUTH), (SOUTH, WEST), (WEST, NORTH)]:
        self.next_actions = [ACTION_FORWARD]
        action =  ACTION_TURN_RIGHT
    elif (self.worldmodel.heading, new_heading) in [(NORTH, WEST), (WEST, SOUTH), (SOUTH, EAST), (EAST, NORTH)]:
        self.next_actions = [ACTION_FORWARD]
        action =  ACTION_TURN_LEFT
    else:
        self.next_actions = [ACTION_TURN_LEFT, ACTION_FORWARD]
        action = ACTION_TURN_LEFT
    return action

    # What does my heading have to be in order to go FORWARD and end up 
    # in new_position
    
def heading_for_position(self, new_position):
    x1, y1 = self.worldmodel.current_position
    x2, y2 = new_position
    newheading = None
    if (x1 < x2):
        newheading =  SOUTH
    elif (x1 > x2):
        newheading = NORTH
    elif (y1 < y2):
        newheading = EAST
    elif (y1 > y2):
        newheading =  WEST 
    else:
        raise(Exception("Bad position argument to heading_for_position"))
    return newheading
