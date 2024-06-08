import tkinter as tk
from math import degrees

from scene_graphics.objects.graphic_objects import DynamicCircle
from styles import COLOR_PALETTE


class SoundSource(DynamicCircle):
    IS_ROTATABLE = True
    CLIPPING_PREVENTED_CLASSES = ['Wall',]

    OUTLINE_COLOR = COLOR_PALETTE['secondary']
    FILL_COLOR = COLOR_PALETTE['primary']

    RADIUS = 40
    IMAGE_PATH = 'assets/images/speaker.png'

    def __init__(self, scene, x, y, direction_angle = 90):
        super().__init__(scene, x, y, self.RADIUS, self.OUTLINE_COLOR, fill = self.FILL_COLOR)

        self.direction_angle = direction_angle

        self.icon = SoundSourceIcon(self.scene, self.x, self.y, self.radius, self.direction_angle)

        for arc in self.icon.get_arcs():
            self.add_graphic_object(arc)


    def undraw(self):
        super().undraw()
        self.icon.undraw()


    def move(self, x, y, *args, **kwargs):
        if super().move(x, y, *args, **kwargs) == False:
            return False 

        self.icon.move(x, y)

        return True
    

    def rotate(self, start_x, start_y, end_x, end_y):
        move_angle_rad = self.get_angle(start_x, start_y, self.x, self.y, end_x, end_y)

        self.direction_angle -= degrees(move_angle_rad)

        self.icon.rotate(self.direction_angle)

    
    def resize(self, x, y):
        return


    def get_resize_hover_cursor(self, x, y):
        return 'arrow'


    def get_vertically_flipped_direction_angle(self):
        return int(360 - self.direction_angle)




class SoundSourceIcon:
    ARC_GAP = 10

    ARCS_COLOR = COLOR_PALETTE['secondary']
    FILL_COLOR = COLOR_PALETTE['primary']


    def __init__(self, scene, x, y, radius, angle):
        self.scene = scene

        self.x = x
        self.y = y

        self.radius = radius

        self.angle = angle

        self.arcs_ids = []

        self.draw()


    def get_arcs(self):
        return self.arcs_ids


    def draw(self):
        for width, radius in enumerate(range(self.ARC_GAP, self.radius + self.ARC_GAP, self.ARC_GAP)):
            
            arc_id = self.scene.create_arc(
                self.x - radius,
                self.y - radius,
                self.x + radius,
                self.y + radius,
                start = self.angle - 90,
                extent = 180,
                style = tk.ARC,
                outline = self.ARCS_COLOR,
                width = width + 2,
            )

            self.arcs_ids.append(arc_id)
        


    def move(self, x, y):
        self.x+=x
        self.y+=y

        for arc_id in self.arcs_ids:
            self.scene.move(arc_id, x, y)


    def rotate(self, angle):
        for arc_id in self.arcs_ids:
            self.scene.itemconfig(arc_id, start = angle - 90)


    def undraw(self):
        for arc_id in self.arcs_ids:
            self.scene.delete(arc_id)

        self.arc_ids = []



