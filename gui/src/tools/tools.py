from scene_graphics.objects.wall import Wall
from scene_graphics.objects.sound_source import SoundSource
from scene_graphics.objects.listener import Listener

from scene_graphics.objects.clipping import is_rectangle_clipping_with_circle


class Tool:
    def __init__(self, scene, objects, button, *args, **kwargs):
        self.scene = scene
        self.objects = objects
        self.button = button

    def activate(self):
        self.button.tool_active()

    def deactivate(self):
        self.scene.config(cursor='arrow')
        self.button.tool_inactive()

    def is_event_in_scene(self, event):
        return (
            0 < event.x < self.scene.winfo_width() and
            0 < event.y < self.scene.winfo_height()
        )
    
    def get_scene(self):
        return self.scene

    def mouse_leave(self, event):
        self.scene.config(cursor='arrow')



class Select(Tool):
    def __init__(self, scene, objects, button, properties_panel, *args, **kwargs):
        super().__init__(scene, objects, button, *args, **kwargs)
        
        self.properties_panel = properties_panel

        self.current_object = None


    def activate(self):
        super().activate()

        for obj in self.objects:
            if not obj.IS_SELECTABLE:
                continue

            obj.bind('<Motion>', self.mouse_hover)
            obj.bind('<ButtonPress-1>', lambda event, obj=obj: self.mouse_down(event, obj))
            obj.bind('<Leave>', lambda event: self.mouse_leave(event))

    
    def deactivate(self):
        super().deactivate()

        if self.current_object is not None:
            self.current_object.unselect()
            self.properties_panel.set_object(None)


        for obj in self.objects:
            if not obj.IS_SELECTABLE:
                continue
            
            obj.unbind('<Motion>')
            obj.unbind('<ButtonPress-1>')
            obj.unbind('<Leave>')

    
    def mouse_hover(self, event):
        self.scene.config(cursor='hand2')


    def mouse_down(self, event, obj):
        if self.current_object:
            self.current_object.unselect()

        if self.current_object == obj:
            self.unselect_object()
            return

        self.select_object(obj)


    def select_object(self, obj):
        self.current_object = obj
        self.current_object.select()
        self.properties_panel.set_object(self.current_object)


    def unselect_object(self):
        self.current_object.unselect()
        self.current_object = None
        self.properties_panel.set_object(None)




class Move(Tool):
    def __init__(self, scene, objects, button, *args, **kwargs):
        super().__init__(scene, objects, button, *args, **kwargs)

        self.current_object = None


    def activate(self):
        super().activate()

        self.scene.bind("<ButtonRelease-1>", self.mouse_up)

        for obj in self.objects:
            obj.bind('<ButtonPress-1>', lambda event, obj=obj: self.mouse_down(event, obj))
            obj.bind('<Motion>', self.mouse_hover)
            obj.bind('<B1-Motion>', self.mouse_drag)
            obj.bind('<Leave>', lambda event: self.mouse_leave(event))


    def deactivate(self):
        super().deactivate()

        self.scene.unbind("<Motion>")
        self.scene.unbind("<ButtonRelease-1>")

        for obj in self.objects:
            obj.unbind('<ButtonPress-1>')
            obj.unbind('<Motion>')
            obj.unbind('<B1-Motion>')


    def mouse_up(self, event):
        self.current_object = None
    

    def mouse_hover(self, event):
        self.scene.config(cursor='fleur')


    def mouse_down(self, event, obj):
        self.current_object = obj

        self.lastMouseX = event.x
        self.lastMouseY = event.y


    def mouse_drag(self, event):
        if not self.is_event_in_scene(event):
            return
        
        self.current_object.move(event.x - self.lastMouseX, event.y - self.lastMouseY, self.objects)

        self.lastMouseX = event.x
        self.lastMouseY = event.y




class Resize(Tool):

    def __init__(self, scene, objects, button, *args, **kwargs):
        super().__init__(scene, objects, button, *args, **kwargs)

        self.current_object = None
        

    def activate(self):
        super().activate()

        self.scene.bind("<ButtonRelease-1>", self.mouse_up)

        for obj in self.objects:
            obj.bind('<ButtonPress-1>', self.mouse_down)
            obj.bind('<Motion>', lambda event, obj=obj: self.mouse_hover(event, obj))
            obj.bind('<ButtonRelease-1>', self.mouse_up)
            obj.bind('<Leave>', lambda event: self.mouse_leave(event))


    def deactivate(self):
        super().deactivate()

        self.scene.unbind("<Motion>")
        self.scene.unbind("<ButtonRelease-1>")

        for obj in self.objects:
            obj.unbind('<ButtonPress-1>')
            obj.unbind('<Motion>')
            obj.unbind('<ButtonRelease-1>')
            obj.unbind('<Leave>')


    def mouse_hover(self, event, obj):
        self.current_object = obj

        cursor = self.current_object.get_resize_hover_cursor(
            x = self.scene.canvasx(event.x), 
            y = self.scene.canvasy(event.y)
        )

        self.scene.config(cursor=cursor)


    def mouse_down(self, event):
        event.x = self.scene.canvasx(event.x)
        event.y = self.scene.canvasy(event.y)

        self.current_object.unbind('<Motion>')

        self.scene.bind("<B1-Motion>", self.mouse_drag)


    def mouse_drag(self, event):
        if not self.current_object:
            return
        
        event_x = self.scene.canvasx(event.x)
        event_y = self.scene.canvasy(event.y)

        self.current_object.resize(
            x = event_x,
            y = event_y,
            clipping_objects = self.objects
        )


    def mouse_up(self, event):
        self.scene.unbind("<B1-Motion>")
        self.current_object.bind('<Motion>', lambda event, obj=self.current_object: self.mouse_hover(event, obj))



class AddWall(Tool):
    def __init__(self, scene, objects, button, *args, **kwargs):
        super().__init__(scene, objects, button, *args, **kwargs)

        self.current_object = None
        

    def activate(self):
        super().activate()

        self.scene.bind("<Button-1>", self.mouse_down)
        self.scene.bind("<ButtonRelease-1>", self.mouse_up)

        self.scene.config(cursor='crosshair')

    
    def deactivate(self):
        super().deactivate()

        self.scene.unbind("<Button-1>")


    def mouse_down(self, event):
        event.x = self.scene.canvasx(event.x)
        event.y = self.scene.canvasy(event.y)

        self.current_object = Wall(self.scene, event.x, event.y, event.x, event.y)

        if not self.current_object:
            return

        self.objects.append(self.current_object)

        self.scene.bind("<B1-Motion>", self.mouse_drag)


    def mouse_drag(*args, **kwargs):
        Resize.mouse_drag(*args, **kwargs)


    def mouse_up(self, event):
        self.scene.unbind("<B1-Motion>")




class Delete(Tool):

    def activate(self):
        super().activate()

        for obj in self.objects:
            obj.bind('<Motion>', self.delete_mouse_hover_event)
            obj.bind('<Button-1>', lambda event, obj=obj: self.mouse_click(event, obj))
            obj.bind('<Leave>', lambda event: self.mouse_leave(event))


    def deactivate(self):
        super().deactivate()

        for obj in self.objects:
            obj.unbind('<Motion>')
            obj.unbind('<Button-1>')
            obj.unbind('<Leave>')


    def delete_mouse_hover_event(self, event):
        self.scene.config(cursor='X_cursor')


    def mouse_click(self, event, obj):
        obj.unbind('<Motion>')
        obj.unbind('<Button-1>')
        obj.unbind('<Leave>')

        obj.undraw()

        self.objects.remove(obj)

        self.scene.config(cursor='arrow')



class SetSoundSource(Tool):
    def __init__(self, scene, objects, button, *args, **kwargs):
        super().__init__(scene, objects, button, *args, **kwargs)


    def activate(self):
        super().activate()

        self.scene.bind("<Button-1>", self.mouse_click)
        self.scene.config(cursor='crosshair')


    def deactivate(self):
        super().deactivate()

        self.scene.unbind("<Button-1>")

        self.scene.config(cursor='arrow')


    def mouse_click(self, event):
        event.x = self.scene.canvasx(event.x)
        event.y = self.scene.canvasy(event.y)
        
        for obj in self.objects:
            if isinstance(obj, SoundSource):
                obj.undraw()
                self.objects.remove(obj)

        sound_source = SoundSource(self.scene, event.x, event.y)

        if sound_source.is_clipping(self.objects):
            sound_source.undraw()
            return

        self.objects.append(sound_source)



class AddListner(Tool):
    def activate(self):
        super().activate()

        self.scene.bind("<Button-1>", self.mouse_down)
        self.scene.config(cursor='crosshair')


    def deactivate(self):
        super().deactivate()

        self.scene.unbind("<Button-1>")
        self.scene.unbind("<B1-Motion>")

        self.scene.config(cursor='arrow')


    def mouse_down(self, event):
        event.x = self.scene.canvasx(event.x)
        event.y = self.scene.canvasy(event.y)

        self.current_listner = Listener(self.scene, event.x, event.y)

        if self.current_listner.is_clipping(self.objects):
            self.current_listner.undraw()
            self.current_listner = None
            return

        self.objects.append(self.current_listner)

        self.scene.bind("<B1-Motion>", self.mouse_drag)


    def mouse_drag(self, event):
        if not self.current_listner:
            return

        self.current_listner.resize(
            x = self.scene.canvasx(event.x),
            y = self.scene.canvasy(event.y),
            offset = Listener.RADIUS
        )




class Rotate(Tool):
    def __init__(self, scene, objects, button, *args, **kwargs):
        super().__init__(scene, objects, button, *args, **kwargs)

        self.current_object = None


    def activate(self):
        super().activate()

        for obj in self.objects:
            if not obj.IS_ROTATABLE:
                continue

            obj.bind('<ButtonPress-1>', lambda event, obj=obj: self.mouse_down(event, obj))
            obj.bind('<Motion>', self.mouse_hover)
            obj.bind('<B1-Motion>', self.mouse_drag)
            obj.bind('<Leave>', lambda event: self.mouse_leave(event))


    def deactivate(self):
        super().deactivate()

        self.scene.unbind("<Motion>")
        self.scene.unbind("<ButtonRelease-1>")

        for obj in self.objects:
            if not obj.IS_ROTATABLE:
                continue
            
            obj.unbind('<ButtonPress-1>')
            obj.unbind('<Motion>')
            obj.unbind('<B1-Motion>')
    

    def mouse_hover(self, event):
        self.scene.config(cursor='exchange')


    def mouse_down(self, event, obj):
        self.current_object = obj

        self.lastMouseX = event.x
        self.lastMouseY = event.y


    def mouse_drag(self, event):
        if not self.is_event_in_scene(event):
            return
        
        self.current_object.rotate(self.lastMouseX, self.lastMouseY, event.x, event.y)

        self.lastMouseX = event.x
        self.lastMouseY = event.y