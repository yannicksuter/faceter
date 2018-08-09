import logging

# from pyglet.gl import *
# from pyglet import image, resource, graphics

import ObjLoader
import model

import ctypes, math
import pyglet
from pyglet.gl import *

from euclid import euclid


# colors
black = (0, 0, 0, 1)
grey = (.25, .25, .25, 1)
dark_gray = (.75, .75, .75, 1)

class Material(pyglet.graphics.Group):
    # diffuse = [.8, .8, .8]
    diffuse = [1., .0, .0]
    # ambient = [.2, .2, .2]
    ambient = [.5, .0, .0]
    specular = [0., 0., 0.]
    emission = [0., 0., 0.]
    shininess = 0.
    opacity = 1.
    texture = None

    def __init__(self, name, **kwargs):
        self.name = name
        super(Material, self).__init__(**kwargs)

    def set_state(self, face=GL_FRONT_AND_BACK):
        if self.texture:
            glEnable(self.texture.target)
            glBindTexture(self.texture.target, self.texture.id)
        else:
            glDisable(GL_TEXTURE_2D)

        glMaterialfv(face, GL_DIFFUSE,
            (GLfloat * 4)(*(self.diffuse + [self.opacity])))
        glMaterialfv(face, GL_AMBIENT,
            (GLfloat * 4)(*(self.ambient + [self.opacity])))
        glMaterialfv(face, GL_SPECULAR,
            (GLfloat * 4)(*(self.specular + [self.opacity])))
        glMaterialfv(face, GL_EMISSION,
            (GLfloat * 4)(*(self.emission + [self.opacity])))
        glMaterialf(face, GL_SHININESS, self.shininess)

    def unset_state(self):
        if self.texture:
            glDisable(self.texture.target)
        glDisable(GL_COLOR_MATERIAL)

    def __eq__(self, other):
        if self.texture is None:
            return super(Material, self).__eq__(other)
        return (self.__class__ is other.__class__ and
                self.texture.id == other.texture.id and
                self.texture.target == other.texture.target and
                self.parent == other.parent)

    def __hash__(self):
        if self.texture is None:
            return super(Material, self).__hash__()
        return hash((self.texture.id, self.texture.target))

class Scene:
    def __init__(self, x=0, y=0, z=0, color=dark_gray):
        # translation and rotation values
        self.x, self.y, self.z = x, y, z
        self.rx = self.ry = self.rz = 0

        # color of the model
        self.color = color

        self._transforms = euclid.Matrix4.new_identity()
        self._batch = pyglet.graphics.Batch()

    def load_identity(self):
        '''Discard any transformation'''
        self._transforms.identity()
        self.normalize = False

    def translate(self, x, y, z):
        self._transforms.translate(x, y, z)

    def rotate(self, angle, x, y, z):
        self._transforms.rotate_axis(math.pi*angle/180.0, euclid.Vector3(x, y, z))

    def scale(self, x, y, z):
        self._transforms.scale(x, y, z)
        self.normalize = True

    def add_model(self, model):
        center = model._center
        self.translate(-center[0], -center[1], -center[2])
        for group in model._groups:
            vertices = []
            normals = []
            for face in group._faces:
                for tv in face._vertices:
                    v = self._transforms * euclid.Point3(tv[0], tv[1], tv[2])
                    vertices.extend(v[:])
                    n = self._transforms * euclid.Point3(face._norm[0], face._norm[1], face._norm[2]).normalized()
                    normals.extend(n[:])

            material = Material(group._material._name)
            material.diffuse = group._material._diffuse
            self._batch.add(len(vertices) // 3,
                      GL_TRIANGLES,
                      material,
                      ('v3f/static', tuple(vertices)),
                      ('n3f/static', tuple(normals)),
                      )

    def draw(self):
        gl.glLoadIdentity()
        gl.glTranslatef(self.x, self.y, self.z)
        gl.glRotatef(self.rx, 1, 0, 0)
        gl.glRotatef(self.ry, 0, 1, 0)
        gl.glRotatef(self.rz, 0, 0, 1)
        self._batch.draw()

class Window(pyglet.window.Window):
    def __init__(self, width, height, caption, resizable=False, retina=False):
        pyglet.window.Window.__init__(self, width=width, height=height, caption=caption, resizable=resizable)

        # sets the background color
        gl.glClearColor(*grey)
        fourfv = ctypes.c_float * 4
        glLightfv(GL_LIGHT0, GL_POSITION, fourfv(0, 200, 5000, 1))
        glLightfv(GL_LIGHT0, GL_AMBIENT, fourfv(0.0, 0.0, 0.0, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, fourfv(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, fourfv(1.0, 1.0, 1.0, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        self.wireframe = False
        self._retina = retina

        # define scene
        self.scene = Scene(z=-30)

        @self.event
        def on_resize(width, height):
            # sets the viewport
            if self._retina:
                gl.glViewport(0, 0, width*2, height*2)
            else:
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
            self.clear()
            glLoadIdentity()
            gluLookAt(0, 0, 30, 0, 0, 0, 0, 1, 0)

            if self.wireframe:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
                glDisable(GL_LIGHTING)
            else:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                glEnable(GL_LIGHTING)

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

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     logging.error("Usage: %s file.obj" % sys.argv[0])
    # else:
    filename = 'cube'
    obj_data = ObjLoader.ObjLoader(f'./example/{filename}.obj')
    obj_model = model.Model.load_fromdata(obj_data, scale=10)
    obj_model.simplify()

    obj_model._groups[0]._material._diffuse = [1., 0., 0.]
    obj_model.extrude(5., faces=obj_model._faces)

    window = Window(width=1024, height=768, caption='Faceter (Preview)', resizable=False, retina=False)
    obj_model.triangulate()
    window.scene.add_model(obj_model)
    pyglet.app.run()
