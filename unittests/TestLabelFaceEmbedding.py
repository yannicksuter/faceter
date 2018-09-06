#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model import Model
import MtxMath
from euclid import euclid
import numpy as np
import svg
import Exporter

def fit_rect_in_triangle(tri_vertice, side, rectangle):
    """ http://mathcountsnotes.blogspot.com/2013/05/the-largest-rectangle-inscribed-in-any.html """
    position = euclid.Point2(0., 0.)
    scaling = euclid.Point2(1., 1.)
    rotation = 0

    side = euclid.Line2(euclid.Point2(tri_vertice[0].x, tri_vertice[0].y), euclid.Point2(tri_vertice[1].x, tri_vertice[1].y))
    height = side.distance(euclid.Point2(tri_vertice[2].x, tri_vertice[2].y))

    # Largest inscribing rectangle
    a = euclid.LineSegment2(side).length * 0.5
    b = height * 0.5

    return position, scaling, rotation

if __name__ == "__main__":
    label = '726'
    model = Model()

    vertices = [euclid.Point3(128.36, -3.32, -13.75), euclid.Point3(129.77, 91.40, -13.75), euclid.Point3(103.81, 61.64, -13.75)]
    target_path = svg.Path.from_shape(svg.Shape([np.array([v[0], v[1]]) for v in vertices]))

    # render label into path
    glyph = svg.Path.read(f'./example/svg/0123.svg', flip_y=True)
    label_path = svg.Path.combine([(glyph[int(c)], np.array([1., 0.])) for c in label])
    fit_rect_in_triangle(vertices, 0, label_path._bbox)

    label_path.triangulate(merge_to_model=model)
    target_path.triangulate(merge_to_model=model)

    Exporter.write(model, f'./export/test_label.obj')