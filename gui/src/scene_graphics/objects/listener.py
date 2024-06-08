import math
import tkinter as tk

from scene_graphics.objects.graphic_objects import DynamicCircle
from styles import COLOR_PALETTE

class Listener(DynamicCircle):
    IS_ROTATABLE = True
    CLIPPING_PREVENTED_CLASSES = ['Wall',]

    OUTLINE_COLOR = COLOR_PALETTE['secondary']
    FILL_COLOR = COLOR_PALETTE['primary']
    RADIUS = 25
    WIDTH = 5

    ICON_PATH = 'assets/icons/microphone.png'

    CHANNEL_CRICLE_RADIUS = 7 

    def __init__(self, scene, center_x, center_y, radius = RADIUS):
        super().__init__(scene, center_x, center_y, radius, self.OUTLINE_COLOR, self.WIDTH, fill = self.FILL_COLOR)

        self.icon = tk.PhotoImage(file = self.ICON_PATH)

        self.icon_id = self.scene.create_image(
            center_x,
            center_y,
            image = self.icon,
        )

        self.add_graphic_object(self.icon_id)

        self.left_channel_point = {
            "point": [center_x - radius, center_y],
            "circle": self.scene.create_oval(
                center_x - radius - self.CHANNEL_CRICLE_RADIUS,
                center_y - self.CHANNEL_CRICLE_RADIUS,
                center_x - radius + self.CHANNEL_CRICLE_RADIUS,
                center_y + self.CHANNEL_CRICLE_RADIUS,
                fill = COLOR_PALETTE['secondary_triadic_1'],
                width = 0,
            ),
        }
        
        self.right_channel_point = {
            "point": [center_x + radius, center_y],
            "circle": self.scene.create_oval(
                center_x + radius - self.CHANNEL_CRICLE_RADIUS,
                center_y - self.CHANNEL_CRICLE_RADIUS,
                center_x + radius + self.CHANNEL_CRICLE_RADIUS,
                center_y + self.CHANNEL_CRICLE_RADIUS,
                fill = COLOR_PALETTE['secondary_triadic_2'],
                width = 0,
            ),
        }

        self.add_graphic_object(self.left_channel_point['circle'])
        self.add_graphic_object(self.right_channel_point['circle'])


    def rotate(self, start_x, start_y, end_x, end_y):
        move_angle_rad = self.get_angle(start_x, start_y, self.x, self.y, end_x, end_y)

        angle_cos = math.cos(move_angle_rad)
        angle_sin = math.sin(move_angle_rad)

        x_diff = self.right_channel_point['point'][0] - self.x
        y_diff = self.right_channel_point['point'][1] - self.y

        new_x = self.x + angle_cos * x_diff - angle_sin * y_diff
        new_y = self.y + angle_sin * x_diff + angle_cos * y_diff

        self.set_channel_point(self.right_channel_point, new_x, new_y)
        self.set_channel_point(self.left_channel_point, 2 * self.x - new_x, 2 * self.y - new_y)


    def set_channel_point(self, channel, x, y):
        channel['point'] = [x, y]

        self.scene.coords(
            channel['circle'],
            x - self.CHANNEL_CRICLE_RADIUS,
            y - self.CHANNEL_CRICLE_RADIUS,
            x + self.CHANNEL_CRICLE_RADIUS,
            y + self.CHANNEL_CRICLE_RADIUS,
        )
    

    def move(self, x, y, *args, **kwargs):
        if super().move(x, y, *args, **kwargs) == False:
            return False 

        self.scene.move(self.icon_id, x, y)

        self.set_channel_point(self.left_channel_point, self.x - self.radius, self.y)
        self.set_channel_point(self.right_channel_point, self.x + self.radius, self.y)

        return True


    def resize(self, x, y, *args, **kwargs):
        if super().resize(x, y, *args, **kwargs) == False:
            return False

        self.set_channel_point(self.left_channel_point, self.x - self.radius, self.y)
        self.set_channel_point(self.right_channel_point, self.x + self.radius, self.y)

    
    def undraw(self):
        super().undraw()

        self.scene.delete(self.left_channel_point['circle'])
        self.scene.delete(self.right_channel_point['circle'])

        self.scene.delete(self.icon_id)


    def get_left_channel_point(self):
        return self.left_channel_point['point']


    def get_right_channel_point(self):
        return self.right_channel_point['point']
    