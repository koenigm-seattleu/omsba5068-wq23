from batch_simulator import run_agents_in_environment

#######################################
# Two options about what to do with the agent's log messages in absence 
# of a GUI pane
def log_to_console(msg):
    print(msg)

def log_null(msg):
    pass

########################################

# Write all batch results to this file
default_output_file_name = 'simulation_results.csv'

## All possible agents and their recon configurations

agents = [ ("agents/reactiveagent.py",    "NoSenseAgent"),
           ("agents/reactiveagent.py",    "SensingAgent"),
           ("agents/worldmodelagent.py",  "WorldModelAgent"),
           ("agents/planningagent.py",    "OmniscientAgent"),
         ]

recon = {"NoSenseAgent": 'None',
         "SensingAgent": 'None',
         "WorldModelAgent": 'None',
         "OmniscientAgent": 'Full'}

#############################################################################
# Show a single example (agent + dirt density + wall density + num samples)
#  of running an experiment.
#
# EXAMPLE ONLY!  This just shows you how to set parameters in order to run
# your experiments!

def run_agents_example():
    dirt_density = 0.1
    wall_density = 0.3
    num_samples = 10
    write_results_to_console = True
    demo_agents = [agents[1], agents[2]]   # Sensing agent and world model agent
    battery_capacity = 1000               # This is twice the default battery 
                                            # capacity -- most of your experiments
                                            # should use the default, you get the 
                                            # default by setting battery_capacity to None
    run_agents_in_environment(dirt_density, 
                              wall_density, 
                              demo_agents, 
                              recon,
                              battery_capacity,
                              log_to_console,   # Print agent log messages to console
                              num_samples, 
                              default_output_file_name, 
                              write_results_to_console)

#  Run the demo!
run_agents_example()