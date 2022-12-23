from agents.vacuumagent import VacuumAgent
from vacuumenvironment import ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD
from vacuumenvironment import ACTION_SUCK, ACTION_NOP
from vacuumenvironment import ACTION_MINE_GOLD, ACTION_UNLOAD_GOLD
from agents.agentworldmodel import AgentWorldModel
from agents.agentworldmodel import NORTH, SOUTH, WEST, EAST
from agents.agentworldmodel import GOLD, DIRT, WALL
from random import randint

VERSION = "TEST"

class TestAgent(VacuumAgent):
    
    def __init__(self, log, battery=500):
        super().__init__(VERSION, log, battery, self.execute)
        self.last_action = None
        self.state = AgentWorldModel(20, 20)
        self.return_home_permanently = False
        self.completed = False

    ################################################
    # This method gets called once prior to execution, w/ info about
    # the world.  Just pass it on to the world model
    
    def prep(self, recon):
        self.state.prep(recon)
        self.log("Received recon report, ready to go!")
        self.log(f"Gold: {len(self.state.squares_with_state(GOLD))}," +
                          f" Dirt: {len(self.state.squares_with_state(DIRT))}" +
                          f" Walls: {len(self.state.squares_with_state(WALL))}")
    
   #################################################################
   #  Called once per simulation cycle.  Must return an action choice
     
    def execute(self, percept): 
        
        # Update world model
        self.state.update(percept.attributes["dirt"], percept.attributes["bump"])
        
        # Choose action
        action = self.choose_action()
 
        # Notify superclass to update score and battery usage
        self.step_update(action, percept)
        self.state.update_action(action)
        
        return action
   
    ###############################################################
    
    def choose_action(self):
        action = None
        
        if self.battery_depleted():
            if not self.completed():
                self.log("Battery depleted")
            action = ACTION_NOP       
        elif self.state.current_position == (1,1) and self.state.num_golds > 0:
            action = ACTION_UNLOAD_GOLD
            self.log(f"Unloading gold ({self.state.num_golds})")     
        elif self.state.current_position in self.state.squares_with_state(DIRT):
            action = ACTION_SUCK
            self.log(f"Sucking dirt")
        elif self.state.current_position in self.state.squares_with_state(GOLD)\
                and self.state.num_golds < 2:
            action = ACTION_MINE_GOLD
            self.log(f"Mining gold")    
        else:
            action=[ACTION_FORWARD, ACTION_FORWARD, ACTION_FORWARD, ACTION_FORWARD,
                    ACTION_TURN_LEFT, ACTION_TURN_RIGHT][randint(0,5)]
        return action
    