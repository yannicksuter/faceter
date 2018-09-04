#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model import Model
import MtxMath
from euclid import euclid
import numpy as np
import svg
import Exporter

def calc_pathes_bbox(paths):
    bbox = paths[0]._bbox
    for path in paths:
        bbox.combine(path._bbox)
    return bbox

if __name__ == "__main__":
    label = '726'
    model = Model()

    vertices = [euclid.Point3(128.36, -3.32, -13.75), euclid.Point3(129.77, 91.40, -13.75), euclid.Point3(103.81, 61.64, -13.75)]
    target_path = svg.Path.from_shape(svg.Shape([np.array([v[0], v[1]]) for v in vertices]))

    # render label into path
    glyph = svg.Path.read(f'./example/svg/0123.svg', flip_y=True)
    label_path = svg.Path.combine([(glyph[int(c)], np.array([1., 0.])) for c in label])

    label_path.triangulate(merge_to_model=model)
    target_path.triangulate(merge_to_model=model)

    Exporter.write(model, f'./export/test_label.obj')