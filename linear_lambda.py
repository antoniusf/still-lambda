import pyglet
import math
import vec2
import gfx

class Entity:

    VARIABLE = 0
    APPLICATION = 1
    ABSTRACTION = 2

    def __init__(self, kind, x, y, scale=1, var_id=None):

        self.x = x
        self.y = y
        self.scale = scale

        self.drag = False
        self.hover_over = 0
        self.being_created = False

        self.kind = kind

        self.childs = []
        self.argument_child = None
        self.parent = None

        self.var_id = self.temp_var_id = var_id
        self.colliding = False
        self.delete_on_release = 0

        self.opacity = 1.0
        self.apply_tray_opacity = 0.0


    def _del(self):

        entities.remove(self)

        if self.kind == Entity.VARIABLE:
            vars_by_id[self.var_id].remove(self)
            if vars_by_id[self.var_id] == []:
                available_ids.append(self.var_id)

    def draw(self, scale_factor, xoffset, yoffset):

        local_x = (self.x-0.5*self.scale+xoffset)*scale_factor+window.width/2
        local_y = (self.y-0.5*self.scale+yoffset)*scale_factor+window.height/2
        local_scale = scale_factor*self.scale

        self.apply_tray_opacity = 0.0
        if self == hover_entity:
            self.apply_tray_opacity = 1.0

        if self.kind == Entity.VARIABLE:

            if self.childs != []:
                self.apply_tray_opacity = 1.0
            #draw box

            color = colors[self.temp_var_id]
            draw_rect(local_x, local_y, local_scale, local_scale, darken(color, 0.5*self.opacity))
            draw_rect(local_x+local_scale/32.0, local_y+local_scale/32.0, (1-1/16.0)*local_scale, (1-1/16.0)*local_scale, darken(color, self.opacity))


            #draw connections to other variables
            other_var = None
            old_diff = 0
            for var in vars_by_id[self.var_id]:

                if var != self:
                    diff = vec2.abs(vec2.sub((self.x, self.y), (var.x, var.y)))

                    if other_var == None or diff < old_diff:
                        old_diff = diff
                        other_var = var

            if other_var:
                other_var_center_x = (other_var.x+xoffset)*scale_factor+window.width/2
                other_var_center_y = (other_var.y+yoffset)*scale_factor+window.height/2
                gfx.draw_textured_aa_line((local_x+0.5*local_scale, local_y+0.5*local_scale), (other_var_center_x, other_var_center_y), local_scale/32.0, base_gradient.get_texture())

        elif self.kind == Entity.APPLICATION:

            color = (0.3, 0.3, 0.3, 1.0)
            draw_rect(local_x, local_y, 1*local_scale, 1*local_scale, darken((0.3, 0.3, 0.3, 1.0), 0.5))
            draw_rect(local_x+local_scale/32.0, local_y+local_scale/32.0, (1-1/16.0)*local_scale, (1-1/16.0)*local_scale, (0.3, 0.3, 0.3, 1.0))

        elif self.kind == Entity.ABSTRACTION:

            border = local_scale/16.0
            draw_rect(local_x, local_y, local_scale, border, (0.3, 0.3, 0.3, 1.0))
            draw_rect(local_x, local_y-border+local_scale, local_scale, border, (0.3, 0.3, 0.3, 1.0))
            draw_rect(local_x, local_y, border, local_scale, (0.3, 0.3, 0.3, 1.0))
            draw_rect(local_x-border+local_scale, local_y, border, local_scale, (0.3, 0.3, 0.3, 1.0))

        #Apply tray
        if self.apply_tray_opacity > 0.0:
            draw_rect(local_x+1.0*local_scale, local_y+local_scale/4-local_scale/32.0, (0.5+1/32.0)*local_scale, (0.5+1/16.0)*local_scale, darken(color, 0.5*self.apply_tray_opacity))

        #draw_exp(self.exp, scale_factor*self.scale, (self.x-0.5*self.scale+xoffset)*scale_factor+window.width/2, (self.y-0.5*self.scale+yoffset)*scale_factor+window.height/2)
        for child in self.childs:
            child.draw(scale_factor, xoffset, yoffset)

    def on_mouse_press(self, modifiers):

        global drag_entity
        
        if self == hover_entity:

            if modifiers & pyglet.window.key.MOD_SHIFT:
                new_entity = Entity(kind=self.kind, x=self.x, y=self.y, scale=self.scale, var_id=self.var_id)
                entities.append(new_entity)
                vars_by_id[self.var_id].append(new_entity)
                new_entity.drag = True

            else:
                self.drag = True
                drag_entity = self

                if self.parent != None:
                    self.parent.childs.remove(self)
                    self.parent = None

            return True

        else:
            return False

    def move(self, dx, dy):

        self.x += dx
        self.y += dy
        for child in self.childs:
            child.move(dx, dy)

    def scale_around_center(self, factor, x, y):
        self.scale *= factor
        self.x = x+(self.x-x)*factor
        self.y = y+(self.y-y)*factor

        for child in self.childs:
            child.scale_around_center(factor, x, y)

    def on_mouse_drag(self, dx, dy):

        global drag_entity

        if self.drag:

            if not zooming:
                self.move(dx, dy)

            elif zooming:
                factor = math.exp(0.01* vec2.inner ((dx, dy), (1.0, 0.0)) )
                self.scale_around_center(factor, -xoffset, -yoffset)

        elif self.being_created:

            diff = xoffset - start_drag_x
            if -xoffset <= -start_drag_x:
                self.kind = Entity.VARIABLE
                self.scale = 100/scale_factor
                self.x = -xoffset
                self.y = -yoffset

                opacity = abs(diff/self.scale)

                if opacity >= 1.0:
                    self.opacity = 1.0
                    self.being_created = False
                    self.drag = True
                    drag_entity = self
                else:
                    self.opacity = opacity

            else:
                self.kind = Entity.ABSTRACTION
                self.scale = diff
                self.x = -xoffset+self.scale/2

        else:

            # collision detection
            if drag_entity:
                xdiff = abs(self.x-drag_entity.x)
                ydiff = abs(self.y-drag_entity.y)
                min_diff = (self.scale+drag_entity.scale)/2

                if xdiff < min_diff and ydiff < min_diff:

                    if self.kind == Entity.VARIABLE or drag_entity.kind == Entity.VARIABLE: #is assignment possible
                        if self.colliding == False:
                            self.temp_var_id = drag_entity.var_id
                            self.colliding = True
                            drag_entity.delete_on_release += 1

                            for entity in vars_by_id[self.var_id]:
                                entity.temp_var_id = drag_entity.var_id

                    else:
                        dx = min_diff-xdiff
                        dy = min_diff-ydiff
                        if dx < dy:
                            if self.x > drag_entity.x:
                                self.move(dx, 0)
                            else:
                                self.move(-dx, 0)
                        else:
                            if self.y > drag_entity.y:
                                self.move(0, dy)
                            else:
                                self.move(0, -dy)

                else:

                    if self.colliding == True:
                        self.colliding = False
                        self.temp_var_id = self.var_id
                        drag_entity.delete_on_release -= 1

                        for entity in vars_by_id[self.var_id]:
                            entity.temp_var_id = self.var_id

    def on_mouse_release(self):

        global drag_entity

        if self.drag:
            self.drag = False
            drag_entity = None

            if self.delete_on_release > 0:
                self._del()

            if hover_entity != None:

                #if hover_entity.hover_over == 0 and hover_entity.kind == Entity.VARIABLE and self.kind == Entity.VARIABLE: 

                #    old_id = hover_entity.var_id
                #    new_id = self.var_id

                #    if old_id != new_id:

                #        while len(vars_by_id[old_id]) > 0:
                #            entity = vars_by_id[old_id].pop()
                #            entity.var_id = new_id
                #            vars_by_id[new_id].append(entity)
                #        available_ids.append(old_id)

                #    vars_by_id[self.var_id].remove(self)
                #    entities.remove(self)

                if hover_entity.hover_over == 1:
                    if hover_entity.childs == []:
                        hover_entity.childs.append(self)
                        self.parent = hover_entity

                        new_x = self.parent.x + self.parent.scale*0.75
                        new_y = self.parent.y
                        self.move(new_x-self.x, new_y-self.y)
                        self.scale_around_center((self.parent.scale/2.0)/self.scale, self.x, self.y)

                        #application = Entity(kind=Entity.APPLICATION, x=self.parent.x+0.25*self.parent.scale, y=self.parent.y, scale=self.parent.scale*1.75)
                        #entities.append(application)
                        #application.childs.append(self.parent)


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
            if self.temp_var_id != self.var_id:
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

exp = ("l", ("l", ("a", 1, 2)))
exp = ("l", ("l", ("l", ("l", ("a", ("a", 1, 3), ("a", ("a", 2, 3), 4))))))
#exp = ("l", ("l", ("l", ("a", ("a", ("l", ("l", ("a", 4, ("a", 4, ("a", 4, ("a", 4, ("a", 4, ("a", 4, ("a", 4, 5))))))))), 2), ("a", ("a", 1, 2), 3)))))
#exp = ("l", ("a", ("l", ("a", 1, ("a", 2, 2))), ("l", ("a", 1, ("a", 2, 2)))))
#exp = ("l", ("l", 1))

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

#def draw_exp(exp, scale_factor, xoffset, yoffset, l_index=1):
#
#    if type(exp) == tuple:
#
#        if exp[0] == "l":
#            draw_rect(xoffset, yoffset, 1*scale_factor, 1*scale_factor, colors[l_index%len(colors)])
#            draw_exp(exp[1], scale_factor*0.875, xoffset+scale_factor*0.0625, yoffset+scale_factor*0.0625, l_index+1)
#
#        if exp[0] == "a":
#
#            draw_rect(xoffset, yoffset, 1*scale_factor, 1*scale_factor, darken((0.3, 0.3, 0.3, 1.0), 0.5))
#            draw_rect(xoffset+scale_factor/32.0, yoffset+scale_factor/32.0, (1-1/16.0)*scale_factor, (1-1/16.0)*scale_factor, (0.3, 0.3, 0.3, 1.0))
#
#            draw_exp(exp[1], scale_factor*0.5, xoffset, yoffset+scale_factor*0.25, l_index)
#            draw_exp(exp[2], scale_factor*0.5, xoffset+scale_factor*0.5, yoffset+scale_factor*0.25, l_index)
#
#    elif type(exp) == int:
#
#        draw_rect(xoffset, yoffset, 1*scale_factor, 1*scale_factor, darken(colors[exp%len(colors)], 0.5))
#        draw_rect(xoffset+scale_factor/32.0, yoffset+scale_factor/32.0, (1-1/16.0)*scale_factor, (1-1/16.0)*scale_factor, colors[exp%len(colors)])

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
entities.append(Entity(kind=Entity.VARIABLE, x=0, y=0, scale=0.5, var_id=0))
hover_entity = None
drag_entity = None

available_ids = [0, 1, 2, 3, 4]
vars_by_id = []
for i in range(len(available_ids)):
    vars_by_id.append([])
vars_by_id[0].append(entities[-1])

crosshair = pyglet.graphics.vertex_list(4,
        ('v2i', (window.width//2, window.height//2+10, window.width//2, window.height//2-10, window.width//2+10, window.height//2, window.width//2-10, window.height//2)),
        ('c4f', (0.8, 0.8, 0.8, 0.8)*4)
        )

base_gradient = pyglet.image.load("gradient.png")

fpsclock = pyglet.clock.ClockDisplay()

def check_hover():

    global hover_entity

    hover_entity = None
    for entity in entities:
        if not entity.is_ancestor(of=hover_entity) and not entity.drag and not entity.being_created:
            hover_over = -1
            if -xoffset > entity.x-0.5*entity.scale and -yoffset > entity.y-0.5*entity.scale and -xoffset < entity.x+0.5*entity.scale and -yoffset < entity.y+0.5*entity.scale and entity.drag == False:
                hover_over = 0

            elif -xoffset > entity.x+0.5*entity.scale and -yoffset > entity.y-0.25*entity.scale and -xoffset < entity.x+1.0*entity.scale and -yoffset < entity.y+0.25*entity.scale:
                hover_over = 1

            if hover_over >= 0:
                hover_entity = entity
                hover_entity.hover_over = hover_over




@window.event
def on_draw():

    window.clear()

    #draw_exp(exp, scale_factor, xoffset*scale_factor/400.0+window.width/2, yoffset*scale_factor/400.0+window.height/2)
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

    start_drag_x, start_drag_y = xoffset, yoffset
    lock_position = False

    handled = False
    for entity in entities:
        handled |= entity.on_mouse_press(modifiers)

    if not handled:
        try:
            new_id = available_ids.pop()
        except IndexError:
            raise(BaseException, ("Too many vars. Also, I do not like python exception handling."))

        new_entity = Entity(kind=Entity.VARIABLE, x=-xoffset, y=-yoffset, scale=0, var_id=new_id)
        entities.append(new_entity)
        vars_by_id[new_id].append(new_entity)
        new_entity.being_created = True

    check_hover()

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):

    global xoffset, yoffset

    if not zooming:
        dx /= mouse_sensitivity
        dy /= mouse_sensitivity
        xoffset -= dx
        yoffset -= dy

    if pyglet.window.mouse.LEFT & buttons or pyglet.window.mouse.RIGHT & buttons:

        for entity in entities:
            entity.on_mouse_drag(dx, dy)

    check_hover()


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
