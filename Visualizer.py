import os

import pyglet
from pyglet.gl import gl
from pyglet.gl import glu

from Model import Model
from Facet import Facet

# colors
black = (0, 0, 0, 1)

class Window(pyglet.window.Window):
    def __init__(self, width, height, caption, resizable=False):
        pyglet.window.Window.__init__(self, width=width, height=height, caption=caption, resizable=resizable)

        # sets the background color
        gl.glClearColor(*black)
        self.wireframe = False

        # define model
        self.model = Model(z=-3.5)

        @self.event
        def on_resize(width, height):
            # sets the viewport
            gl.glViewport(0, 0, width, height)

            # sets the projection
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            glu.gluPerspective(60.0, width / float(height), 0.1, 100.0)

            # sets the model view
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

            # draws the current model
            self.model.draw()

        @self.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.W:
                self.wireframe = not self.wireframe

        @self.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            # scroll the MOUSE WHEEL to zoom
            self.model.z -= scroll_y / 10.0

        @self.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            # press the LEFT MOUSE BUTTON to rotate
            if button == pyglet.window.mouse.LEFT:
                self.model.ry += dx / 2.0
                self.model.rx -= dy / 2.0

            # press the LEFT and RIGHT MOUSE BUTTONS simultaneously to pan
            if pyglet.window.mouse.RIGHT:
                self.model.x += dx / 100.0
                self.model.y += dy / 100.0

    # def show(self):

def show(facets):
    window = Window(width=1024, height=768, caption='Faceter (Preview)', resizable=False)
    window.model.facets += facets
    pyglet.app.run()
