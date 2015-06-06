import pyglet
import math
import vec2
import gfx

class Entity:

    VARIABLE = 0
    APPLICATION = 1
    #ABSTRACTION = 2

    def __init__(self, kind, x, y, scale=1, var_id=None):

        self.x = x
        self.y = y
        self.scale = scale
        self.hover = False
        self.drag = False

        self.kind = kind

        self.childs = []

        self.var_id = var_id

    def draw(self, scale_factor, xoffset, yoffset):

        local_x = (self.x-0.5*self.scale+xoffset)*scale_factor+window.width/2
        local_y = (self.y-0.5*self.scale+yoffset)*scale_factor+window.height/2
        local_scale = scale_factor*self.scale

        if self.kind == Entity.VARIABLE:

            #draw box
            draw_rect(local_x, local_y, local_scale, local_scale, darken(colors[self.var_id]))
            draw_rect(local_x+local_scale/32.0, local_y+local_scale/32.0, (1-1/16.0)*local_scale, (1-1/16.0)*local_scale, colors[self.var_id])

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

            draw_rect(x, y, 1*local_scale, 1*local_scale, darken((0.3, 0.3, 0.3, 1.0)))
            draw_rect(x+local_scale/32.0, y+local_scale/32.0, (1-1/16.0)*local_scale, (1-1/16.0)*local_scale, (0.3, 0.3, 0.3, 1.0))

        for child in self.childs:
            child.draw()

        #draw_exp(self.exp, scale_factor*self.scale, (self.x-0.5*self.scale+xoffset)*scale_factor+window.width/2, (self.y-0.5*self.scale+yoffset)*scale_factor+window.height/2)

    def on_mouse_motion(self, x_offset, y_offset):

        if -x_offset > self.x-0.5*self.scale and -y_offset > self.y-0.5*self.scale and -x_offset < self.x+0.5*self.scale and -y_offset < self.y+0.5*self.scale and self.drag == False:
            self.hover = True
        else:
            self.hover = False

        return self.hover

    def on_mouse_press(self, button):
        
        if self.hover:

            if button == pyglet.window.mouse.LEFT:
                self.drag = True

            elif button == pyglet.window.mouse.RIGHT:
                new_entity = Entity(kind=self.kind, x=self.x, y=self.y, scale=self.scale, var_id=self.var_id)
                entities.append(new_entity)
                vars_by_id[self.var_id].append(new_entity)
                new_entity.drag = True

            return True

        else:
            return False

    def on_mouse_drag(self, dx, dy):

        if self.drag:
            self.x += dx
            self.y += dy

        else:
            if -xoffset > self.x-0.5*self.scale and -yoffset > self.y-0.5*self.scale and -xoffset < self.x+0.5*self.scale and -yoffset < self.y+0.5*self.scale:
                self.hover = True
            else:
                self.hover = False

    def on_mouse_scroll(self, factor):

        if self.drag:
            self.scale /= factor
            self.x = -xoffset+(xoffset+self.x)/factor #modify the coordinates so that the difference between crosshair and coordinates stays constant over transformation (else scaling would occur at the center, and the shrinking entity would seem to move away from the cursor, while actually staying rooted in its original position)
            self.y = -yoffset+(yoffset+self.y)/factor

    def on_mouse_release(self):

        if self.drag:
            self.drag = False
            old_id = None
            for entity in entities:
                if entity.hover == True:
                    old_id = entity.var_id
                    break

            if old_id != self.var_id and old_id != None:
                vars_by_id[self.var_id].remove(self)
                entities.remove(self)
                while len(vars_by_id[old_id]) > 0:
                    entity = vars_by_id[old_id].pop()
                    entity.var_id = self.var_id
                    vars_by_id[self.var_id].append(entity)

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

def darken(color):
    return (color[0]*0.5, color[1]*0.5, color[2]*0.5, color[3])

def draw_line(start, end, thickness, color):

    endpoint_offset = vec2.norm(vec2.sub(start, end))
    endpoint_offset[0], endpoint_offset[1] = -endpoint_offset[1], endpoint_offset[0] #rotate 90 degrees
    endpoint_offset = vec2.mul(endpoint_offset, thickness/2)

    pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES, [0, 1, 2, 0, 2, 3],
            ('v2i', (int(start[0]+endpoint_offset[0]), int(start[1]+endpoint_offset[1]), int(end[0]+endpoint_offset[0]), int(end[1]+endpoint_offset[1]), int(end[0]-endpoint_offset[0]), int(end[1]-endpoint_offset[1]), int(start[0]-endpoint_offset[0]), int(start[1]-endpoint_offset[1]))),
            ('c4f', color*4)
            )

def draw_exp(exp, scale_factor, xoffset, yoffset, l_index=1):

    if type(exp) == tuple:

        if exp[0] == "l":
            draw_rect(xoffset, yoffset, 1*scale_factor, 1*scale_factor, colors[l_index%len(colors)])
            draw_exp(exp[1], scale_factor*0.875, xoffset+scale_factor*0.0625, yoffset+scale_factor*0.0625, l_index+1)

        if exp[0] == "a":

            draw_rect(xoffset, yoffset, 1*scale_factor, 1*scale_factor, darken((0.3, 0.3, 0.3, 1.0)))
            draw_rect(xoffset+scale_factor/32.0, yoffset+scale_factor/32.0, (1-1/16.0)*scale_factor, (1-1/16.0)*scale_factor, (0.3, 0.3, 0.3, 1.0))

            draw_exp(exp[1], scale_factor*0.5, xoffset, yoffset+scale_factor*0.25, l_index)
            draw_exp(exp[2], scale_factor*0.5, xoffset+scale_factor*0.5, yoffset+scale_factor*0.25, l_index)

    elif type(exp) == int:

        draw_rect(xoffset, yoffset, 1*scale_factor, 1*scale_factor, darken(colors[exp%len(colors)]))
        draw_rect(xoffset+scale_factor/32.0, yoffset+scale_factor/32.0, (1-1/16.0)*scale_factor, (1-1/16.0)*scale_factor, colors[exp%len(colors)])

scale_factor = 400.0
xoffset = 0.0
yoffset = 0.0
mouse_sensitivity = 400.0

entities = []
#entities.append(Entity(exp, 0, 0))
entities.append(Entity(kind=Entity.VARIABLE, x=0, y=0, scale=0.5, var_id=0))

available_ids = [0, 1, 2, 3, 4, 0, 0]

vars_by_id = []
for i in range(len(available_ids)):
    vars_by_id.append([])
vars_by_id[0].append(entities[-1])

crosshair = pyglet.graphics.vertex_list(4,
        ('v2i', (window.width//2, window.height//2+10, window.width//2, window.height//2-10, window.width//2+10, window.height//2, window.width//2-10, window.height//2)),
        ('c4f', (0.8, 0.8, 0.8, 0.8)*4)
        )

varcounter = 0

base_gradient = pyglet.image.load("gradient.png")

fpsclock = pyglet.clock.ClockDisplay()

def check_hover():

    hover_taken = False
    for i in range(len(entities)-1, -1, -1):
        entity = entities[i]
        if hover_taken:
            entity.hover = False
        else:
            if entity.on_mouse_motion(xoffset, yoffset) == True:
                hover_taken = True

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
    xoffset -= dx/mouse_sensitivity
    yoffset -= dy/mouse_sensitivity

    check_hover()

@window.event
def on_mouse_press(x, y, button, modifiers):

    if button == pyglet.window.mouse.LEFT:
        for entity in entities:
            entity.on_mouse_press(button)
    
    elif button == pyglet.window.mouse.RIGHT:

        handled = False
        for entity in entities:
            handled = entity.on_mouse_press(button)
            if handled:
                break

        if not handled:
            try:
                new_id = available_ids.pop()
            except IndexError:
                raise(BaseException, ("Too many vars. Also, I do not like python exception handling."))

            new_entity = Entity(kind=Entity.VARIABLE, x=-xoffset, y=-yoffset, scale=0, var_id=new_id)
            entities.append(new_entity)
            vars_by_id[new_id].append(new_entity)

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):

    global xoffset, yoffset
    dx /= mouse_sensitivity
    dy /= mouse_sensitivity
    xoffset -= dx
    yoffset -= dy

    if pyglet.window.mouse.LEFT & buttons:
        for entity in entities:
            entity.on_mouse_drag(dx, dy)

    elif pyglet.window.mouse.RIGHT & buttons:
        diff = entities[-1].y + yoffset
        entities[-1].scale += diff
        entities[-1].scale = abs(entities[-1].scale)
        entities[-1].y = -yoffset

    check_hover()


@window.event
def on_mouse_release(x, y, button, modifiers):

    if button == pyglet.window.mouse.LEFT:
        for entity in entities:
            entity.on_mouse_release()

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):

    global scale_factor
    scale_factor *= math.exp(scroll_y/10.0)

    for entity in entities:
        entity.on_mouse_scroll(math.exp(scroll_y/10.0))

pyglet.app.run()
