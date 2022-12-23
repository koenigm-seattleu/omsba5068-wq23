# How the Simulation knows which agents to load.
# First element of each tuple is the name of a file 
# relative to the project root.  Second element is the 
# class that implements the agent.

AGENTS = [ ("agents/reactiveagent.py",    "NoSenseAgent"),
           ("agents/reactiveagent.py",    "SensingAgent"),
           ("agents/worldmodelagent.py",  "WorldModelAgent"),
           ("agents/planningagent.py",    "OmniscientAgent"),
         ]

####  DO NOT EDIT BELOW THIS LINE #########
def agents():
    return AGENTS

def agent_names():
    return list(map(lambda p: p[1]), AGENTS)

def file_for(agent_name):
    for p in AGENTS:
        if p[1] == agent_name:
            return p[0]
    return None

#######################
import importlib.util

def make_agent(file_name, agent_class_name, log):
    spec = importlib.util.spec_from_file_location(agent_class_name, file_name)
    agent_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_mod)
    aclass = eval(f"agent_mod.{agent_class_name}")
    return aclass(log)