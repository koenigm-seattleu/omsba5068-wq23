from agents.vacuumagent import VacuumAgent
from agents.agentworldmodel import AgentWorldModel
from agents.pathnavigation import begin_path, continue_path
from agents.agentworldmodel import GOLD, DIRT, WALL
from vacuumenvironment import ACTION_STOP

class CommandAgentBase(VacuumAgent):
    
    def __init__(self, version, log, worldmodel, command_processor, battery=500):    
        super().__init__(version, log, battery, self.execute)
        self.worldmodel = worldmodel
        self.commmand_processor = command_processor
        self.command_sequence = []
        self.path = []
        self.next_actions = []
 

    ################################################
    # This method gets called once prior to execution, w/ info about
    # the world.  Just pass it on to the world model
    
    def prep(self, recon):
        self.worldmodel.prep(recon)
        self.log("Received recon report, ready to go!")
        self.log(f"Gold: {len(self.worldmodel.squares_with_state(GOLD))}," +
                 f" Dirt: {len(self.worldmodel.squares_with_state(DIRT))}" +
                 f" Walls: {len(self.worldmodel.squares_with_state(WALL))}")
            
   #################################################################
   #  Called by the environment once per simulation cycle.  Must return an action choice
     
    def execute(self, percept):         
        # Update world model
        self.worldmodel.update(percept.attributes["dirt"], percept.attributes["bump"])       
        # Choose action
        action = self.choose_action()
        # Notify superclass to update score and battery usage
        self.step_update(action, percept)
        # Notify world model of action choice
        self.worldmodel.update_action(action)      
        return action
   
    ###############################################################
    
    # Command processor gets the command from the environment, decides
    # what to do, and sets the command_sequence attribute.   This 
    # happens strictly after the recon, but strictly before the first call 
    # to execute
    
    def send_user_command(self, cmd):
         self.command_sequence = self.commmand_processor.interpret_command(cmd)
 
    #############################################################
    # This is the same action policy format we have seen in 
    # all our agents.  In the command sequence agent, we will
    # be executing command sequences, but they decompose into
    # following paths and taking individual actions
    
    def choose_action(self):
        action = None
        
        if self.battery_depleted():
            self.log("Battery depleted")
            action = ACTION_STOP          
        elif len(self.next_actions) > 0:
            action = self.next_actions.pop(0)
        elif len(self.path) > 0:
            action = continue_path(self)   
        elif len(self.command_sequence) > 0:
            return self.process_command_sequence()
        else:
            return ACTION_STOP   
        return action
   
    # Intents generate these command sequences
    # Each element in the sequence is a pair, which is either 
    #   ("actions", list_of_actions) or 
    #   ("path", list_of_positions)
    
    def process_command_sequence(self):
        cmd = self.command_sequence.pop(0)
        if cmd[0] == 'path':
            return begin_path(self, cmd[1])
        elif cmd[0] == 'actions':
            a = cmd[1].pop(0)
            self.next_actions = cmd[1]
            return a

 
    
        