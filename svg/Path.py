#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import sys
import numpy as np
import VecMath as vm
from euclid import euclid

from svg.Shape import *
from svg.BoundingBox import BoundingBox

from model import *
import Exporter

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
        token = cls.splitDescription(description['d'])
        token_idx = 0
        while token_idx < len(token):
            cur_token = token[token_idx]
            # print(f'{cur_token}')
            if cur_token[0:1] == 'm' or cur_token[0:1] == 'M':
                # moveto: relative/absolute mode
                cur_shape = []
                absolute_mode = False if cur_token[0:1] == 'm' else True
                token_idx += 1
                while True:
                    try:
                        # v = cls.__read_vec(token[token_idx])
                        v = cls.__readVector2D(token, token_idx)
                        if token_idx == 1 or absolute_mode:
                            cur_pos = v
                        else:
                            cur_pos += v
                        token_idx += 2
                        cur_shape.append(cur_pos.copy())
                    except:
                        break
            elif cur_token[0:1] == 'z' or cur_token[0:1] == 'Z':
                # closepath
                if vm.equal(cur_shape[-1], cur_shape[0]):
                    cur_shape = cur_shape[:-1]

                # debug ouput, plot shape
                # for v in cur_shape:
                #     print(f'{cls.__convertVector2D(v)}')

                # it is possible that a shape can have twisted/shared vertices (like an 8)
                for shape in cls.split_twisted_shape(cur_shape):
                    cls._shapes.append(Shape(shape))
                token_idx += 1
            elif cur_token[0:1] == 'l' or cur_token[0:1] == 'L':
                # lineto: relative/absolute mode
                absolute_mode = False if cur_token[0:1] == 'l' else True
                token_idx += 1
                while True:
                    try:
                        # v = cls.__read_vec(token[token_idx])
                        v = cls.__readVector2D(token, token_idx)
                        if token_idx == 1 or absolute_mode:
                            cur_pos = v
                        else:
                            cur_pos += v
                        token_idx += 2
                        cur_shape.append(cur_pos.copy())
                    except:
                        break
            elif cur_token[0:1] == 'h' or cur_token[0:1] == 'H':
                # horizontal lineto: relative/absolute mode
                token_idx += 1
            elif cur_token[0:1] == 'v' or cur_token[0:1] == 'V':
                # vertical lineto: relative/absolute mode
                token_idx += 1
            # cubic Bézier curve commands
            elif cur_token[0:1] == 'c' or cur_token[0:1] == 'C':
                # curveto/bezier: relative/absolute mode
                token_idx += 1
            elif cur_token[0:1] == 's' or cur_token[0:1] == 'S':
                # curveto/bezier: relative/absolute mode
                token_idx += 1
            # quadratic Bézier curve commands
            elif cur_token[0:1] == 'q' or cur_token[0:1] == 'Q':
                # quadratic bezier: relative/absolute mode
                absolute_mode = False if cur_token[0:1] == 'q' else True
                token_idx += 1
                while True:
                    try:
                        # read control and endpoint
                        # cp = cls.__read_vec(token[token_idx])
                        cp = cls.__readVector2D(token, token_idx)
                        ep = cls.__readVector2D(token, token_idx+2)

                        # ep =  cls.__read_vec(token[token_idx+1])
                        if absolute_mode:
                            cur_shape.extend(cls.__interpolateQuadratic(cls.__convertVector2D(cur_pos), cls.__convertVector2D(cp), cls.__convertVector2D(ep)))
                            cur_pos = ep
                        else:
                            cur_shape.extend(cls.__interpolateQuadratic(cls.__convertVector2D(cur_pos), cls.__convertVector2D(cp+cur_pos), cls.__convertVector2D(ep+cur_pos), step=0.1))
                            cur_pos += ep
                        token_idx += 4
                    except:
                        break
            elif cur_token[0:1] == 't' or cur_token[0:1] == 'T':
                # smooth quadratic bezier: relative/absolute mode
                token_idx += 1
            else:
                raise RuntimeError(f'Error parsing SVG path id={cls._id}, unexpected token={cur_token}')
        return cls

    @classmethod
    def from_shape(cls, shape):
        cls = Path()
        cls._shapes.append(shape)
        return cls

    def merge(self, path):
        for s in path._shapes:
            self._shapes.append(s)

    def clone(self):
        cls = Path()
        cls._id = self._id
        for shape in self._shapes:
            cls._shapes.append(shape.clone())
        return cls

    def translate(self, v, apply=True):
        """Translate path by vector v"""
        mtx = euclid.Matrix3().translate(v[0], v[1])
        if apply:
            return self.__transform(mtx)
        return mtx

    def rotate(self, angle, anchor=(0., 0.), apply=True):
        """Rotate path by angle (in radian) around anchor."""
        mtx = euclid.Matrix3().translate(anchor[0], anchor[1]).rotate(angle).translate(-anchor[0], -anchor[1])
        if apply:
            return self.__transform(mtx)
        return mtx

    def scale(self, scale_x=1., scale_y=1., apply=True):
        """Scale path by factor x and y"""
        mtx = euclid.Matrix3().scale(scale_x, scale_y)
        if apply:
            return self.__transform(mtx)
        return mtx

    def flip(self, flip_x, flip_y):
        center = self._bbox._center.copy()
        for shape in self._shapes:
            shape.flip(center, flip_x, flip_y)
        return self

    def __transform(self, mtx):
        for shape in self._shapes:
            shape.transform(mtx)
        return self

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

    def splitDescription(self, path_description):
        ext_description = ''
        for c in path_description:
            prev_c = ext_description[-1:]
            if c.isalpha():
                if prev_c != ' ' and len(prev_c) != 0:
                    ext_description += f' '
                ext_description += f'{c} '
            elif c == '-':
                if prev_c != ' ' and len(prev_c) != 0:
                    ext_description += f' '
                ext_description += f'{c}'
            elif c == ',' or c == ' ':
                if prev_c != ' ' and len(prev_c) != 0:
                    ext_description += f' '
            else:
                ext_description += c
        return ext_description.strip().split(' ')

    def __read_vec(self, token):
        return np.array([t(s) for t, s in zip((float, float), token.split(','))])

    def __readVector2D(self, tokens, cur_index):
        return np.array([float(tokens[cur_index]), float(tokens[cur_index+1])])

    def __convertVector2D(self, v):
        return euclid.Vector2(v[0], v[1])

    def __interpolateQuadratic(self, start, cntrl_point, end, step=.1):
        spline = []
        d1 = cntrl_point-start
        d2 = end-cntrl_point
        for t in np.arange(step, 1., step):
            p1 = start+t*d1
            p2 = cntrl_point+t*d2
            bp = p1+t*(p2-p1)
            spline.append(np.array([bp.x, bp.y]))
        spline.append(end.copy())
        return spline

    def get_sublist_cycled(self, list, start, end):
        start = start
        end = end if end > start else end + len(list)
        return [list[i%len(list)] for i in range(start, end)]

    def __merge_overlapping_shapes(self, outer, inner, shared_vertices):
        new_shapes = []
        for idx, start_io in enumerate(shared_vertices):
            end_io = shared_vertices[(idx+1)%len(shared_vertices)]

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

    def __find_min_vert_dist(self, outer_list, inner_list):
        """ Find the vertice pair with smallest distance """
        min_dist = sys.float_info.max
        out_idx, in_idx = None, None
        for v_out_idx, v_out in enumerate(outer_list):
            for v_in_idx, v_in in enumerate(inner_list):
                dist = vm.dist_point_to_point(v_out, v_in)
                if dist < min_dist:
                    min_dist = dist
                    out_idx = v_out_idx
                    in_idx = v_in_idx
        return out_idx, in_idx

    def triangulate(self, z=0., merge_to_model=None):
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
                    outer_idx, inner_idx = self.__find_min_vert_dist(vertices, shape._vertices)

                #insert inner shape and bridges
                for i in range(len(shape._vertices)):
                    vertices.insert(outer_idx+i+1, shape._vertices[(inner_idx+i)%len(shape._vertices)])
                vertices.insert(outer_idx+len(shape._vertices)+1, shape._vertices[inner_idx])
                if not shared_vertices:
                    #if shared vertices are used, inner and outer point to bridge are the same
                    vertices.insert(outer_idx+len(shape._vertices)+2, vertices[outer_idx])

            res.append((Shape(vertices).triangulate(z), outer, inner))

        # optional: merge results into target model
        if merge_to_model != None:
            for entry in res:
                merge_to_model.merge(entry[0])

        return res

    @staticmethod
    def read(filename, flip_x=False, flip_y=False):
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
                        _paths.append(Path.from_description(elem.attrib).flip(flip_x, flip_y))
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

    def embed(self, other, group_name=None, z=0.):
        """ Embeds a triangulated construct defined by other (list of tuples, result from path triangulation). """
        if isinstance(other, list):
            consolidated_model = Model()
            for path in other:
                for model, outer, inner_list in path:
                    # 1) add triangulated path itself
                    consolidated_model.merge(model, group_name=group_name)
                    # 2) add outer shapes as inner (reserve!)
                    self._shapes.append(outer.clone().reverse())
                    # 3) add inner shapes as triangulated objects by themself
                    for inner_shape in inner_list:
                        consolidated_model.merge(inner_shape[0].clone().reverse().triangulate(z), group_name='shape')
            # 4) triangulate outer shape
            path_models = self.triangulate(z)
            for m in path_models:
                consolidated_model.merge(m[0], group_name='shape')
            return consolidated_model

        return False

    @staticmethod
    def combine(paths):
        res = Path()
        pos = np.array([0., 0.])
        for p in paths:
            path = p[0].clone().translate(pos - p[0]._bbox._min)
            path.scale(1., 2.)
            # path = path.rotate(math.pi/4, anchor=(path._bbox._min[0], path._bbox._min[1]))
            res.merge(path)
            pos += (p[1] + np.array([path._bbox._size[0], 0.]))
        return res

if __name__ == "__main__":
    # filename = '0123'
    # filename = 'yannick'
    # filename = 'yannick2'
    filename = 'test'
    paths = Path.read(f'./example/svg/{filename}.svg')
    # paths = Path.read(f'./example/svg/yannick.svg')
    # paths = Path.read(f'./example/svg/yannick2.svg')
    # paths = Path.read(f'./example/svg/test.svg')

    combined_model = Model()
    for path in paths:
        print(f'triangulating path={path._id} shapes={len(path._shapes)}')
        path.triangulate(merge_to_model=combined_model)
        # path_models = path.triangulate()
        # for m in path_models:
        #     combined_model.merge(m[0])

    combined_model.flip(axis_y=True)

    Exporter.write(combined_model, f'./export/_{filename}.obj')
