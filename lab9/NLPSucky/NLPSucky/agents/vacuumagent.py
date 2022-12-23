# -*- coding: utf-8 -*-

from agent import Agent
from vacuumenvironment import ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD
from vacuumenvironment import ACTION_SUCK, ACTION_UNSUCK
from vacuumenvironment import ACTION_SENSE_GOLD, ACTION_MINE_GOLD, ACTION_UNLOAD_GOLD
from vacuumenvironment import ACTION_NOP, ACTION_STOP

DIRT_REWARD = 10
GOLD_REWARD = 100

# Print a log message after this many iterations
REPORT_INTERVAL = 500

BATTERY_CONSUMPTION = {ACTION_TURN_LEFT: 1,
                       ACTION_TURN_RIGHT: 1, 
                       ACTION_FORWARD: 2,
                       ACTION_SUCK: 4,
                       ACTION_UNSUCK: 4,
                       ACTION_SENSE_GOLD: 1,
                       ACTION_MINE_GOLD: 10,
                       ACTION_UNLOAD_GOLD: 1,
                       ACTION_NOP: 1,
                       ACTION_STOP: 0}

class VacuumAgent(Agent):
    def __init__(self, version, log, battery, exec):
        # Agent superclass holds function call to have agent choose next action
        super().__init__(exec)
        # Version is documentation string only
        self.version = version
        # Agent writes log messages by calling this function
        self.log = log
        # Remaining battery units
        self.battery_capacity = battery
        self.battery_level = battery
        # Score bonuses and action power consumption
        self._score = 0
        self.num_gold = 0
        self.num_dirt = 0
        self.execution_count = 0
        self.last_action = None
        self.action_count = 0
    
    def display_execution_status(self):
        self.action_count += 1
        if (self.action_count % REPORT_INTERVAL) == 0:
            self.log("Action count: {self.action_count}, score: {self.score()}, battery: {self.battery_level}")

    # Agent must call this on each call every time its execute
    # method is called -- update last action, score, and battery
    # consumption
    
    def step_update(self, action, percept):
        self.battery_level -= BATTERY_CONSUMPTION[action]
        self._score += self.action_reward(action, percept)
        self.last_action = action
        self.display_execution_status()
        
    def action_reward(self, action, percept):
        if (action == ACTION_SUCK and percept.attributes["dirt"]):
            return DIRT_REWARD
        else:
            return 0
        
    # This is called by the environment when the agent 
    # successfully unloads some gold.  
    def add_gold_reward(self):
         self._score += GOLD_REWARD
         
    # Default getter for agent score; subclass may override
    def score(self):
        return self._score
    
    # Standard pattern for dealing with depleted battery -- repeated
    # in all agents
    def battery_depleted(self):  
        return self.battery_level <= 0
 
        
        
        
        
    