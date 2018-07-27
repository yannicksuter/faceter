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
    # return np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

class Shape:
    def __init__(self, vertices):
        self._vertices = vertices.copy()
        self._bbox = BoundingBox(self._vertices)
        self._tt = True

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
                # ang2 = vm.angle_between(v1 - v, v0 - v)
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
        shape_model = p._shapes[-1].triangulate()

        Exporter.translate(shape_model, -shape_model.get_center())  # center object
        Exporter.write_obj(shape_model, f'./export/_svg{idx}.obj')
