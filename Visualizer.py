import logging

import pyglet
from pyglet.gl import *

# colors
black = (0, 0, 0, 1)
dark_gray = (.75, .75, .75, 1)

class Scene:
    def __init__(self, x=0, y=0, z=0, color=dark_gray):
        # translation and rotation values
        self.x, self.y, self.z = x, y, z
        self.rx = self.ry = self.rz = 0

        # color of the model
        self.color = color

        # models
        self.models = []

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

class Window(pyglet.window.Window):
    def __init__(self, width, height, caption, resizable=False):
        pyglet.window.Window.__init__(self, width=width, height=height, caption=caption, resizable=resizable)

        # sets the background color
        gl.glClearColor(*black)
        self.wireframe = False

        # define scene
        self.scene = Scene(z=-3.5)

        @self.event
        def on_resize(width, height):
            # sets the viewport
            gl.glViewport(0, 0, width, height)

            # sets the projection
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            glu.gluPerspective(60.0, width / float(height), 0.1, 100.0)

            # sets the scene view
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            return pyglet.event.EVENT_HANDLED

        @self.event
        def on_draw():
            # clears the screen with the background color
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            if self.wireframe:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

            # draws the current scene
            self.scene.draw()

        @self.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.W:
                self.wireframe = not self.wireframe

        @self.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            # scroll the MOUSE WHEEL to zoom
            self.scene.z -= scroll_y / 10.0

        @self.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            # press the LEFT MOUSE BUTTON to rotate
            if button == pyglet.window.mouse.LEFT:
                self.scene.ry += dx / 2.0
                self.scene.rx -= dy / 2.0

            # press the LEFT and RIGHT MOUSE BUTTONS simultaneously to pan
            if pyglet.window.mouse.RIGHT:
                self.scene.x += dx / 100.0
                self.scene.y += dy / 100.0

def show(model):
    window = Window(width=1024, height=768, caption='Faceter (Preview)', resizable=False)
    window.scene.models += model
    pyglet.app.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: %s file.obj" % sys.argv[0])
    else:

        show(model)