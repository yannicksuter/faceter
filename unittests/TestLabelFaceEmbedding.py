#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model import Model
import MtxMath
from euclid import euclid
import numpy as np
import svg
import Exporter
import math

def angle(v1, v2):
    angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
    if angle < 0.:
        angle += (2. * math.pi)
    return angle

def fit_rect_in_triangle(tri_vertice, side_idx, rectangle):
    """ http://mathcountsnotes.blogspot.com/2013/05/the-largest-rectangle-inscribed-in-any.html """

    side = euclid.Line2(euclid.Point2(tri_vertice[side_idx%3].x, tri_vertice[side_idx%3].y), euclid.Point2(tri_vertice[(side_idx+1)%3].x, tri_vertice[(side_idx+1)%3].y))
    height = side.distance(euclid.Point2(tri_vertice[(side_idx+2)%3].x, tri_vertice[(side_idx+2)%3].y))

    # Largest inscribing rectangle
    a = euclid.LineSegment2(side).length * 0.5
    b = height * 0.5

    position = side.p + side.v*.5
    rotation = angle(euclid.Vector2(side.v[1], side.v[0]), euclid.Vector2(0., rectangle._size[1]))
    scaling = euclid.Point2(0.1, 0.1)
    # scaling = euclid.Point2(a/rectangle._size[0], b/rectangle._size[1])

    return position, scaling, rotation

if __name__ == "__main__":
    label = '726'
    model = Model()

    vertices = [euclid.Point3(128.36, -3.32, -13.75), euclid.Point3(129.77, 91.40, -13.75), euclid.Point3(103.81, 61.64, -13.75)]
    target_path = svg.Path.from_shape(svg.Shape([np.array([v[0], v[1]]) for v in vertices]))

    # render label into path
    glyph = svg.Path.read(f'./example/svg/0123.svg', flip_y=True)
    label_path = svg.Path.combine([(glyph[int(c)], np.array([1., 0.])) for c in label])
    p, s, r = fit_rect_in_triangle(vertices, 0, label_path._bbox)

    # a = angle(euclid.Vector2(0, 1), euclid.Vector2(0, -2.))
    # print(a)

    label_path.scale(s[0], s[1])
    pivot = label_path._bbox._center+np.array([0, label_path._bbox._size[1]*-.5])
    label_path.rotate(r, anchor=pivot)
    label_path.translate(p-pivot)

    label_path.triangulate(merge_to_model=model)
    target_path.triangulate(merge_to_model=model)

    Exporter.write(model, f'./export/test_label.obj')