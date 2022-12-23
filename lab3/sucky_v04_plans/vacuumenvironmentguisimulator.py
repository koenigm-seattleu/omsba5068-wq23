from tkinter import Tk, Frame, Button, BOTH, OptionMenu, StringVar, Text, END, PhotoImage
from tkinter import Entry
from vacuumenvironment import VacuumEnvironment
from constants import CLEAN, DIRT, WALL, GOLD
from load_agents import make_agent, agents
import yaml

CONFIG_FILE_NAME = 'config.yml'

DIRT_BIAS = 0.5
WALL_BIAS = 0.0

# Pre-selected PRF seeds
FIXED_SEED_1 = 1337
FIXED_SEED_2 = 69420

STANDARD_ENV_DIMS = (20,20)
DEFAULT_AGENT_LOCATION = (1,1)

WORLD_COLOR_WALL = "black"
WORLD_COLOR_CLEAN = "white"
WORLD_COLOR_DIRTY = "gray"
WORLD_COLOR_GOLD = "yellow"
WORLD_COLOR_HOME = "blue"

import platform
PLATFORM_WINDOWS = platform.system() == 'Windows'

class VacuumEnvironmentGUISimulator:
 
    def __init__(self):
        self.vacuum_env = None
        self.agent = None
        self.grid_frame = None
        self.grid = None
        self.previous_dims = None
        self.is_running = False
        self.marked_agent_pos = (0, 0)
        self.marked_agent_rot = (1, 0)
        
        self.setup_gui()
        self.setup_images()
        self.setup_selection_menus()
        self.setup_buttons()
 
        self.update_all(force=True)


        
    def setup_gui(self):
        command = yaml.safe_load(open(CONFIG_FILE_NAME))['simulation']['command']
        self.root = Tk()
        self.root.title("Vacuum Environment")
        self.root.minsize(1024,768)
        self.root.resizable(width=True, height=True)
        self.agent_btn_dims = 22
        self.host_frame = Frame(self.root)
        if command:
            self.setup_command_widget()
        self.setup_log_widget()
        if command:
            self.command_frame.pack(side="top")
        self.options_frame.pack(side="top")
        self.host_frame.pack(expand=True, fill=BOTH)
        
    def setup_log_widget(self):
        self.log = Text(self.host_frame, width=50, borderwidth=2)
        self.log.pack(side="right", expand=True, fill="y")
        self.log.configure(state="disabled")
        self.options_frame = Frame(self.host_frame)
   
    def setup_command_widget(self):
        command_frame = Frame(self.host_frame)
        txt = Entry(command_frame, bd =2, width=100)
        txt.pack(side = "left")
        self.command_text = txt
        b = Button(command_frame, text="Do It!")
        b.pack(side="right")
        b.config(command=lambda: self.send_user_command)
        txt.bind('<Return>', self.send_user_command)
        self.command_frame = command_frame
        
    def setup_images(self):
        self.agent_img = dict()
        self.agent_img[(1, 0)] = PhotoImage(file="images/agent_east.png")
        self.agent_img[(0, 1)] = PhotoImage(file="images/agent_south.png")
        self.agent_img[(-1, 0)] = PhotoImage(file="images/agent_west.png")
        self.agent_img[(0, -1)] = PhotoImage(file="images/agent_north.png")
        self.images = {CLEAN: PhotoImage(file="images/blank.png"),
                       DIRT: PhotoImage(file="images/dirt.png"),
                       WALL:  PhotoImage(file="images/wall.png"),
                       GOLD:  PhotoImage(file="images/gold.png")}
        self.blank_img = PhotoImage(file="images/blank.png")
        
    def setup_selection_menus(self):
        # Environment wall bias
        self.wall_bias_getter = self.create_selection_menu(
            self.update_all,
            *[(str(bias), bias) for bias in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]]
        )
        # Environment dirt bias
        self.dirt_bias_getter = self.create_selection_menu(
            self.update_all,
            *[(str(bias), bias) for bias in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]]
        )
        # Environment goal bias
        self.gold_bias_getter = self.create_selection_menu(
                self.update_all,
                *[(str(bias), bias) for bias in [0, 1, 2, 3, 4, 5, 0.01, 0.05]]
                )
        # Environment PRF seed
        self.seed_getter = self.create_selection_menu(
            self.update_all,
            ("Random", None),
            ("Seed 1", FIXED_SEED_1),
            ("Seed 2", FIXED_SEED_2),
            always_trigger_onselect=True
        )

        self.recon_getter = self.create_selection_menu(
                self.update_all,
                ("None", "None"), 
                ("Full", "Full"), 
                ("WallsAndGold", "WallsAndGold"),
                ("WallsOnly", "WallsOnly"),
                always_trigger_onselect=True
        )     
        self.agent_getter = self.create_selection_menu(
            self.update_all,
            *list(map(lambda p: (p[1], p), agents())),
            always_trigger_onselect=True
        )
        self.delay_getter = self.create_selection_menu(
            None,
            *[(str(time) + "ms", time) for time in [100, 500, 1000, 10, 50]]
        )

    def make_button(self, text, callback):
        b = Button(self.options_frame, text=text)
        b.pack(side="left")
        b.config(command=callback)
 
    def setup_buttons(self):
        self.make_button("Prepare", self.update_all)
        self.make_button("Run", self.start)
        self.make_button("Stop", self.stop)
        self.make_button("Step", self.step)
        self.make_button("Clear Log", self.log_clear)

    def send_user_command(self, ignore=None):
        self.agent.is_alive = True
        self.agent.send_user_command(self.command_text.get())
        self.start()
        self.command_text.delete(0, 'end')

    def start_main_loop(self):
        self.root.mainloop()

    def append_log(self, text, end="\r\n"):
        self.log.configure(state="normal")
        self.log.insert("end", str(text)+end)
        self.log.see(END)
        self.log.configure(state="disabled")

    def log_clear(self):
        self.log.configure(state="normal")
        self.log.replace("0.0", END, "")
        self.log.configure(state="disabled")
        
    def refresh_tile(self, x, y):
        if PLATFORM_WINDOWS:
            state = self.vacuum_env.world[x][y]
            new_state =  WORLD_COLOR_CLEAN  if state == CLEAN\
                    else WORLD_COLOR_DIRTY  if state == DIRT\
                    else WORLD_COLOR_GOLD   if state == GOLD\
                    else WORLD_COLOR_WALL

            # Apply color to tile (if necessary)
            if new_state != self.grid[x][y].cget("bg"):
                self.grid[x][y].configure(bg=new_state)
        else:
            new_image = self.images[self.vacuum_env.world[x][y]]
            if new_image != self.grid[x][y].cget("image"):
                self.grid[x][y].configure(image=new_image)
                
    def refresh(self):
        for x in range(self.vacuum_env.env_x):
            for y in range(self.vacuum_env.env_y):
                self.refresh_tile(x, y)
        self.draw_agent()

    def step(self):
        """
        Run one step in environment simulation.
        This automatically refreshes tiles.
        """
        self.vacuum_env.step()
        self.refresh()

    def start(self):
        if self.is_running:
            #self.append_log("Already running")
            return
        #self.append_log("Starting...")
        self.is_running = True
        self.run()

    def run(self):
        if self.is_running:
            self.step()
            self.root.after(self.delay_getter(), self.run)  # Trigger a timer for next call

    def stop(self):
        if self.is_running:
            self.append_log("Stopped")
        self.is_running = False

    def make_env_frame(self):
        """
        Create the grid layout representing the state of the vacuum environment

        :return: None
        """

        width, height = STANDARD_ENV_DIMS
        previous_width, previous_height = (self.previous_dims or (-1, -1))

        if (width != previous_width or height != previous_height) and self.grid:
            self.grid[self.marked_agent_pos[0]][self.marked_agent_pos[1]].configure(image=self.blank_img)

        padx = 5 if width > 15 else 8
        pady = 2 if height > 15 else 4

        def make_callback(x, y):
            """
            Create a callback function for the given coordinate

            :param x: X-coordinate
            :param y: Y-coordinate
            :return: Callback function for the given coordinate
            """
            return lambda: self.grid_click_callback(x, y)

        def make_button(x, y, container_frame):
            """
            Shorthand for creating a button in the tile grid

            :param x: X-coordinate of button
            :param y: Y-coordinate of button
            :param container_frame: Frame to hold button
            :return: Reference to button
            """
            nonlocal padx
            nonlocal pady

            btn = Button(container_frame, text="", height=self.agent_btn_dims, width=self.agent_btn_dims, padx=padx, pady=pady, image=self.blank_img)
            btn.pack(side="right")
            btn.config(command=make_callback(x, y))
            return btn

        # Create an unpopulated button ref grid (filled with None for debug purposes)
        grid = [[None for _ in range(height)] for _ in range(width)]

        frame_pad = 0 if height > 30 else 8 * (30 - height)
        if self.grid is None:
            frame = Frame(self.host_frame, pady=frame_pad, padx=0)

            for y in range(height - 1, -1, -1):
                row_frame = Frame(frame)
                for x in range(width - 1, -1, -1):
                    grid[x][y] = make_button(x, y, row_frame)
                row_frame.pack(side="bottom")

            frame.pack(side="bottom")

            self.grid_frame = frame
        else:
            # Optimization to hopefully be a bit nicer on GC (if nothing else)
            for y in range(height - 1, -1, -1):
                rel_y = height - 1 - y
                row_frame = Frame(self.grid_frame) if rel_y >= previous_height else self.grid[0][
                    previous_height - 1 - rel_y].master
                for x in range(width - 1, -1, -1):
                    rel_x = width - 1 - x
                    grid[x][y] = self.grid[previous_width - 1 - rel_x][
                        previous_height - 1 - rel_y] if rel_x < previous_width and rel_y < previous_height else make_button(
                        x, y, row_frame)

                    if rel_x < previous_width and rel_y < previous_height:
                        grid[x][y].configure(padx=padx, pady=pady)
                        grid[x][y].config(command=make_callback(x, y))

                row_frame.pack(side="bottom")

            for y in range(previous_height):
                if previous_height - y > height:
                    self.grid[0][y].master.pack_forget()
                    continue

                for x in range(previous_width):
                    if previous_width - x > width:
                        self.grid[x][y].pack_forget()

            self.grid_frame.configure(pady=frame_pad, width=frame_pad)
            self.grid_frame.pack(side="bottom")

        # Update grid
        self.grid = grid
        self.previous_dims = (width, height)
        self.draw_agent()

    def draw_agent(self):
        self.grid[self.marked_agent_pos[0]][self.marked_agent_pos[1]].configure(image=self.blank_img)
        self.grid[self.agent.location[0]][self.agent.location[1]].configure(image=self.agent_img[self.agent.facing])
        self.marked_agent_pos = self.agent.location
        self.marked_agent_rot = self.agent.facing

    def update_all(self, force=False):
        """
        Trigger a full refresh. This recreates the environment, agent and grid, as well as updates tile colours.

        :param force: Force update.
        :return: None
        """

        if self.vacuum_env is not None or force:
            # Ensure we stop the agent
            if self.is_running:
                self.stop()
            self.create_sim()
            self.make_env_frame()
            self.refresh()

    def grid_click_callback(self, x, y):
        """
        Callback to manually mark a tile as clean, dirty or a wall. Outer walls cannot be changed.
        Tile at coordinate (1, 1) cannot be a wall; only clean or dirty since this is where agents are spawned.

        :param x: X-coordinate of tile
        :param y: Y-coordinate of tile
        :return: None
        """
        w, h = self.grid_dims_getter()
        current = self.vacuum_env.world[x][y]
        if x != 0 and x != w - 1 and y != 0 and y != h - 1:
            self.vacuum_env.world[x][y] = DIRT if current == WALL or (
                    x == 1 and y == 1 and current == CLEAN) else CLEAN if current == DIRT else WALL
            self.refresh_tile(x, y)

    def create_selection_menu(self, cb_on_select, *opts, always_trigger_onselect=False, no_destructure=False, pass_selection_to_callback=False):
        """
        Quick way of creating a drop-down menu with a set of options and selection callbacks.

        :param cb_on_select: Menu item selection event callback
        :param opts: Menu options. These should be a list of two-element tuples where the first item is the label and the second is the corresponding value
        :param always_trigger_onselect: Whether the selection callback should be triggered even if an already-selected item was selected
        :param no_destructure: Whether option values should be destructured into the arguments of the callback
        :param pass_selection_to_callback: Whether or not to pass the selected value to the selection callback function
        :return: Getter function for the currently selected `value` (not label)
        """

        options_dict = dict()

        selection_active = StringVar(self.root)
        selection_previous = StringVar(self.root)

        for (key, value) in opts:
            options_dict[key] = value

        menu = OptionMenu(self.options_frame, selection_active, *options_dict.keys())

        def on_select(*args):
            """
            Callback function for when a menu item is selected

            :param args: Ignored arguments. Just contains the modified variable
            :return: None
            """
            # Check if a previously un-selected item was selected (or if the event should be processed anyway)
            if selection_active.get() != selection_previous.get() or always_trigger_onselect:
                selection_previous.set(selection_active.get())

                # Call callback if one was specified
                if cb_on_select:
                    if pass_selection_to_callback:
                        # Attempt to destructure parameter as much as possible
                        # This is just a lazy way of passing sets of arguments in less LOC
                        if (not no_destructure) and dir(options_dict[selection_active.get()]).__contains__("__iter__"):
                            if type(options_dict[selection_active.get()]) is dict:
                                cb_on_select(**options_dict[selection_active.get()])
                            else:
                                cb_on_select(*(options_dict[selection_active.get()]))
                        else:
                            cb_on_select(options_dict[selection_active.get()])
                    else:
                        cb_on_select()

        # Set a callback for when variable changes value
        selection_active.trace("w", on_select)

        # Pack menu if a side as packed, else assume packing will be done elsewhere
        menu.pack(side="left")

        # Select a menu option. This also triggers an initial callback
        selection_active.set(opts[0][0])

        # Return a getter function to the active *value* (not key)
        return lambda: options_dict[selection_active.get()]

    def get_agent(self):
        file_name, agent_class_name = self.agent_getter()   # this is (file, name)
        return make_agent(file_name, agent_class_name, self.append_log)
        
    def create_sim(self):
        """
        Create environment and agent and add agent to environment
        """
        self.vacuum_env = VacuumEnvironment(*STANDARD_ENV_DIMS, 
                                            self.dirt_bias_getter(), 
                                            self.wall_bias_getter(),
                                            self.gold_bias_getter(),
                                            self.seed_getter())
        self.agent = self.get_agent()
        self.vacuum_env.add_thing(self.agent, DEFAULT_AGENT_LOCATION)
        recon = self.recon_getter()
        self.vacuum_env.prep_agent(self.agent, recon)

def run():
    VacuumEnvironmentGUISimulator().start_main_loop()
