import pyglet
import math
import vec2
import gfx

class ID:

    VARIABLE = 0
    APPLICATION = 1
    ABSTRACTION = 2

    def __init__(self, kind, color_id=None):

        self.kind = kind
        self.parent = None
        self.value = None
        self.argument = None
        self.binds_id = None
        self.color_id = color_id

        self.temp_value = None

    def draw(self, x, y, scale, opacity=1.0):

        if self.binds_id != None:
            color = colors[self.binds_id]
        else:
            color = (0.9, 0.9, 0.9, 1.0)
        draw_rect(x, y+scale/6, scale/3, scale*2/3, darken(color, 0.5))

        if self.color_id != None:
            color = colors[self.color_id]
        else:
            color = colors[0]
        draw_rect(x+scale/3, y+scale/6, scale*2/3, scale*2/3, darken(color, opacity))
        #draw_rect(x+scale/32.0, y+scale/32.0, (1-1/16.0)*scale, (1-1/16.0)*scale, darken(color, opacity))

        if self.temp_value:
            value = self.temp_value
        else:
            value = self.value

        value_x, value_y, value_scale = self.get_offset_and_scale(scale, for_value=True)
        if self.kind == ID.VARIABLE:
            if value != None:
                value.draw(x+value_x, y+value_y, value_scale)

        elif self.kind == ID.APPLICATION:
            value.draw(x+value_x, y+value_y, value_scale)
            self.argument.draw(x+scale/4, y+scale/4, scale/3)

        elif self.kind == ID.ABSTRACTION:
            value.draw(x+value_x, y+value_x, value_scale)

    def get_offset_and_scale(self, scale, for_value=False, for_argument=False):
        xoffset = scale/3
        yoffset = scale/6
        scale *= 2/3

        if for_value:
            if self.kind == ID.VARIABLE:
                if self.color_id > 0:
                    return xoffset+scale/16, yoffset+scale/16, scale*7/8
                else:
                    return xoffset, yoffset, scale
            elif self.kind == ID.APPLICATION:
                return xoffset+scale/2, yoffset+scale/4, scale/2
            elif self.kind == ID.ABSTRACTION:
                return xoffset, yoffset, scale

        elif for_argument:
            return xoffset+scale/4, yoffset+scale/4, scale/3

    def get_hover_id(self, rel_mouse_x, rel_mouse_y, scale):

        base_y = scale/6
        top_y = scale*5/6
        left_x = 0
        right_x = scale
        sep_x = scale/3

        if rel_mouse_y > base_y and rel_mouse_y < top_y and rel_mouse_x > sep_x and rel_mouse_x < right_x:
            
            sub_hover = None

            if self.value != None:
                value_x, value_y, value_scale = self.get_offset_and_scale(scale, for_value=True)
                sub_hover = self.value.get_hover_id(rel_mouse_x-value_x, rel_mouse_y-value_y, value_scale)

            if sub_hover == None and self.argument != None:
                argument_x, argument_y, argument_scale = self.get_offset_and_scale(scale, for_argument=True)
                sub_hover = self.argument.get_hover_id(rel_mouse_x-argument_x, rel_mouse_y-argument_y, argument_scale)


            if sub_hover == None:
                return self
            else:
                return sub_hover

    def assign(self, other):

        if self.kind == ID.VARIABLE:
            self.value = other
            other.parent = self

        elif other.kind == ID.VARIABLE:
            other.value = self
            self.parent = other

        else:
            print("Cannot assign term to non-variable term!")

    def unassign(self):
        if self.kind == ID.VARIABLE:
            self.value.parent = None
            self.value = None
        elif self.parent.kind == ID.VARIABLE and self.parent.value == self:
            self.parent.value = None
            self.parent = None

class Entity:


    def __init__(self, x, y, scale, var_id):

        self.x = x
        self.y = y
        self.scale = scale

        self.id = var_id

        self.drag = False
        self.hover_over = 0
        self.being_created = False

        self.var_id = self.temp_var_id = var_id
        self.colliding = False
        self.delete_on_release = 0

        self.opacity = 1.0


    def _del(self):

        entities.remove(self)

    def transform_to_local_coordinates(self, xoffset, yoffset, scale_factor):
        return ((self.x-0.5*self.scale+xoffset)*scale_factor+window.width/2,
                (self.y-0.5*self.scale+yoffset)*scale_factor+window.height/2,
                scale_factor*self.scale)

    def draw(self, scale_factor, xoffset, yoffset):

        x, y, scale = self.transform_to_local_coordinates(xoffset, yoffset, scale_factor)

        if self == drag_entity and drag_entity.delete_on_release > 0:
            pass
        
        else:

            if self == hover_entity:
                opacity = 0.5
            else:
                opacity = self.opacity
            self.id.draw(x, y, scale, opacity=opacity)

    def move(self, dx, dy):

        self.x += dx
        self.y += dy

    def scale_around_center(self, factor, x, y):
        self.scale *= factor
        self.x = x+(self.x-x)*factor
        self.y = y+(self.y-y)*factor

    def on_mouse_release(self):

        global drag_entity

        if self == drag_entity:
            drag_entity = None

            if self.delete_on_release > 0:
                self._del()

            if hover_entity != None:

                pass


        elif self.being_created:

            if self.kind == Entity.VARIABLE:
                self._del()

            elif self.kind == Entity.ABSTRACTION:
                self.being_created = False
                available_ids.append(self.var_id)
                vars_by_id[self.var_id].remove(self)
                self.var_id = None

        else:
            self.colliding = False
            if self.var_id != None and self.temp_var_id != self.var_id:
                if self.var_id != None:
                    vars_by_id[self.var_id].remove(self)
                if vars_by_id[self.var_id] == []:
                    available_ids.append(self.var_id)
                self.var_id = self.temp_var_id
                vars_by_id[self.var_id].append(self)

    def is_ancestor(self, of):

        if of == None:
            return False
        elif of in self.childs:
            return True
        else:
            return self.is_ancestor(of.parent)



window = pyglet.window.Window(1024, 768)
window.set_exclusive_mouse(True)

colors = (
        (0.7, 0.7, 0.7, 1.0),
        (0.149, 0.078, 0.757, 1.0),
        (0.545, 0.024, 0.729, 1.0),
        (0.929, 0.988, 0.0, 1.0),
        (1.0, 0.78, 0.0, 1.0),
        )

def draw_rect(x, y, w, h, color):
    pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES, [0, 1, 2, 0, 2, 3],
            ('v2i', (int(x), int(y), int(x+w), int(y), int(x+w), int(y+h), int(x), int(y+h))),
            ('c4f', color*4)
            )

def darken(color, factor):
    return (color[0]*factor, color[1]*factor, color[2]*factor, color[3])

def draw_line(start, end, thickness, color):

    endpoint_offset = vec2.norm(vec2.sub(start, end))
    endpoint_offset[0], endpoint_offset[1] = -endpoint_offset[1], endpoint_offset[0] #rotate 90 degrees
    endpoint_offset = vec2.mul(endpoint_offset, thickness/2)

    pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES, [0, 1, 2, 0, 2, 3],
            ('v2i', (int(start[0]+endpoint_offset[0]), int(start[1]+endpoint_offset[1]), int(end[0]+endpoint_offset[0]), int(end[1]+endpoint_offset[1]), int(end[0]-endpoint_offset[0]), int(end[1]-endpoint_offset[1]), int(start[0]-endpoint_offset[0]), int(start[1]-endpoint_offset[1]))),
            ('c4f', color*4)
            )

scale_factor = 400.0
start_scale_factor = 400.0
xoffset = 0.0
yoffset = 0.0
start_drag_x = 0.0
start_drag_y = 0.0
mouse_sensitivity = 400.0
lock_position = False
zooming = False

entities = []
hover_entity = None
drag_entity = None

available_color_ids = [0, 1, 2, 3, 4]

IDs = []

crosshair = pyglet.graphics.vertex_list(4,
        ('v2i', (window.width//2, window.height//2+10, window.width//2, window.height//2-10, window.width//2+10, window.height//2, window.width//2-10, window.height//2)),
        ('c4f', (0.8, 0.8, 0.8, 0.8)*4)
        )

base_gradient = pyglet.image.load("gradient.png")

fpsclock = pyglet.clock.ClockDisplay()

def check_hover():

    global hover_entity

    old_hover_entity = hover_entity
    hover_entity = None

    for entity in entities:
        if entity != drag_entity and not entity.being_created:
            x, y, scale = entity.transform_to_local_coordinates(xoffset, yoffset, scale_factor)
            entity.hover_over = entity.id.get_hover_id(window.width/2-x, window.height/2-y, scale)

            if entity.hover_over != None:
                hover_entity = entity

    if hover_entity != old_hover_entity and old_hover_entity != None:
        on_hover_stop(old_hover_entity)

def on_hover_stop(entity):

    entity.id.temp_value = None


@window.event
def on_draw():

    window.clear()

    for entity in entities:
        entity.draw(scale_factor, xoffset, yoffset)

    #draw crosshair
    crosshair.draw(pyglet.gl.GL_LINES)

    fpsclock.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    
    global xoffset, yoffset
    global scale_factor

    if not lock_position and not zooming:
        xoffset -= dx/mouse_sensitivity
        yoffset -= dy/mouse_sensitivity

    elif zooming:
        scale_factor *= math.exp(0.01*vec2.inner( (dx, dy), (1.0, 0.0)))

    check_hover()

@window.event
def on_mouse_press(x, y, button, modifiers):

    global start_drag_x, start_drag_y
    global lock_position
    global drag_entity

    start_drag_x, start_drag_y = xoffset, yoffset
    lock_position = False

    if hover_entity != None:

        if modifiers & pyglet.window.key.MOD_SHIFT:#?
            new_entity = Entity(kind=hover_entity.kind, x=hover_entity.x, y=hover_entity.y, scale=hover_entity.scale, var_id=hover_entity.var_id)
            entities.append(new_entity)
            drag_entity = new_entity

        else:
            if hover_entity.id == hover_entity.hover_over: # <=> hover_entity.id.parent == None [read: an id with a parent can not be assigned to an entity] #?ds
                drag_entity = hover_entity

            else:
                free_id = hover_entity.hover_over
                new_entity = Entity(x=-xoffset, y=-yoffset, scale=50, var_id=free_id)
                if free_id == free_id.parent.value:

                    if free_id.parent.kind == ID.APPLICATION:
                        free_id.parent.value = free_id.parent.argument
                        free_id.parent.kind = ID.VARIABLE
                        free_id.parent.color_id = 0
                    elif free_id.parent.kind == ID.ABSTRACTION:
                        free_id.parent.binds_id = 0
                    free_id.parent.value = None
                    free_id.parent = None

                elif free_id == free_id.parent.argument: # <=> free_id.parent.kind == ID.APPLICATION #?ds
                    #effectively replace free_id.parent with free_id.parent.value in all occurences
                    free_id.parent.argument = None
                    free_id.parent.kind = ID.VARIABLE
                    free_id.parent.color_id = 0 # make it an 'invisible' variable that just passes the value data through
                    free_id.parent = None


    if hover_entity == None:
        try:
            color_id = available_color_ids.pop()
        except IndexError:
            raise(BaseException, ("Too many vars. Also, I do not like python exception handling."))

        new_id = ID(kind=ID.VARIABLE, color_id=color_id)
        IDs.append(new_id)
        new_entity = Entity(x=-xoffset, y=-yoffset, scale=0, var_id=new_id)
        entities.append(new_entity)
        new_entity.being_created = True
        drag_entity = new_entity

    check_hover()

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):

    global xoffset, yoffset
    global drag_entity

    if not zooming:
        dx /= mouse_sensitivity
        dy /= mouse_sensitivity
        xoffset -= dx
        yoffset -= dy

    if drag_entity != None:

        if drag_entity.being_created:
            diff = vec2.abs(vec2.sub( (xoffset, yoffset), (start_drag_x, start_drag_y)))
            drag_entity.scale = 100/scale_factor
            drag_entity.x = -xoffset
            drag_entity.y = -yoffset

            opacity = abs(diff/drag_entity.scale)

            if opacity >= 1.0:
                drag_entity.opacity = 1.0
                drag_entity.being_created = False
            else:
                drag_entity.opacity = opacity

        else:
            if not zooming:
                drag_entity.move(dx, dy)

            elif zooming:
                factor = math.exp(0.01* vec2.inner ((dx, dy), (1.0, 0.0)) )
                drag_entity.scale_around_center(factor, -xoffset, -yoffset)

        for entity in entities:
            if entity != drag_entity:
                # collision detection
                xdiff = abs(entity.x-drag_entity.x)
                ydiff = abs(entity.y-drag_entity.y)
                min_diff = (entity.scale+drag_entity.scale)/2

                if xdiff < min_diff and ydiff < min_diff:

                    if entity.colliding == False:
                        entity.colliding = True
                        drag_entity.delete_on_release += 1

                else:
                    if entity.colliding == True:
                        entity.colliding = False
                        drag_entity.delete_on_release -= 1

    check_hover()

    if hover_entity:

        assert hover_entity.id.value == None #TODO: general case
        assert hover_entity.colliding == True # mouse cursor should not be able to be outside of drag_entity
        if -xoffset < hover_entity.x:
            #copy binder
            pass
        else:
            hover_entity.id.temp_value = drag_entity.id #reset is in check_hover


@window.event
def on_mouse_release(x, y, button, modifiers):

    stable_entities = entities[:]
    for entity in stable_entities:
        entity.on_mouse_release()

    check_hover()

@window.event
def on_key_press(key, modifiers):

    global lock_position
    global start_drag_x, start_drag_y
    global zooming
    global start_scale_factor

    if key == pyglet.window.key.LSHIFT or key == pyglet.window.key.RSHIFT:
        lock_position = True

    elif key == pyglet.window.key.LCTRL or key == pyglet.window.key.RCTRL:
        start_drag_x, start_drag_y = xoffset, yoffset
        start_scale_factor = scale_factor
        zooming = True

@window.event
def on_key_release(key, modifiers):

    global lock_position
    global zooming

    if key == pyglet.window.key.LSHIFT or key == pyglet.window.key.RSHIFT:
        lock_position = False

    elif key == pyglet.window.key.LCTRL or key == pyglet.window.key.RCTRL:
        zooming = False

pyglet.app.run()
