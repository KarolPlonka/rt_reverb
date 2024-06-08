import customtkinter as ctk
import tkinter as tk

from object_properties.materials import MATERIALS, DEFAULT_MATERIAL
from styles import COLOR_PALETTE, OPTION_MENU_STYLE, LABEL_STYLE


class PropertiesPanel(ctk.CTkFrame):

    def __init__(self, master, grid_args, *args, **kwargs):
        super().__init__(
            master=master,
            fg_color=COLOR_PALETTE['secondary'],
            *args, **kwargs
        )

        self.grid_args = grid_args

        self.selected_object = None

        self.panel_label = ctk.CTkLabel(
            self,
            text = "Properties",
            **LABEL_STYLE
        )
        self.panel_label.pack(padx=10, pady=10)

        self.material = tk.StringVar(value=DEFAULT_MATERIAL['name'])
        self.material_menu = ctk.CTkOptionMenu(
            master=self,
            variable=self.material,
            values = [material['name'] for material in MATERIALS.values()],
            command = self.material_changed,
            **OPTION_MENU_STYLE
        )
        self.material_menu.pack(padx=10, pady=10)


    def set_object(self, new_selected_object):
        self.selected_object = new_selected_object

        if new_selected_object is None:
            self.grid_remove()
            return
        
        self.grid(**self.grid_args)

        self.load_object_properites()


    def load_object_properites(self):
        self.material.set(self.selected_object.material['name'])


    def material_changed(self, *args):
        if self.selected_object:
            self.selected_object.material = MATERIALS[self.material.get()]
