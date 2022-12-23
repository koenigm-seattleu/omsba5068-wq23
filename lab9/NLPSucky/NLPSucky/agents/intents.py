from vacuumenvironment import ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD
from vacuumenvironment import ACTION_SUCK
from vacuumenvironment import ACTION_MINE_GOLD, ACTION_UNLOAD_GOLD
from vacuumenvironment import ACTION_STOP
from agents.agentworldmodel import GOLD, DIRT
from agents.paths import path_to_position, path_to_any, path_to_exactly, path_from_to_position

STOP = [('actions', [ACTION_STOP])]

#############################
#  Information intents
#    agent information
#    find some dirt
#    find some gold

def intent_agent_info(self):
    self.log(f"I am at {self.worldmodel.current_position} and I am heading {self.worldmodel.heading}")
    batpct = "{:.2%}".format(self.agent.battery_level/self.agent.battery_capacity)
    self.log(f"My battery level is at {batpct}")
    self.log(f"My score is {self.agent.score()}")
    self.log(f"I am holding {self.agent.num_gold} gold and {self.agent.num_dirt} dirt")
    return STOP

def intent_find_objtype(self, objtype):
   squares = self.worldmodel.squares_with_state(objtype)
   if len(squares) == 0:
        self.log(f"There is no {objtype} that I know of.")
   else:
        self.log(f"There is some {objtype} at {squares[0]}.  Would you like me to get it for you?")
   return STOP 

def intent_find_dirt(self):
    return intent_find_objtype(self, DIRT)

def intent_find_gold(self):
    return intent_find_objtype(self, GOLD)

###################################
#  Turning and moving

def intent_turn(self, dir):
    self.log(f"Turning {dir}")
    actions = []
    if dir == 'left':
        actions = [ACTION_TURN_LEFT]
    elif dir == 'right':
        actions = [ACTION_TURN_RIGHT]
    elif dir == 'around':
        actions = [ACTION_TURN_LEFT, ACTION_TURN_LEFT]
    else:
        raise(Exception("Bad direction {dir}"))
    return [('actions', actions)]
       
def intent_forward_backward(self, fb, num):
    self.log(f"Moving {fb} {num} spaces")
    actions = []
    if fb == 'backward':
        actions += [ACTION_TURN_LEFT, ACTION_TURN_LEFT]
    actions += [ACTION_FORWARD] * num
    actions.append(ACTION_STOP)
    return [('actions', actions)]

#########################################
#  Goto
#    Go to a coordinate
#    Go home

def intent_goto(self, coord):
    if self.worldmodel.current_position == coord:
        self.log(f"I am already at {coord}")
        return STOP
    self.log(f"Going to {coord}")
    return [('path', path_to_position(self, coord))]

def intent_go_home(self):
    self.log("Going home")
    p = path_to_position(self, (1,1))
    return [('path', p), ('actions', [ACTION_STOP])]

###########################################
#  Dirt sucking
#    at a coordinate
#    find and suck
    
def intent_suck_dirt_at(self, coord):
    self.log(f"Sucking dirt at {coord}")
    if self.worldmodel.state_at(coord) != DIRT:
        self.log(f"There is no dirt at {coord}!")
        return STOP
    else:
        p = path_to_position(self, coord)
        if not p:
            self.log(f"There is no path from here to {coord}")
            return STOP
        else:
            return [('path', p), 
                    ('actions', [ACTION_SUCK, ACTION_STOP])]

def intent_suck_some_dirt(self):
    p = path_to_any(self, DIRT)
    if p == None:
        return [('explore_dirt')]
    elif len(p) == 0:
        return intent_suck_dirt_at(self, self.worldmodel.current_position)
    else:
        return intent_suck_dirt_at(self, p[-1])
    
########################################
#   Gold getting (mine, return home, unload)
#     at a known coordinate
#     find and get gold
    
def intent_get_gold_at(self, coord):
    self.log(f"Getting gold at {coord}")
    if self.worldmodel.state_at(coord) != GOLD:
        self.log(f"There is no gold at {coord}!")
        return STOP
    else:
        p = path_to_position(self, coord)
        if not p:
            self.log(f"There is no path from here to {coord}")
            return STOP
        else:
            p2 = path_from_to_position(self, coord, (1,1))
            return [('path', p), 
                    ('actions', [ACTION_MINE_GOLD]),
                    ('path', p2), 
                    ('actions', [ACTION_UNLOAD_GOLD, ACTION_STOP])]
            
def intent_get_some_gold(self):
    p = path_to_exactly(self, GOLD)
    if not p:
        self.log(f"There is no gold available!")
        return STOP
    else:
        return intent_get_gold_at(self, p[-1])

#########################################
#  If all else fails
    
def intent_unknown(self):
    self.log(f"Hmmm ... I don't know what to do about that")
    return STOP

