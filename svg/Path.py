#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import numpy as np
import math
from enum import Enum
import itertools

from model import *
import Exporter
import VecMath as vm

class BoundingBox:
    def __init__(self):
        self._min = np.array([0., 0.])
        self._max = np.array([0., 0.])

    @classmethod
    def from_vertices(cls, vertices):
        cls = BoundingBox()
        cls._min = vertices[0].copy()
        cls._max = vertices[0].copy()
        for vertex in vertices:
            cls._min[0] = min(cls._min[0], vertex[0])
            cls._min[1] = min(cls._min[1], vertex[1])
            cls._max[0] = max(cls._max[0], vertex[0])
            cls._max[1] = max(cls._max[1], vertex[1])
        return cls

    @classmethod
    def from_other(cls, other):
        cls = BoundingBox()
        cls._min = other._min.copy()
        cls._max = other._max.copy()
        return cls

    def is_inside(self, other):
        """Check if bounding box is inside the other bounding box."""
        if isinstance(other, BoundingBox):
          if all(m_s >= m_o for m_s,m_o in zip(self._min, other._min)) and all(m_s <= m_o for m_s,m_o in zip(self._max, other._max)):
              return True
        return False

    def expand(self, w, h):
        self._min[0] -= w
        self._min[1] -= h
        self._max[0] += w
        self._max[1] += h
        return self

    def combine(self, other):
        if isinstance(other, BoundingBox):
            self._min = np.minimum(self._min, other._min)
            self._max = np.maximum(self._max, other._max)

    @property
    def _size(self):
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

    def get_identical_vertices(self, other):
        res = [(u, v) for u, v in list(itertools.product(range(len(self._vertices)), range(len(other._vertices)))) if vm.equal(self._vertices[u], other._vertices[v])]
        return res

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
    def __init__(self):
        self._shapes = []
        self._id = None

    @classmethod
    def from_description(cls, description):
        """Parse path element from a SVG<1.1 file. (https://www.w3.org/TR/SVG/paths.html#PathData)"""
        cls = Path()

        if 'id' in description:
            cls._id = description['id']

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
                    cur_pos = cls.__read_vec(token[token_idx+1])
                else:
                    cur_pos += cls.__read_vec(token[token_idx+1])
                cur_shape = [cur_pos.copy()]
                token_idx += 2
            elif cur_token[0:1] == 'z' or cur_token[0:1] == 'Z':
                # closepath
                if vm.equal(cur_shape[-1], cur_shape[0]):
                    cur_shape = cur_shape[:-1]
                # it is possible that a shape can have twisted/shared vertices (like an 8)
                for shape in cls.split_twisted_shape(cur_shape):
                    cls._shapes.append(Shape(shape))
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
                v = cls.__read_vec(token[token_idx])
                if absolute_mode:
                    cur_pos = v
                else:
                    cur_pos += v
                cur_shape.append(cur_pos.copy())
                token_idx += 1
        return cls

    @classmethod
    def from_shape(cls, shape):
        cls = Path()
        cls._shapes.append(shape)
        return cls

    def split_twisted_shape(self, vertices):
        """Walk multi split paths and return separated shapes"""
        vcount = len(vertices)
        shared_vertices = {i: i for i in range(vcount)}
        for idx1, vertex1 in enumerate(vertices):
            for idx2, vertex2 in enumerate(vertices):
                if idx1 != idx2 and vm.equal(vertex1, vertex2):
                    shared_vertices[idx1] = idx2
                    break

        splits = []
        id_queue = [x for x in range(vcount)]
        while id_queue:
            shape = []
            cur_id = id_queue[0]
            while id_queue:
                id_queue.remove(cur_id)
                shape.append(cur_id)
                cur_id = (shared_vertices[cur_id]+1)%vcount
                # test if loop is closed -> define new shape
                if cur_id == shape[0]:
                    splits.append([vertices[i] for i in shape])
                    break
        return splits

    def __read_vec(self, token):
        return np.array([t(s) for t, s in zip((float, float), token.split(','))])

    def get_sublist_cycled(self, list, start, end):
        # print(f'{start} -> {end}')
        # print(f'{[i%len(list) for i in range(start+len(list), end+1+len(list))]}')
        start = start
        end = end if end > start else end + len(list)
        return [list[i%len(list)] for i in range(start, end)]

    def __merge_overlapping_shapes(self, outer, inner, shared_vertices):
        new_shapes = []
        for idx, start_io in enumerate(shared_vertices):
            end_io = shared_vertices[(idx+1)%len(shared_vertices)]

            # print(f'{start_io[0]} -> {end_io[0]}({end_io[1]}) -> {start_io[1]}({start_io[0]})')
            vertices = self.get_sublist_cycled(inner._vertices, start_io[0], end_io[0])
            vertices += self.get_sublist_cycled(outer._vertices, end_io[1], start_io[1])

            new_shapes.append(Shape(vertices))

        return new_shapes

    def split_shapes(self):
        queue = self._shapes.copy()
        groups = {shape: [] for shape in self._shapes}

        while queue:
            outer = queue[0]
            for inner in self._shapes:
                if outer != inner:
                    shared_vertices = inner.get_identical_vertices(outer)
                    if inner.is_inside(outer, exclude=[u for u, v in shared_vertices]):
                        if len(shared_vertices) > 1:
                            new_outer_shapes = self.__merge_overlapping_shapes(outer, inner, shared_vertices)
                            #add new shapes to queue for inner/outer testing
                            queue += new_outer_shapes
                            #add new shapes as outer shapes (default)
                            for no_shape in new_outer_shapes:
                                groups[no_shape] = []
                            # dissolve outer shape
                            if outer in groups:
                                # if outer shaper had already inner shapes, add them to queue to revalidate befor deleting group
                                queue += [inner for inner, shared_vertices in groups[outer]]
                                del groups[outer]
                            # dissolve inner shape
                            if inner in groups:
                                del groups[inner]
                            # update queue
                            try:
                                queue.remove(inner)
                            except ValueError:
                                pass  # do nothing!
                        else:
                            groups[outer].append((inner, shared_vertices))
                            if inner in groups:
                                del groups[inner]
            try:
                queue.remove(outer)
            except ValueError:
                pass  # do nothing!

        return groups

    def triangulate(self):
        res = []
        for outer, inner in self.split_shapes().items():
            # inner shape must be counter clockwise oriented
            if outer._orientation != ShapeOrientation.ORIENTATION_CCW:
                outer.reverse()
            vertices = list(outer._vertices)
            for shape, shared_vertices in inner:
                #inner shape must be clockwise oriented
                if shape._orientation != ShapeOrientation.ORIENTATION_CW:
                    shape.reverse()

                if shared_vertices:
                    if len(shared_vertices) > 1:
                        raise RuntimeError("More than 1 shared vertex is not allowed.")
                    #if there one shared vertice, use it as a bridge
                    inner_idx, outer_idx = shared_vertices[0]
                else:
                    #find max-x vertice in inner_shape
                    inner_idx = int(np.array(shape._vertices).argmax(axis=0)[0])
                    inner_v = shape._vertices[inner_idx]
                    #find the closest outer-vertice on the right side
                    outer_idx = min([(vm.len(inner_v-v), idx) for idx, v in enumerate(vertices) if v[0] >= inner_v[0]], key=lambda x:x[0])[1]

                #insert inner shape and bridges
                for i in range(len(shape._vertices)):
                    vertices.insert(outer_idx+i+1, shape._vertices[(inner_idx+i)%len(shape._vertices)])
                vertices.insert(outer_idx+len(shape._vertices)+1, shape._vertices[inner_idx])
                if not shared_vertices:
                    #if shared vertices are used, inner and outer point to bridge are the same
                    vertices.insert(outer_idx+len(shape._vertices)+2, vertices[outer_idx])

            res.append((Shape(vertices).triangulate(), outer, inner))
        return res

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
                        _paths.append(Path.from_description(elem.attrib))
                    except Exception as e:
                        print(f'Error loading shape: {e}')
            print(f'{len(_paths)} elements read from {filename}')
        except:
            print(f'Error while reading {filename}')
        return _paths

    @property
    def _bbox(self):
        """ Get bounding box """
        bb = BoundingBox.from_other(self._shapes[0]._bbox)
        for shape in self._shapes:
            bb.combine(shape._bbox)
        return bb

    def _size(self):
        """ Get size of bounding box """
        bbox = self._bbox
        return np.absolute(bbox[1] - bbox[0])

    def embed(self, other, tag=None):
        if isinstance(other, list):
            return self.triangulate()[0][0]

if __name__ == "__main__":
    # filename = '0123'
    # filename = 'yannick'
    filename = 'yannick2'
    # filename = 'test'
    paths = Path.read(f'./example/svg/{filename}.svg')
    # paths = Path.read(f'./example/svg/yannick.svg')
    # paths = Path.read(f'./example/svg/yannick2.svg')
    # paths = Path.read(f'./example/svg/test.svg')

    combined_model = Model()
    for path in paths:
        print(f'triangulating path={path._id} shapes={len(path._shapes)}')
        path_models = path.triangulate()
        for m in path_models:
            combined_model.merge(m[0])

    combined_model.flip(axis_y=True)

    Exporter.write(combined_model, f'./export/_{filename}.obj')
