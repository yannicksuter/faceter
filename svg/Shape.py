import numpy as np
import math
from enum import Enum
import itertools

from model import *
import VecMath as vm

from svg.BoundingBox import BoundingBox

def angle(v1, v2):
    angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
    if angle < 0.:
        angle += (2. * math.pi)
    return angle

class ShapeOrientation(Enum):
    ORIENTATION_CW = 1
    ORIENTATION_CCW = 2

class Shape:
    def __init__(self, vertices):
        self._vertices = vertices.copy()
        self.__update()

    def move(self, v):
        for i, vertex in enumerate(self._vertices):
            self._vertices[i] = vertex+v

    def reverse(self):
        self._vertices = list(reversed(self._vertices))
        self.__update()
        return self

    def clone(self):
        return Shape(self._vertices)

    def __update(self):
        v_count = len(self._vertices)
        self._angles = [angle(self._vertices[(i+1)%len(self._vertices)]-v, self._vertices[(i-1)%len(self._vertices)]-v) for i, v in enumerate(self._vertices)]
        self._bbox = BoundingBox.from_vertices(self._vertices)
        def shoelace(v1, v2):
            return (v2[0]-v1[0])*(v2[1]+v1[1])
        self._orientation = ShapeOrientation.ORIENTATION_CW if sum([shoelace(v,self._vertices[(i+1)%v_count] ) for i,v in enumerate(self._vertices)]) > 0. else ShapeOrientation.ORIENTATION_CCW

    def __ray_tracing(self, x, y, poly):
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def is_inside(self, other, exclude=[]):
        if isinstance(other, Shape) and self != other:
            if self._bbox.is_inside(other._bbox):
                if all(self.__ray_tracing(v[0], v[1], other._vertices) for id, v in enumerate(self._vertices) if id not in exclude):
                    return True
        return False

    def triangulate(self):
        """Triangulate shape using ear clipping algorithm."""
        model = Model()
        v_list = [np.array([v[0], v[1], 0.]) for v in self._vertices]
        v_list_len = len(v_list)
        while v_list_len > 3:
            for i,v in enumerate(v_list):
                # print(f'processing {i}, {v}')
                v0 = v_list[(i-1)%len(v_list)]
                v1 = v_list[(i+1)%len(v_list)]
                ang = angle(v1-v, v0-v)
                #first: find a triangle with a convex corner
                if ang < math.pi:
                    #second: check if no other vertices are inside triangle
                    if not any(not vm.equal(vv,v) and not vm.equal(vv,v0) and not vm.equal(vv,v1) and self.__point_in_triangle(vv, v0, v, v1) for vv in v_list):
                        model.add_face([v0, v, v1])
                        v_list.pop(i)
                        break
            if v_list_len == len(v_list):
                raise RuntimeError('Ear clipping failed to find vertice tripple to triangulate')
            v_list_len = len(v_list)

        model.add_face(v_list)
        model._update()
        return model

    def __sign(self, p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    def __point_in_triangle(self, pt, v1, v2, v3):
        b1 = self.__sign(pt, v1, v2) < 0.0
        b2 = self.__sign(pt, v2, v3) < 0.0
        b3 = self.__sign(pt, v3, v1) < 0.0
        return (b1 == b2) and (b2 == b3)

    def get_identical_vertices(self, other):
        res = [(u, v) for u, v in list(itertools.product(range(len(self._vertices)), range(len(other._vertices)))) if vm.equal(self._vertices[u], other._vertices[v])]
        return res

    def to_string(self):
        return f'vertices: {len(self._vertices)} bbox: {self._bbox._min}/{self._bbox._max}'
