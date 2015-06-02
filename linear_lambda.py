import pyglet
import math

window = pyglet.window.Window(1024, 768)
window.set_exclusive_mouse(True)

colors = (
        (0.149, 0.078, 0.757, 1.0),
        (0.545, 0.024, 0.729, 1.0),
        (0.929, 0.988, 0.0, 1.0),
        (1.0, 0.78, 0.0, 1.0)
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

fpsclock = pyglet.clock.ClockDisplay()

@window.event
def on_draw():

    window.clear()

    draw_exp(exp, scale_factor, xoffset*scale_factor/400.0+window.width/2, yoffset*scale_factor/400.0+window.height/2)

    fpsclock.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    
    global xoffset, yoffset
    xoffset -= dx
    yoffset -= dy

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):

    global scale_factor
    scale_factor *= math.exp(scroll_y/10.0)

pyglet.app.run()
