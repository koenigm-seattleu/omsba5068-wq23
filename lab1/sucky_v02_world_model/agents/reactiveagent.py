from agents.vacuumagent import VacuumAgent
from constants import ACTION_STOP
from constants import ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD, ACTION_SUCK
from random import choice

class NoSenseAgent(VacuumAgent):
    def __init__(self, log):
        self.version = "NoSense"
        super().__init__(self.version, log, self.execute)
    
    def prep(self, report):
        pass
        
    def execute(self, percept):
        self.pre_update(percept) 
        action = self.choose_action()
        self.post_update(action)
        return action
   
    def choose_action(self):
        action = None
        if self.battery_depleted():
            self.log(f"Battery depleted, score is {self.score()}")
            action = ACTION_STOP          
        else:
            action = choice([ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD, ACTION_SUCK])
        return action
  
#####################################################

class SenseDirtAgent(VacuumAgent):
    def __init__(self, log):
        self.version = "SenseDirtAgent"
        super().__init__(self.version, log, self.execute)
    
    def prep(self, report):
        pass
        
    def execute(self, percept):
        self.pre_update(percept) 
        action = self.choose_action(percept)
        self.post_update(action)
        return action
   
    def choose_action(self, percept):
        action = None
        if self.battery_depleted():
            self.log(f"Battery depleted, score is {self.score()}")
            action = ACTION_STOP          
        else:
            dirt_here = percept.attributes['dirt']
            if dirt_here:
                action = ACTION_SUCK
            else:
                action = choice([ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD])
        return action