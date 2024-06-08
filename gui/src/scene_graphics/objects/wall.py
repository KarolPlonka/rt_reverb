from scene_graphics.objects.graphic_objects import DynamicGraphicObject
from scene_graphics.objects.clipping import is_rectangle_clipping_with_circle
from object_properties.materials import DEFAULT_MATERIAL
from styles import COLOR_PALETTE


class Wall(DynamicGraphicObject):
    HOVER_TRESHOLD = 10
    WIDTH = 10

    IS_SELECTABLE = True
    CAN_CLIP_WITH_WALL = True
    CLIPPING_PREVENTED_CLASSES = ['Listener', 'SoundSource', ]

    def __init__(self, scene, x1, y1, x2, y2):
        super().__init__(scene)
        
        self.x1 = x1 
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.rectangle = self.scene.create_rectangle(
            x1, y1, x2, y2,
            width = Wall.WIDTH,
            outline = COLOR_PALETTE['secondary']
        )

        self.add_graphic_object(self.rectangle)

        self.xDragged = None
        self.yDragged = None

        self.material = DEFAULT_MATERIAL


    def get_coords(self):
        return self.x1, self.y1, self.x2, self.y2


    def move(self, x, y, clipping_objects = []):
        new_x1 = self.x1 + x
        new_y1 = self.y1 + y
        new_x2 = self.x2 + x
        new_y2 = self.y2 + y

        if clipping_objects and self.is_clipping(clipping_objects, new_x1, new_y1, new_x2, new_y2):
            return False

        self.x1 = new_x1
        self.y1 = new_y1
        self.x2 = new_x2
        self.y2 = new_y2

        self.scene.coords(self.rectangle, self.x1, self.y1, self.x2, self.y2)

        return True


    def resize(self, x, y, clipping_objects = []):
        new_x1 = self.x1
        new_x2 = self.x2
        new_y1 = self.y1
        new_y2 = self.y2

        if not self.xDragged and not self.yDragged:
            new_x1 = x
            new_y1 = y            

        if self.xDragged:
            if self.xDragged == 'x1':
                new_x1 = x
            else:
                new_x2 = x

        if self.yDragged:
            if self.yDragged == 'y1':
                new_y1 = y
            else:
                new_y2 = y

        if clipping_objects and self.is_clipping(clipping_objects, new_x1, new_y1, new_x2, new_y2):
            return False
        
        self.x1 = new_x1
        self.y1 = new_y1
        self.x2 = new_x2
        self.y2 = new_y2

        self.scene.coords(self.rectangle, self.x1, self.y1, self.x2, self.y2)

        return True


    def get_resize_hover_cursor(self, x, y):
        distances = {
            'x1': abs(self.x1 - x),
            'x2': abs(self.x2 - x),
            'y1': abs(self.y1 - y),
            'y2': abs(self.y2 - y),
        }

        minDistanceX = min(distances['x1'], distances['x2'])
        minDistanceY = min(distances['y1'], distances['y2'])

        self.xDragged = None
        self.yDragged = None

        if minDistanceX < self.HOVER_TRESHOLD:
            self.xDragged = 'x1' if minDistanceX == distances['x1'] else 'x2'
        
        if minDistanceY < self.HOVER_TRESHOLD:
            self.yDragged = 'y1' if minDistanceY == distances['y1'] else 'y2'

        if self.xDragged and self.yDragged:
            return 'diamond_cross'
        elif self.xDragged:
            return 'sb_h_double_arrow'
        elif self.yDragged:
            return 'sb_v_double_arrow'


    def get_bottom_left_point(self):
        if self.x1 < self.x2:
            x = self.x1
        else:
            x = self.x2

        if self.y1 < self.y2:
            y = self.y1
        else:
            y = self.y2

        return x, y
    

    def get_top_right_point(self):
        if self.x1 > self.x2:
            x = self.x1
        else:
            x = self.x2

        if self.y1 > self.y2:
            y = self.y1
        else:
            y = self.y2

        return x, y
    

    def get_reflectivity(self):
        return 1 - self.material['absorption']
    

    def get_speed_of_sound_cm_per_sec(self):
        return self.material['speed_of_sound'] * 100
    

    def is_clipping(self, other_objects, new_x1 = None, new_y1 = None, new_x2 = None, new_y2 = None):
        x1 = new_x1 if new_x1 else self.x1
        y1 = new_y1 if new_y1 else self.y1
        x2 = new_x2 if new_x2 else self.x2
        y2 = new_y2 if new_y2 else self.y2

        for other_object in other_objects:
            if other_object.__class__.__name__ == 'Wall':
                continue

            if other_object.__class__.__name__ in ['Listener', 'SoundSource']:
                if is_rectangle_clipping_with_circle(
                    x1, y1, x2, y2,
                    other_object.x, other_object.y, other_object.radius
                ):
                    return True
                else:
                    continue
            
            raise Exception(f'Checking for clipping with {other_object.__class__.__name__} and {self.__class__.__name__} is not implemented')
                
        return False



    def set_coords(self, x1, y1, x2, y2):
        self.x1 = x1 
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.scene.coords(self.rectangle, x1, y1, x2, y2)



