### Vacuum World Simulator

The vacuum world is a software framework for building and testing simple agent
architectures.  It was originally built by 
[Department of Computer and Information Science, Linkopings University](https://www.ida.liu.se/~TDDC17/info/labs/lab1_agents_java.en.shtml)
 and modified 
for this class.

The dirt world is a grid of squares inhabited by an agent who occupies a single square and can 
move from a square to an adjacent square.  Some squares are walls, and the agent 
cannot into those squares.  A non-wall square may or may not contain a single
piece of dirt, which can be sucked up by the agent.

Here is a graphical depiction of a dirt world

![dirt world](dirtworldAnnotated.gif)

* This world is 20x20
* Walls render in black
* Dirt renders in grey
* The agent is a yellow circle
* The coordinate system starts at upper left, with the outer rows and columns being walls
* The agent begins at square [1,1] and is facing East

---

For this lab you will be 
* building agents, then 
* putting them in environments, then 
* running simulations, then 
* evaluating and comparing agent performance

---

#### Enviroments

An environment defines characteristics of the world and its contents apart from the agent.

The following parameters can be adjusted
* Environment (grid) size -- for this exercise we will use a 20x20 grid only
* Dirt density -- specified by a parameter between 0.0 and 1.0, dirt particles are placed randomly in grid squares 
at the beginning of a simulation.  A dirt density of 0.0 means no dirt, 1.0 means all non-wall squares will have dirt
* Dirt distribution -- a 0/1 parameter.  If 0, dirt is distributed uniformly around the grid according to 
the density parameter.  If 1, dirt tends to placed close to other dirt, so the agent is likely to find relatively dirty regions of the grid
along with relatively clean regions
* Wall density -- specified by a parameter between 0.0 and 1.0, walls are placed randomly at the beginning of a simulation.   A wall density of 0.0 means no walls, 1.0 means all squares except [1,1] will contain a wall.
* Random number seed -- you can specify a random number seed to the environment, which means that it will generate
the same world (walls and dirt) every time.  This  will be useful for debugging or if you want to compare agent performance on 
exactly the same world.

The section on Test Harnesses below will show how to build environments, put agents in them, and run 
simulations.

---

#### Agents

An agent appears has a *position* and a *heading* (the direction it is facing).  By convention, the agent's initial
position is [1,1] -- the upper left cell -- and its initial heading is EAST.

Each cycle in the environment/simulation proceeds as follows:
* The simulation presents the agent with *percepts* describing the current state of the world
* The agent decides what *action* to take
* The agent returns its chosen action to the simulation/environment

Each cycle the agent gets these three *percepts*, each describing part of the world. Each percept has a True/False value
* **DIRT** -- the square occupied by the agent contains dirt
* **BUMP** -- the agent tried to move into a wall;  its position did not change
* **HOME** -- the agent's current position is its initial position

The agent then chooses an action from among these: 
* **SUCK** -- try to suck up dirt.  If there is dirt in the same square as the agent, it disappears.  If there 
is no dirt in the square, the action has no effect.  
* **FORWARD** -- try to move to the adjacent square in the *heading* direction.  For example, if the agent is at [3,3]
and has the heading **SOUTH** and selects **FORWARD**, the simulation will try to move the agent to [4,3].  If that 
adjacent square is not a wall, the agent's position changes and the next **BUMP** percept will be false.  If that 
adjacent square is a wall, the agent's position and heading do not change, and the next **BUMP** percept will be true.
* **TURN_LEFT** -- change orientation by facing one compass heading to the left (**NORTH** -> **EAST**, **EAST** -> **SOUTH**, etc.)
* **TURN_RIGHT** -- change orientation by facing one compass heading to the right (**NORTH** -> **WEST**, **WEST** -> **SOUTH**, etc.)
* **NOP** -- Do nothing.

Here is a code fragment demonstrating a very simple agent:  it chooses the **SUCK** action if there is dirt, otherwise 
chooses randomly between its four other actions.  The ```log`` operation is optional, and where the log mention appears 
depends on the simulation environment.

<pre>
class SimpleAgent(Agent):
    
    def __init__(self, world_width, world_height, log):
     self.log = log

    def execute(self, percept): 
       action = None
       if percept.attributes['dirt']:
          action = ACTION_SUCK
       else:
        action = [ACTION_FORWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_NOP][randint(0,3)]
       self.log(f"Choosing action {action}")
       return action
</pre>

---

#### Evaluating an Agent

The basic simulation testbed has no concept of how well an agent performs.  That is up to an agent and
its designer.

For this lab we will extend the basic framework with these costs and rewards for the agent
* An agent has a fixed battery capacity, and each action it takes consumes a certain number of battery units
* An agent gets a reward for every piece of dirt it sucks up
* The agent's *score* is the amount of dirt it sucks up before its battery is consumed

(You will implement an extension to this reward/score function in one of the lab problems.)

Here are the default costs and rewards for an agent.  These appear in `vacuumagent.py` and can be customized
* The reward is 10 points per dirt sucked
* Battery capacity is 300 units
* The **SUCK** action consumes 4 battery units
* The **FORWARD** action consumes 2 battery units
* **TURN_LEFT** and **TURN_RIGH** both consume 1 battery unit
* **NOP** consumes 0 battery units

You are provided with agent code making it easy to set up an agent with these costs and rewards, and that stops when its batter is depleted.

---

#### Running a Simulation

Running a simulation for the purposes of this lab involves
* Creating an environment and setting its parameters
* Creating an agent and setting its parameters
* Initializing the environment which randomly assigns walls and dirt according to the environment parameters, and inserts the agent in the environment
* Run simulation steps (given the agent percepts, receive its action choice, update the world) until the agent's battery depletes
* Reading the agent's score

There is a GUI simulation platform as well as code that allows you to run a simulation entirely in code.  The former 
is good for debugging and visualizing, the latter is good for running repeated experiments and gathering statistics for analysis purposes.

---

##### The Simulation GUI

Start the simulation testbed by running the code in `run_lab1.py`.  You can then run multiple simulations, which you 
control using buttons in the GUI.

To configure a simulation, the first seven buttons configure these parameters
* The grid size (fixed at 20x20)
* The wall density
* The dirt density
* The dirt uniformity
* The random number generator seed
* The agent class
* Time delay between simulation steps

The next five buttons set up and run a simulation
* Prepare the simulation by randomly generating walls and dirt and initializing and placing the agent in its initial position and heading
* Run the simulation or resume a stopped simulation
* Stop the simulation
* Run one simulation
* Clear the agent's log (appears in the pane to the right of the grid)

With the GUI, the only source of information about the world is the graphical depiction of the grid, plus whatever information the agent logs.
So if you want information about the agent's action choice, or want to know its score, your agent must use `log` calls to 
display that information.

In the GUI, simulations run until they are explicitly stopped.  By convention our agents will run until their battery is
depleted, then they will create a log message with their final score, then they will always choose a NOP action.
You will see code that implements this pattern in all of the sample agents.  When you write your own agent, it must copy this code.

---

#### The API Simulation

There is code in `vacuumsimulation.py` that makes it easy to run multiple simulations involving multiple agents
and environment parameters, and write information about the agent, parameters, and score to the console or to a file.
You can modify this code to build a data set that can then be read into a stat analysis package to evaluate agent 
performance.

 

