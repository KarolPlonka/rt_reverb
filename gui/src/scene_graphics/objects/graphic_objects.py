from scene_graphics.objects.clipping import is_rectangle_clipping_with_circle
from styles import COLOR_PALETTE
from math import atan2

class DynamicGraphicObject:
    IS_SELECTABLE = False
    IS_ROTATABLE = False

    CLIPPING_PREVENTED_CLASSES = []

    def __init__(self, scene):
        self.scene = scene

        self._graphic_object_ids = []

        self._original_colors = []


    def undraw(self):
        for graphic_object_id in self._graphic_object_ids:
            self.scene.delete(graphic_object_id)


    def add_graphic_object(self, graphic_object_id):
        self._graphic_object_ids.append(graphic_object_id)
        self._original_colors.append(None)


    def bind(self, event, function):
        for graphic_object_id in self._graphic_object_ids:
            self.scene.tag_bind(graphic_object_id, event, function)


    def unbind(self, event):
        for graphic_object_id in self._graphic_object_ids:
            self.scene.tag_unbind(graphic_object_id, event)
    

    def select(self):
        for i, graphic_object_id in enumerate(self._graphic_object_ids):
            self._original_colors[i] = self.scene.itemcget(graphic_object_id, 'outline')
            self.scene.itemconfig(graphic_object_id, outline=COLOR_PALETTE['accent'])


    def unselect(self):
        for i, graphic_object_id in enumerate(self._graphic_object_ids):
            if self._original_colors[i]:
                self.scene.itemconfig(graphic_object_id, outline=self._original_colors[i])




class DynamicCircle(DynamicGraphicObject):
    DEFAULT_OUTLINE_WIDTH = 5

    MIN_RADIUS = 10
    MAX_RADIUS = 100

    def __init__(self, scene, x, y, radius, color = None, width = DEFAULT_OUTLINE_WIDTH, fill = None):
        super().__init__(scene)

        self.x = x
        self.y = y
        self.radius = radius

        self.circle = self.scene.create_oval(
            x - radius,
            y - radius, 
            x + radius,
            y + radius,
            width = width,
            outline = color,
            fill = fill,
        )

        self.add_graphic_object(self.circle)
    

    def get_center(self):
        return self.x, self.y
    

    def get_radius(self):
        return self.radius
    

    def get_resize_hover_cursor(self, x, y):
        return 'sizing'
    

    def move(self, x, y, clipping_objects = []):
        new_x = self.x + x
        new_y = self.y + y
        
        if clipping_objects and self.is_clipping(clipping_objects, new_x = new_x, new_y = new_y):
            return False
        
        self.x = new_x
        self.y = new_y
        
        self.scene.move(self.circle, x, y)

        return True


    def resize(self, x, y, offset = 0, clipping_objects = []):
        radius = ( (self.x - x)**2 + (self.y - y)**2 )**0.5 + offset

        if radius < self.MIN_RADIUS:
            radius = self.MIN_RADIUS

        if radius > self.MAX_RADIUS:
            radius = self.MAX_RADIUS

        if self.is_clipping(clipping_objects, new_radius = radius):
            return False

        self.radius = radius

        self.scene.coords(
            self.circle,
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
        )

        return True


    def get_angle(self, x1, y1, x_mid, y_mid, x3, y3):
        angle = atan2(y3 - y_mid, x3 - x_mid) - atan2(y1 - y_mid, x1 - x_mid)

        return angle


    def is_clipping(self, other_objects, new_radius = None, new_x = None, new_y = None):
        if not other_objects:
            return False

        radius = new_radius if new_radius else self.radius
        x = new_x if new_x else self.x
        y = new_y if new_y else self.y

        for other_object in other_objects:
            if other_object.__class__.__name__ not in self.CLIPPING_PREVENTED_CLASSES:
                continue

            if other_object.__class__.__name__ == 'Wall':
                if is_rectangle_clipping_with_circle(
                    other_object.x1, other_object.y1, other_object.x2, other_object.y2,
                    x, y, radius 
                ):
                    return True
                else:
                    continue
            
            raise Exception(f'Checking for clipping with {other_object.__class__.__name__} and {self.__class__.__name__} is not implemented')
                
        return False