from pyglet.gl import *

class Facet:
    # def __init__(self):
    #     self.vertices = pyglet.graphics.vertex_list(3, ('v3f', [-0.5,-0.5,0.0, 0.5,-0.5,0.0, 0.0,0.5,0.0]))
    #     # self.vertices = pyglet.graphics.vertex_list(3, ('v3f', [-0.5,-0.5,0.0, 0.5,-0.5,0.0, 0.0,0.5,0.0]),
    #     #                                                ('c3B', [100,200,220, 200,110,100, 100,250,100]))
    def __init__(self, vertices, vert_normales):
        num_verts = int(vertices / 3)
        self.vertices = pyglet.graphics.vertex_list(3, ('v3f', vertices))

    def draw(self):
        self.vertices.draw(GL_TRIANGLES)
