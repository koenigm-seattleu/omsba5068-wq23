from agent import Agent
from constants import ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD
from constants import ACTION_NOP, ACTION_STOP
from constants import ACTION_PROBE_GHOST, ACTION_BUST_GHOST

BUST_REWARD = 200
BUST_PENALTY = 50
PROBE_PENALTY = 5

# Print a log message after this many iterations; None for no report
REPORT_INTERVAL = 100

DEFAULT_BATTERY_CAPACITY = 500

BATTERY_CONSUMPTION = { ACTION_TURN_LEFT: 0,
                        ACTION_TURN_RIGHT: 0, 
                        ACTION_FORWARD: 0,
                        ACTION_NOP: 0,
                        ACTION_STOP: 0,
                        ACTION_PROBE_GHOST: 5, 
                        ACTION_BUST_GHOST: 20
                        }

class VacuumAgent(Agent):
    def __init__(self, version, log, program, battery=DEFAULT_BATTERY_CAPACITY):
        # Agent superclass holds function call to have agent choose next action
        super().__init__(program)
        # Version is documentation string only
        self.version = version
        # Agent writes log messages by calling this function
        self.log = log
        # Remaining battery units
        self.battery_capacity = battery
        self.battery_level = battery
        # Score bonuses and action power consumption
        self.num_dirt = 0
        self.num_gold = 0
        self._score = 0
        self.action_count = 0
    
    def display_execution_status(self, force=False):
        if force or (REPORT_INTERVAL != None and (self.action_count % REPORT_INTERVAL) == 0):
            self.log(f"Action count: {self.action_count}, score: {self.score()}, battery: {self.battery_level}")

    # Enviornment calls the agent with initial "recon" information about the world.
    # Can be overridden;  default is to ignore this information
    def prep(self, recon):
        pass
    
    # Agent must call this method first on each call to its execute
    # method is called -- update last action, score, and battery
    # consumption
    
    def pre_update(self, percept):
        self.display_execution_status()
    
    def post_update(self, action):
        self.battery_level -= BATTERY_CONSUMPTION[action]
        if action == ACTION_PROBE_GHOST:
            self._score -= PROBE_PENALTY
        if action == ACTION_BUST_GHOST:
            self._score -= BUST_PENALTY
        self.action_count += 1
 
    def add_bust_reward(self):
        self._score += BUST_REWARD

    # Default getter for agent score; subclass may override
    def score(self):
        return self._score
    
    # Standard pattern for dealing with depleted battery -- repeated
    # in all agents
    def battery_depleted(self):  
        return self.battery_level <= 0
 
        
        
        
        
    