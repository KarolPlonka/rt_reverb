import customtkinter as ctk

from styles import COLOR_PALETTE


class Scene(ctk.CTkCanvas):
    BG_COLOR = COLOR_PALETTE['primary']
    GRID_COLOR = COLOR_PALETTE['primary_light']
    
    def __init__(self, master, settings, is_grid_shown, graphic_objects, *args, **kwargs):
        self.settings = settings
        self.is_grid_shown = is_grid_shown
        self.graphic_objects = graphic_objects

        self.add_settings_callbacks(settings)

        super().__init__(
            master = master,
            width = self.settings['scene_width'].get(),
            height = self.settings['scene_height'].get(),
            bg = self.BG_COLOR,
            scrollregion = (0, 0, self.settings['scene_width'].get(), self.settings['scene_height'].get()),
            *args, **kwargs
        )

        self.grid_lines = []

        self.set_grid_lines(self.settings['grid_size'].get())

        # self.cur_zoom = 1

        # self.camera = SceneCamera(self)

        self.previous_cursor = 'arrow'

        self.bind_events()


    def get_height(self):
        return self.settings['scene_height'].get()
    

    def get_width(self):
        return self.settings['scene_width'].get()
    

    def add_settings_callbacks(self, settings):
        settings['scene_width'].trace_add("write", self.on_settings_change)
        settings['scene_height'].trace_add("write", self.on_settings_change)
        settings['grid_size'].trace_add("write", self.on_settings_change)


    def on_settings_change(self, *args):
        self.config(
            width = self.settings['scene_width'].get(),
            height = self.settings['scene_height'].get(),
            scrollregion = (0, 0, self.settings['scene_width'].get(), self.settings['scene_height'].get())
        )

        new_spacing = self.settings['grid_size'].get()

        if isinstance(new_spacing, int) and new_spacing > 0:
            self.hide_grid()
            self.set_grid_lines(new_spacing)
            self.is_grid_shown.set(True)
            self.show_grid()



    def bind_events(self):
        self.bind("<ButtonPress-3>", self.drag_mouse_down_event)
        self.bind("<B3-Motion>", self.drag_mouse_move_event)
        self.bind("<ButtonRelease-3>", self.drag_mouse_up_event)


    def drag_mouse_down_event(self, event):
        self.previous_cursor = self.cget("cursor")
        self.config(cursor="fleur")

        self.scan_mark(event.x, event.y)


    def drag_mouse_move_event(self, event):
        self.scan_dragto(event.x, event.y, gain=1)


    def drag_mouse_up_event(self, event):
        self.config(cursor=self.previous_cursor)


    def set_grid_lines(self, spacing):
        self.grid_lines = []

        for offsest in range(0, self.settings['scene_width'].get(), spacing):
            line = self.create_line(offsest, 0, offsest, self.settings['scene_height'].get(), fill=self.GRID_COLOR, state="hidden", tags="grid")
            self.tag_lower(line)
            self.grid_lines.append(line)

        for offsest in range(0, self.settings['scene_height'].get(), spacing):
            line = self.create_line(0, offsest, self.settings['scene_width'].get(), offsest, fill=self.GRID_COLOR, state="hidden", tags="grid")
            self.grid_lines.append(line)

    
    def show_grid(self):
        for line in self.grid_lines:
            self.itemconfig(line, state="normal")
            self.tag_lower(line)


    def hide_grid(self):
        for line in self.grid_lines:
            self.itemconfig(line, state="hidden")


    def create_ray(self, *args, **kwargs):
        ray_id = self.create_line(*args, **kwargs, tags="ray")
        self.tag_lower(ray_id)


    def clear(self):
        for graphic_object in self.graphic_objects:
            graphic_object.undraw()

        self.graphic_objects.clear()

        self.clear_rays()


    def clear_rays(self):
        self.delete("ray")


    def get_graphic_objects(self):
        return self.graphic_objects   
    