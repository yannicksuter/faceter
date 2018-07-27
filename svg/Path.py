#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import numpy as np

from Plane import Plane

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

class Shape:
    def __init__(self, vertices):
        self._vertices = vertices.copy()
        self._bbox = BoundingBox(self._vertices)
        self._tt = True

    def is_inside(self, other):
        if isinstance(other, Shape):
            return self._bbox.is_inside(other._bbox)
        return False

    def tostring(self):
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

# def v3(v):
#     return np.array([v[0], v[1], 0.])

if __name__ == "__main__":
    paths = Path.read(f'../example/svg/0123.svg')
    for idx, p in enumerate(paths):
        print(f'{idx}: {len(p._shapes)}')
        if len(p._shapes) > 1:
            print(p._shapes[0].is_inside(p._shapes[-1]))
        # for s in p._shapes:
        #     cp = Plane.from_points(v3(s._vertices[0]), v3(s._vertices[1]), v3(s._vertices[2]))
        #     print(f'{len(s._vertices)} {cp._norm}')