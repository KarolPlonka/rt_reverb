import tkinter as tk
import customtkinter as ctk
from CTkMenuBar import *

import threading as th

from scene_graphics.scene import Scene
from scene_graphics.objects.wall import Wall
from scene_graphics.objects.listener import Listener
from tools.tool_button import ToolButton
from tools.tools_panel import ToolsPanel
import tools.tools as Tools
from algorithm_handler import AlgorithmHandler
from scene_graphics.objects.sound_source import SoundSource
from settings import SettingsPopUp
from object_properties.properties_panel import PropertiesPanel
from audio.audio_panel import AudioPanel
from styles import COLOR_PALETTE, CHECKBOX_STYLE, ACTION_BUTTON_STYLE 


class App(ctk.CTk):
    SEGEMNTS_GAP = 15
    CONTROLS_PANEL_GAP = 15

    DEFAULTS = {
        'reflections_amount': 5,
        'initial_rays_amount': 8,
        'min_energy_threshold': 0.001,
        'scene_walls_reflectivity': 0.95,

        'scene_width':  1500,
        'scene_height': 700,
        'grid_size': 100,
        'show_grid': True,
    }

    def __init__(self):
        super().__init__()

        self.geometry("1300x800+50+50")
        self.minsize(width=800, height=700)

        self.title('RT Reverb')
        self.config(bg = COLOR_PALETTE['primary'])

        self.settings = {
            'simulation': {
                'reflections_amount': tk.IntVar(value = self.DEFAULTS['reflections_amount']),
                'initial_rays_amount': tk.IntVar(value = self.DEFAULTS['initial_rays_amount']),
                'min_energy_threshold': tk.DoubleVar(value = self.DEFAULTS['min_energy_threshold']),
            },
            'scene': {
                'scene_width': tk.IntVar(value = self.DEFAULTS['scene_width']),
                'scene_height': tk.IntVar(value = self.DEFAULTS['scene_height']),
                'scene_walls_reflectivity': tk.DoubleVar(value = self.DEFAULTS['scene_walls_reflectivity']),
                'grid_size': tk.IntVar(value = self.DEFAULTS['grid_size']),
            },
        }

        self.simulation_settings_pop_up = SettingsPopUp('Simulation Settings', self.settings['simulation'])
        self.scene_settings_pop_up = SettingsPopUp('Scene Settings', self.settings['scene'])

        self.menus = self.get_menus()
        self.config(menu=self.menus['main'])

        self.content_frame = ctk.CTkFrame(self, fg_color=COLOR_PALETTE['primary'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.rowconfigure(0, weight=1)  

        self.controls_panel = ctk.CTkFrame(self.content_frame, fg_color=COLOR_PALETTE['secondary'])
        self.controls_panel.grid(column=0, row=0, sticky="n", padx=self.SEGEMNTS_GAP, pady=self.SEGEMNTS_GAP)

        self.tools_panel = ToolsPanel(self.controls_panel, fg_color="transparent")
        self.tools_panel.pack(side=tk.TOP, padx=20, pady=self.CONTROLS_PANEL_GAP)

        self.show_grid = tk.BooleanVar(value=self.DEFAULTS['show_grid'])
        self.show_grid_checkbox = ctk.CTkCheckBox(
            self.controls_panel,
            text="Show Grid",
            variable=self.show_grid,
            command=self.toggle_grid,
            bg_color=COLOR_PALETTE['accent'],
        )
        self.show_grid_checkbox.configure(**CHECKBOX_STYLE)
        self.show_grid_checkbox.pack(side=tk.TOP, pady=(0, self.CONTROLS_PANEL_GAP))

        self.graphic_objects = []

        self.scene = Scene(self.content_frame, self.settings['scene'], self.show_grid, self.graphic_objects)
        self.scene.grid(column=1, row=0, rowspan=2, sticky="n", padx=self.SEGEMNTS_GAP, pady=self.SEGEMNTS_GAP)

        # RAYS (REFL COUNT): 24730
        # 1026ms

        # DEV 
        self.graphic_objects.append(Listener(self.scene, 1050, 450))
        self.graphic_objects.append(SoundSource(self.scene, 200, 250, 0))
        # self.graphic_objects.append(Wall(self.scene, 300, 0, 400, 300))
        # self.graphic_objects.append(Wall(self.scene, 300, 800, 400, 500))

        # self.graphic_objects.append(Wall(self.scene, 100, 100, 200, 200))
        # self.graphic_objects.append(Wall(self.scene, 100, 300, 200, 400))
        # self.graphic_objects.append(Wall(self.scene, 100, 500, 200, 600))

        # self.graphic_objects.append(Wall(self.scene, 300, 100, 400, 200))
        # self.graphic_objects.append(Wall(self.scene, 300, 300, 400, 400))
        # self.graphic_objects.append(Wall(self.scene, 300, 500, 400, 600))

        # self.graphic_objects.append(Wall(self.scene, 500, 100, 600, 200))
        # self.graphic_objects.append(Wall(self.scene, 500, 300, 600, 400))
        # self.graphic_objects.append(Wall(self.scene, 500, 500, 600, 600))

        # self.graphic_objects.append(Wall(self.scene, 700, 100, 800, 200))
        # self.graphic_objects.append(Wall(self.scene, 700, 300, 800, 400))
        # self.graphic_objects.append(Wall(self.scene, 700, 500, 800, 600))

        # self.graphic_objects.append(Wall(self.scene, 900, 100, 1000, 200))
        # self.graphic_objects.append(Wall(self.scene, 900, 300, 1000, 400))
        # self.graphic_objects.append(Wall(self.scene, 900, 500, 1000, 600))

        # self.graphic_objects.append(Wall(self.scene, 1100, 100, 1200, 200))
        # self.graphic_objects.append(Wall(self.scene, 1100, 300, 1200, 400))
        # self.graphic_objects.append(Wall(self.scene, 1100, 500, 1200, 600))

        # self.graphic_objects.append(Wall(self.scene, 1300, 100, 1400, 200))
        # self.graphic_objects.append(Wall(self.scene, 1300, 300, 1400, 400))
        # self.graphic_objects.append(Wall(self.scene, 1300, 500, 1400, 600))

        # self.graphic_objects.append(Wall(self.scene, 700, 600, 800, 500))
        

        self.bake_button = ctk.CTkButton(
            self.controls_panel,
            text="Bake",
            command=self.bake,
        )
        self.bake_button.configure(**ACTION_BUTTON_STYLE, height=50, width=100)
        self.bake_button.pack(side=tk.BOTTOM, pady=self.CONTROLS_PANEL_GAP)

        properties_panel_grid_args = {
            'column': 0,
            'row': 1,
            'sticky': "n",
            'padx': self.SEGEMNTS_GAP,
            'pady': self.SEGEMNTS_GAP,
        }
        self.properties_panel = PropertiesPanel(self.content_frame, properties_panel_grid_args)

        self.is_audio_file_loaded = tk.BooleanVar()
        self.is_audio_file_loaded.set(False)
        self.is_audio_file_loaded.trace_add("write", self.refresh_export_state)

        self.is_baked = tk.BooleanVar()
        self.is_baked.set(False)
        self.is_baked.trace_add("write", self.refresh_export_state)

        self.caught_rays = {
            'left': [],
            'right': [],
        }
        self.caught_rays_amount = 0

        self.audio_panel = AudioPanel(self.content_frame, self.is_audio_file_loaded, self.is_baked)
        self.audio_panel.grid(column=0, row=2, columnspan=2, sticky="sew", padx=self.SEGEMNTS_GAP, pady=self.SEGEMNTS_GAP)

        self.status_bar = ctk.CTkFrame(self.content_frame, fg_color=COLOR_PALETTE["secondary"])
        self.status_bar.grid(column=0, row=3, columnspan=2, sticky="sew", padx=self.SEGEMNTS_GAP, pady=(0,5))
        self.status_bar_label = ctk.CTkLabel(self.status_bar, text="", height=16)
        self.status_bar_label.pack()

        self.current_tool_name = None # key to self.tools
        self.tools = self.load_tools()
        
        self.bind_events()
        self.toggle_grid()

        self.algorithm_handler = AlgorithmHandler()

        # DEV
        # self.bake()
        # self.audio_panel.load_audio_file()
        # self.simulation_settings_pop_up.open()

        # for i in range(20):
        #     self.clear_rays()
        #     walls = [wall for wall in self.graphic_objects if isinstance(wall, Wall)]
        #     listners = [listner for listner in self.graphic_objects if isinstance(listner, Listener)]
        #     sound_source = [sound_source for sound_source in self.graphic_objects if isinstance(sound_source, SoundSource)][0]

        #     self.run_simulation(walls, listners, sound_source)
        # samples = [0.00005, 0.0004, .0003, 0.0002, 0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01]

        # for min_energy_threshold in samples:

        #     self.settings['simulation']['min_energy_threshold'].set(min_energy_threshold)

        #     self.clear_rays()
        #     walls = [wall for wall in self.graphic_objects if isinstance(wall, Wall)]
        #     listners = [listner for listner in self.graphic_objects if isinstance(listner, Listener)]
        #     sound_source = [sound_source for sound_source in self.graphic_objects if isinstance(sound_source, SoundSource)][0]
        #     self.run_simulation(walls, listners, sound_source)

        


    def load_tools(self):
        icons_path = 'assets/icons/'

        tools = [
            {'name': 'Select', 'class': Tools.Select, 'icon': 'select.png'},
            {'name': 'Move', 'class': Tools.Move, 'icon': 'move.png'},
            {'name': 'Add', 'class': Tools.AddWall, 'icon': 'add_wall.png'},
            {'name': 'Resize', 'class': Tools.Resize, 'icon': 'resize.png'},
            {'name': 'Delete', 'class': Tools.Delete, 'icon': 'delete.png'},
            {'name': 'Set Sound Source', 'class': Tools.SetSoundSource, 'icon': 'sound_source.png'},
            {'name': 'Add Listner', 'class': Tools.AddListner, 'icon': 'add_listener.png'},
            {'name': 'Rotate', 'class': Tools.Rotate, 'icon': 'rotate.png'},
        ]

        return {
            tool['name']: tool['class'](
                self.scene,
                self.graphic_objects,
                ToolButton(
                    panel = self.tools_panel, 
                    command = lambda tool=tool['name']: self.set_tool(tool),
                    icon_path = icons_path + tool['icon'],
                    tool_name = tool['name'],
                    set_status_bar_text = self.set_status_bar_text,
                ),
                self.properties_panel
            ) for tool in tools
        }
    

    def get_menus(self):
        main_menu = CTkMenuBar(self)
        file_menu_button = main_menu.add_cascade("File")
        options_menu_button = main_menu.add_cascade("Options")

        file_menu_dropdown = CustomDropdownMenu(widget=file_menu_button)
        file_menu_dropdown.add_option(option="Clear Scene", command=self.clear_scene)
        file_menu_dropdown.add_option(option="Clear Rays", command=self.clear_rays)
        file_menu_dropdown.add_separator()
        file_menu_dropdown.add_option(option="Export Audio", command=self.export, state=tk.DISABLED)

        options_menu_dropdown = CustomDropdownMenu(widget=options_menu_button)
        options_menu_dropdown.add_option(option="Simulation", command=self.open_simulation_options)
        options_menu_dropdown.add_option(option="Scene", command=self.open_scene_options)

        return {
            "main": main_menu,
            "file_menu": file_menu_dropdown,
            "options_menu": options_menu_dropdown,
        }
    
    
    def bind_events(self): # KEYBOARD SHORTCUTS
        self.bind("<Control-m>", lambda event, tool_name='Move': self.set_tool(tool_name))
        self.bind("<Control-a>", lambda event, tool_name='Add': self.set_tool(tool_name))
        self.bind("<Control-r>", lambda event, tool_name='Resize': self.set_tool(tool_name))
        self.bind("<Control-d>", lambda event, tool_name='Delete': self.set_tool(tool_name))
        self.bind("<Control-s>", lambda event, tool_name='Select': self.set_tool(tool_name))
        
        self.bind("<Control-b>", self.bake)
        


    def set_tool(self, tool_name):
        if self.current_tool_name == tool_name:
            return

        if self.current_tool_name:
            self.tools[self.current_tool_name].deactivate()

        self.current_tool_name = tool_name
        self.tools[tool_name].activate()


    def toggle_grid(self):
        if self.show_grid.get():
            self.scene.show_grid()
        else:
            self.scene.hide_grid()

    
    def bake(self, *args):
        self.clear_rays()

        walls = [obj for obj in self.graphic_objects if isinstance(obj, Wall)]

        listners = [obj for obj in self.graphic_objects if isinstance(obj, Listener)]
        if len(listners) == 0:
            self.set_status_bar_text("Error: No listener", status="error")
            return
        elif len(listners) > 1:
            self.set_status_bar_text("Warring: Only one listener is supported at the moment")

        sound_sources = [obj for obj in self.graphic_objects if isinstance(obj, SoundSource)]
        if len(sound_sources) == 0:
            self.set_status_bar_text("Error: No sound source", status="error")
            return
        elif len(sound_sources) > 1:
            self.set_status_bar_text("Warring: Only one sound source is supported at the moment")

        simulation_thread = th.Thread(target=self.run_simulation, args=(walls, listners, sound_sources[0]))
        simulation_thread.start()
        

    def run_simulation(self, walls, listners, sound_source):
        try:
            self.algorithm_handler.run_simulation(
                scene_width = self.scene.get_width(),
                scene_height = self.scene.get_height(),
                scene_walls_reflectivity = self.settings['scene']['scene_walls_reflectivity'].get(),
                rectangular_walls = walls,
                sound_source = sound_source,
                listener = listners[0],
                reflections_amount = self.settings['simulation']['reflections_amount'].get(),
                inital_rays_amount = self.settings['simulation']['initial_rays_amount'].get(),
                min_energy_threshold = self.settings['simulation']['min_energy_threshold'].get(),
                caught_ray_callback = self.register_caught_ray,
            )
        except AlgorithmHandler.BakingException as err:
            self.set_status_bar_text(f'Baking failed. Error: {err}', status="error")
            return

        self.is_baked.set(True)
        self.audio_panel.set_caught_rays(self.caught_rays)

        self.set_status_bar_text(f'Baking succesfull. Registerd rays: {self.caught_rays_amount}', status="succes")


    def channel_id_to_name(self, channel_id):
        if channel_id == 0:
            return 'left'
        elif channel_id == 1:
            return 'right'
        else:
            raise Exception("Unknown channel id: ", channel_id)


    def register_caught_ray(self, time, energy, path, path_length, are_obstacles_on_path, channel_id):
        path = [(path[i].x, path[i].y) for i in range(path_length)]

        self.caught_rays_amount += 1 

        if not are_obstacles_on_path:
            fill = COLOR_PALETTE['accent'] 
        else:
            fill = COLOR_PALETTE['accent_dark']

        if (
            self.caught_rays_amount < 10 or 
            self.caught_rays_amount < 100 and self.caught_rays_amount % 10 == 0 or 
            self.caught_rays_amount < 1000 and self.caught_rays_amount % 100 == 0 or
            self.caught_rays_amount < 10000 and self.caught_rays_amount % 1000 == 0 or
            self.caught_rays_amount % 10000 == 0
        ):
            self.set_status_bar_text(f'Baking in process. Registered rays: {self.caught_rays_amount}')

            self.scene.create_ray(path, fill = fill)

        self.caught_rays[self.channel_id_to_name(channel_id)].append({
            'time': time,
            'energy': energy,
        })


    def set_status_bar_text(self, text = "", status="neutral"):
        if status == 'neutral':
            color = 'white'
        elif status == 'error':
            color = '#fa4d4d'
        elif status == 'succes':
            color = '#4dfa6a'
        else:
            color = 'white'

        self.status_bar_label.configure(text=text, text_color=color)


    def export(self):
        path = tk.filedialog.asksaveasfilename(
            filetypes=[('Wave File', '*.wav')],
            defaultextension='.wav'
        )

        self.audio_panel.export_with_reverb(path, self.caught_rays)


    def refresh_export_state(self, *args):
        if self.is_baked.get() and self.is_audio_file_loaded.get():
            state = tk.NORMAL
        else:
            state = tk.DISABLED
        
        for child in self.menus['file_menu'].winfo_children():
            if isinstance(child, ctk.CTkButton) and child.cget('text') == "Export Audio":
                child.configure(state = state)


    def open_simulation_options(self):
        self.simulation_settings_pop_up.open()


    def open_scene_options(self):
        self.scene_settings_pop_up.open()


    def clear_scene(self):
        self.scene.clear()

        self.is_baked.set(False)


    def clear_rays(self):
        self.scene.clear_rays()

        for channel_rays in self.caught_rays.values():
            channel_rays.clear()
        self.caught_rays_amount = 0

        self.is_baked.set(False)


if __name__ == '__main__':
    app = App()
    app.mainloop()
    # chnage style theme to clam

    # PREFORMANCE TESTS
