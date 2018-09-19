#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svg
import Exporter
from model import Model

if __name__ == "__main__":
    filename = '0123'
    paths = svg.Path.read(f'./example/svg/{filename}.svg', flip_y=True)

    combined_model = Model()
    for path in paths:
        print(f'triangulating path={path._id} shapes={len(path._shapes)}')
        path.triangulate(merge_to_model=combined_model)

    Exporter.write(combined_model, f'./export/_{filename}.obj')
