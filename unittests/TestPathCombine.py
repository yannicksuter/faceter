#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svg
import ObjExporter
import model
import numpy as np

if __name__ == "__main__":
    paths = svg.Path.read(f'./example/svg/0123.svg')

    label = '726'
    label_path = svg.Path.combine([(paths[int(c)], np.array([1., 0.])) for c in label])

    combined_model = model.Model()
    for m in label_path.triangulate():
        combined_model.merge(m[0])

    combined_model.flip(axis_y=True)

    ObjExporter.write(combined_model, f'./export/combined_{label}.obj')