from agents.agentworldmodel import AgentWorldModel
from agents.commandprocessorml import CommandProcessor
from agents.commandagentbase import CommandAgentBase

VERSION = "CML"

class CommandAgentML(CommandAgentBase):
    def __init__(self, log):
        world_model = AgentWorldModel(20,20)
        command_processor = CommandProcessor(self, world_model, log)
        super().__init__(VERSION, log, world_model, command_processor)