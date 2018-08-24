#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svg
import Exporter
import model

if __name__ == "__main__":
    paths = svg.Path.read(f'./example/svg/0123.svg')

    label = '726'
    label_path = svg.Path.combine([(paths[int(c)], (0., 0.)) for c in label])

    combined_model = model.Model()
    for path in label_path:
        print(f'triangulating path={path._id} shapes={len(path._shapes)}')
        for m in path.triangulate():
            combined_model.merge(m[0])

    combined_model.flip(axis_y=True)

    Exporter.write(combined_model, f'./export/combined_{label}.obj')