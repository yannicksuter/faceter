#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import numpy as np
import math

from Plane import Plane
from Model import Model
from Exporter import Exporter
from VecMath import VecMath as vm

class BoundingBox:
    def __init__(self, vertices):
        self._min = vertices[0].copy()
        self._max = vertices[0].copy()
        for vertex in vertices:
            self._min[0] = min(self._min[0], vertex[0])
            self._min[1] = min(self._min[1], vertex[1])
            self._max[0] = max(self._max[0], vertex[0])
            self._max[1] = max(self._max[1], vertex[1])

    def is_inside(self, other):
        """Check if bounding box is inside the other bounding box."""
        if isinstance(other, BoundingBox):
          if all(m_s >= m_o for m_s,m_o in zip(self._min, other._min)) and all(m_s <= m_o for m_s,m_o in zip(self._max, other._max)):
              return True
        return False

    def get_size(self):
        """Get size of bounding box."""
        return np.absolute(self._max - self._min)

def angle(v1, v2):
    angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
    if angle < 0.:
        angle += (2. * math.pi)
    return angle

class Shape:
    def __init__(self, vertices):
        self._vertices = vertices.copy()
        self._edges = [Segment2D(i, (i+1)%len(vertices), v, vertices[(i+1)%len(vertices)]) for i,v in enumerate(vertices)]
        self._angles = [angle(self._vertices[(i+1)%len(self._vertices)]-v, self._vertices[(i-1)%len(self._vertices)]-v) for i, v in enumerate(self._vertices)]
        self._bbox = BoundingBox(self._vertices)
        self._norm = vm.unit_vector(np.cross(self._vertices[-1] - self._vertices[0], self._vertices[1] - self._vertices[0])) * -1.

    def is_inside(self, other):
        if isinstance(other, Shape):
            return self._bbox.is_inside(other._bbox)
        return False

    def triangulate(self):
        """Triangulate shape using ear clipping algorithm."""
        model = Model()
        v_list = [np.array([v[0], v[1], 0.]) for v in self._vertices]
        while len(v_list) > 3:
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

    def to_string(self):
        return f'vertices: {len(self._vertices)} bbox: {self._bbox._min}/{self._bbox._max}'

# def line(p1, p2):
#     A = (p1[1] - p2[1])
#     B = (p2[0] - p1[0])
#     C = (p1[0]*p2[1] - p2[0]*p1[1])
#     return A, B, -C

class Segment2D:
    def __init__(self, idx0, idx1, v0, v1):
        self._idx0 = idx0
        self._v0= v0
        self._idx1 = idx1
        self._v1= v1
        A = (v0[1] - v1[1])
        B = (v1[0] - v0[0])
        C = (v0[0] * v1[1] - v1[0] * v0[1])
        self._line = A, B, -C

    @classmethod
    def ray(cls, p, dir):
        return cls(None, None, p, p+dir)

    def intersect_line(self, other):
        D = self._line[0] * other._line[1] - self._line[1] * other._line[0]
        Dx = self._line[2] * other._line[1] - self._line[1] * other._line[2]
        Dy = self._line[0] * other._line[2] - self._line[2] * other._line[0]
        if D != 0:
            x = Dx / D
            y = Dy / D
            return x, y
        else:
            return False

    def intersect_segment(self, other):
        #todo: implement
        return self.intersect_line(other)

class Path:
    def __init__(self, description):
        """Parse path element from a SVG<1.1 file. (https://www.w3.org/TR/SVG/paths.html#PathData)"""
        self._shapes = []
        _cur_pos = None
        for token in description['d'].split(' '):
            if token[0:1] == 'm':
                # moveto
                _cur_line = []
            elif token[0:1] == 'z':
                # closepath
                self._shapes.append(Shape(_cur_line[:-1]))
            else:
                vec = np.array([t(s) for t, s in zip((float, float), token.split(','))])
                if _cur_pos is not None:
                    _cur_pos += vec
                else:
                    _cur_pos = vec
                _cur_line.append(_cur_pos.copy())

    def triangulate(self):
        outer_shapes = [shape for shape in self._shapes if shape._norm == 1.0]
        inner_shapes = [shape for shape in self._shapes if shape._norm == -1.0]

        if inner_shapes:
            model = Model()
            for shape in inner_shapes:
                #find max-x vertice in inner_shape
                x_indices = int(np.array(shape._vertices).argmax(axis=0)[0])
                #find outer segment that intersects ray
                ray = Segment2D.ray(shape._vertices[x_indices], np.array([1, 0]))
                for s in outer_shapes[0]._edges:
                    t=s.intersect(ray)
            return model
        else:
            return [shape.triangulate() for shape in outer_shapes]

    @staticmethod
    def read(filename):
        _paths = []
        try:
            tree = ET.parse(filename)
            for elem in tree.iter():
                #only 1.1 support yet
                if elem.tag.endswith('svg'):
                    if 'version' in elem.attrib and float(elem.attrib['version']) > 1.1:
                        print('Only SVG <= 1.1 supported.')
                        return
                #read path elements
                if elem.tag.endswith('path'):
                    try:
                        _paths.append(Path(elem.attrib))
                    except:
                        pass
            print(f'{len(_paths)} elements read from {filename}.')
        except:
            print(f'Error while reading {filename}.')
        return _paths

if __name__ == "__main__":
    paths = Path.read(f'./example/svg/0123.svg')
    for idx, p in enumerate(paths):
        path_model = p.triangulate()

        for s in p._shapes:
            print(f'{idx}: {s._norm}')
        shape_model = p._shapes[-1].triangulate()

        Exporter.translate(shape_model, -shape_model.get_center())  # center object
        Exporter.write_obj(shape_model, f'./export/_svg{idx}.obj')
