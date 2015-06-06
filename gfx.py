import pyglet
import vec2

def draw_textured_aa_line (start, end, thickness, tex):

    if start != end and thickness != 0 and tex != None:
        endpoint_offset = vec2.norm(vec2.sub(start, end))
        endpoint_offset[0], endpoint_offset[1] = -endpoint_offset[1], endpoint_offset[0] #rotate 90 degrees
        endpoint_offset = vec2.mul(endpoint_offset, thickness/2)

        pyglet.gl.glEnable(tex.target)
        pyglet.gl.glBindTexture(tex.target, tex.id)

        pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES, [0, 1, 2, 0, 2, 3],
                ('v2i', (int(start[0]+endpoint_offset[0]), int(start[1]+endpoint_offset[1]), int(end[0]+endpoint_offset[0]), int(end[1]+endpoint_offset[1]), int(end[0]-endpoint_offset[0]), int(end[1]-endpoint_offset[1]), int(start[0]-endpoint_offset[0]), int(start[1]-endpoint_offset[1]))),
                ('t3f', tex.tex_coords)
                )

        pyglet.gl.glDisable(tex.target)

