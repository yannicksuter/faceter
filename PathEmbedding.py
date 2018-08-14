#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from model import *
import svg
import Exporter

if __name__ == "__main__":
    filename = '0123'
    paths = svg.Path.read(f'./example/svg/{filename}.svg')

    min, max = paths._size
    shape = svg.Shape([np.array([min[0], min[1]]),
                   np.array([max[0], min[1]]),
                   np.array([max[0], max[1]]),
                   np.array([min[0], max[1]]),
                  ])

    combined_model = Model()
    for path in paths:
        print(f'triangulating path={path._id} shapes={len(path._shapes)}')
        path_models = path.triangulate()
        for m in path_models:
            combined_model.merge(m[0])
    combined_model.flip(axis_y=True)



    Exporter.write(combined_model, f'./export/_{filename}.obj')