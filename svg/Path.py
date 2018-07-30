#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import numpy as np
import math
from enum import Enum

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

class ShapeOrientation(Enum):
    ORIENTATION_CW = 1
    ORIENTATION_CCW = 2

class Shape:
    def __init__(self, vertices):
        self._vertices = vertices.copy()
        self.__update()

    def reverse(self):
        self._vertices = list(reversed(self._vertices))
        self.__update()

    def __update(self):
        v_count = len(self._vertices)
        self._edges = [Segment2D(i, (i+1)%v_count, v, self._vertices[(i+1)%v_count]) for i,v in enumerate(self._vertices)]
        self._angles = [angle(self._vertices[(i+1)%len(self._vertices)]-v, self._vertices[(i-1)%len(self._vertices)]-v) for i, v in enumerate(self._vertices)]
        self._bbox = BoundingBox(self._vertices)
        def shoelace(v1, v2):
            return (v2[0]-v1[0])*(v2[1]+v1[1])
        self._orientation = ShapeOrientation.ORIENTATION_CW if sum([shoelace(v,self._vertices[(i+1)%v_count] ) for i,v in enumerate(self._vertices)]) > 0. else ShapeOrientation.ORIENTATION_CCW

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
        pt = self.intersect_line(other)
        print(pt)
        if pt:
            return (pt[0] >= self._v0[0] and pt[0] <= self._v1[0])
        return False

class Path:
    def __init__(self, description):
        """Parse path element from a SVG<1.1 file. (https://www.w3.org/TR/SVG/paths.html#PathData)"""
        self._shapes = []
        if 'id' in description:
            self._id = description['id']

        cur_pos = None
        token = description['d'].split(' ')
        token_idx = 0
        while token_idx < len(token):
            cur_token = token[token_idx]
            # print(f'{cur_token}')
            if cur_token[0:1] == 'm' or cur_token[0:1] == 'M':
                # moveto: relative/absolute mode
                absolute_mode = False if cur_token[0:1] == 'm' else True
                if token_idx == 0 or absolute_mode:
                    cur_pos = self.__read_vec(token[token_idx+1])
                else:
                    cur_pos += self.__read_vec(token[token_idx+1])
                cur_shape = [cur_pos.copy()]
                token_idx += 2
            elif cur_token[0:1] == 'z' or cur_token[0:1] == 'Z':
                # closepath
                if vm.equal(cur_shape[-1], cur_shape[0]):
                    cur_shape = cur_shape[:-1]
                self._shapes.append(Shape(cur_shape))
                token_idx += 1
            elif cur_token[0:1] == 'l' or cur_token[0:1] == 'L':
                # lineto: relative/absolute mode
                token_idx += 1
            elif cur_token[0:1] == 'h' or cur_token[0:1] == 'H':
                # horizontal lineto: relative/absolute mode
                token_idx += 1
            elif cur_token[0:1] == 'v' or cur_token[0:1] == 'V':
                # vertical lineto: relative/absolute mode
                token_idx += 1
            else:
                v = self.__read_vec(token[token_idx])
                if absolute_mode:
                    cur_pos = v
                else:
                    cur_pos += v
                cur_shape.append(cur_pos.copy())
                token_idx += 1

    def __read_vec(self, token):
        return np.array([t(s) for t, s in zip((float, float), token.split(','))])

    def triangulate(self):
        outer_shapes = [shape for shape in self._shapes if shape._orientation == ShapeOrientation.ORIENTATION_CCW]
        inner_shapes = [shape for shape in self._shapes if shape._orientation == ShapeOrientation.ORIENTATION_CW]

        if inner_shapes:
            vertices = list(outer_shapes[0]._vertices)
            for shape in inner_shapes:
                #find max-x vertice in inner_shape
                inner_idx = int(np.array(shape._vertices).argmax(axis=0)[0])
                inner_v = shape._vertices[inner_idx]

                #find the closest outer-vertice on the right side
                outer_idx = min([(vm.len(inner_v-v), idx) for idx, v in enumerate(vertices) if v[0] >= inner_v[0]], key=lambda x:x[0])[1]

                #insert inner shape and bridges
                for i in range(len(shape._vertices)):
                    vertices.insert(outer_idx+i+1, shape._vertices[(inner_idx+i)%len(shape._vertices)])
                vertices.insert(outer_idx+len(shape._vertices)+1, shape._vertices[inner_idx])
                vertices.insert(outer_idx+len(shape._vertices)+2, vertices[outer_idx])

            return Shape(vertices).triangulate()
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
            print(f'{len(_paths)} elements read from {filename}')
        except:
            print(f'Error while reading {filename}')
        return _paths

if __name__ == "__main__":
    # paths = Path.read(f'./example/svg/0123.svg')
    # paths = Path.read(f'./example/svg/yannick.svg')
    # paths = Path.read(f'./example/svg/yannick2.svg')
    paths = Path.read(f'./example/svg/test.svg')

    path_model = paths[0].triangulate()
    Exporter.translate(path_model, -path_model.get_center())  # center object
    Exporter.write_obj(path_model, f'./export/__svg{8}.obj')

    for idx, p in enumerate(paths):
        for s in p._shapes:
            print(f'path {idx}: orientation={s._orientation} vertices:{len(s._vertices)}')
    #     shape_model = p._shapes[-1].triangulate()
    # Exporter.translate(shape_model, -shape_model.get_center())  # center object
    # Exporter.write_obj(shape_model, f'./export/_svg{idx}.obj')

    # path_model = paths[0].triangulate()
    # Exporter.translate(path_model, -path_model.get_center())  # center object
    # Exporter.write_obj(path_model, f'./export/_test.obj')
