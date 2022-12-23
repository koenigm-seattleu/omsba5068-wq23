# -*- coding: utf-8 -*-

AGENTS = [("agents/commandagentmanual.py",  "CommandAgentManual"),
          ("agents/commandagentml.py",  "CommandAgentML") 
         ]

def agents():
    return AGENTS

def agent_names():
    return list(map(lambda p: p[1]), AGENTS)

def file_for(agent_name):
    for p in AGENTS:
        if p[1] == agent_name:
            return p[0]
    return None

