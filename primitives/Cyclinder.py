import model
import math
from euclid import euclid

class Cylinder:
    def __init__(self, radius, height, center=euclid.Vector3(0.,0.,0.)):
        self._center = euclid.Vector3(center[0], center[1], center[2])
        self._radius = radius
        self._height = height

    def triangulate(self, sides):
        cylinder_model = model.Model()
        angle_f = 2.*math.pi / float(sides)
        base_verts = [euclid.Vector3(math.cos(angle_f*i)*self._radius, math.sin(angle_f*i)*self._radius, 0.) + self._center for i in range(0,sides)]
        top_verts = [euclid.Vector3(0,0,self._height) + v for v in base_verts]

        if self._height > 0:
            cylinder_model.add_face(top_verts, tags=['top'])
            cylinder_model.add_face(list(reversed(base_verts)), tags=['bottom'])
            for i in range(0, sides):
                cylinder_model.add_face([base_verts[i], base_verts[(i+1)%sides], top_verts[(i+1)%sides], top_verts[i]], tags=['side'])
        else:
            cylinder_model.add_face(base_verts, tags=['top'])
            cylinder_model.add_face(list(reversed(top_verts)), tags=['bottom'])
            for i in range(0, sides):
                cylinder_model.add_face([top_verts[i], top_verts[(i+1)%sides], base_verts[(i+1)%sides], base_verts[i]], tags=['side'])

        return cylinder_model