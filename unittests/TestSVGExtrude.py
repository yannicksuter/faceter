#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svg
import ObjExporter
from model import Model

if __name__ == "__main__":
    # filename = 'y'
    filename = 'logo_tamedia_black'
    paths = svg.Path.read(f'./example/svg/{filename}.svg', flip_y=True)

    combined_model = Model()
    for path in paths:
        print(f'triangulating path={path._id} shapes={len(path._shapes)}')
        combined_model.merge(path.extrude(10.))

    ObjExporter.write(combined_model, f'./export/_{filename}_extruded.obj')
