# colors
from pyglet.gl import gl

dark_gray = (.75, .75, .75, 1)

class Model:

    def __init__(self, x=0, y=0, z=0, color=dark_gray):
        # translation and rotation values
        self.x, self.y, self.z = x, y, z
        self.rx = self.ry = self.rz = 0

        # color of the model
        self.color = color

        # facets
        self.facets = []

    def clear(self):
        self.facets = self.facets[:]

    def draw(self):
        gl.glLoadIdentity()
        gl.glTranslatef(self.x, self.y, self.z)
        gl.glRotatef(self.rx, 1, 0, 0)
        gl.glRotatef(self.ry, 0, 1, 0)
        gl.glRotatef(self.rz, 0, 0, 1)

        # sets the color
        gl.glColor4f(*self.color)

        for facet in self.facets:
            facet.draw()
