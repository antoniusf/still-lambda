import pyglet
import math

class Entity:

    def __init__(self, exp, x, y, scale=1):

        self.x = x
        self.y = y
        self.scale = scale
        self.hover = False
        self.drag = False

        self.exp = exp

    def draw(self, scale_factor, xoffset, yoffset):

        draw_exp(self.exp, scale_factor*self.scale, (self.x-0.5*self.scale+xoffset)*scale_factor+window.width/2, (self.y-0.5*self.scale+yoffset)*scale_factor+window.height/2)

    def on_mouse_motion(self, x_offset, y_offset):

        if -x_offset > self.x-0.5*self.scale and -y_offset > self.y-0.5*self.scale and -x_offset < self.x+0.5*self.scale and -y_offset < self.y+0.5*self.scale:
            self.hover = True
        else:
            self.hover = False

    def on_mouse_press(self):
        
        if self.hover:
            self.drag = True

    def on_mouse_drag(self, dx, dy):

        if self.drag:
            self.x += dx
            self.y += dy

    def on_mouse_scroll(self, factor):

        if self.drag:
            self.scale /= factor
            self.x = -xoffset+(xoffset+self.x)/factor #modify the coordinates so that the difference between crosshair and coordinates stays constant over transformation (else scaling would occur at the center, and the shrinking entity would seem to move away from the cursor, while actually staying rooted in its original position)
            self.y = -yoffset+(yoffset+self.y)/factor

    def on_mouse_release(self):

        if self.drag:
            self.drag = False

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
entities.append(Entity(exp, 0, 0))
entities.append(Entity(0, 1, 0, 0.5))

crosshair = pyglet.graphics.vertex_list(4,
        ('v2i', (window.width//2, window.height//2+10, window.width//2, window.height//2-10, window.width//2+10, window.height//2, window.width//2-10, window.height//2)),
        ('c4f', (0.8, 0.8, 0.8, 0.8)*4)
        )

fpsclock = pyglet.clock.ClockDisplay()

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

    for entity in entities:
        entity.on_mouse_motion(xoffset, yoffset)

@window.event
def on_mouse_press(x, y, button, modifiers):

    if button == pyglet.window.mouse.LEFT:
        for entity in entities:
            entity.on_mouse_press()
    
    elif button == pyglet.window.mouse.RIGHT:
        entities.append(Entity(exp=0, x=-xoffset, y=-yoffset, scale=0))

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
