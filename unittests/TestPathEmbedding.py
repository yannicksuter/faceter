#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import svg
import ObjExporter
import PathUtility


if __name__ == "__main__":
    # filename = '0123'
    filename = 'test'
    paths = svg.Path.read(f'./example/svg/{filename}.svg')

    bbox = PathUtility.get_bbox_for_path(paths).expand(10, 10)
    target_path = svg.Path.from_shape(svg.Shape([np.array([bbox._min[0], bbox._min[1]]),
                   np.array([bbox._max[0], bbox._min[1]]),
                   np.array([bbox._max[0], bbox._max[1]]),
                   np.array([bbox._min[0], bbox._max[1]]),
                  ]))

    embedded_model = target_path.embed([path.triangulate() for path in paths], group_name='svg')
    embedded_model.flip(axis_y=True)

    embedded_model.get_group('svg')._material._diffuse = [1., 0., 0.]
    embedded_model.extrude(5., faces=embedded_model.get_group('svg')._faces)

    ObjExporter.write(embedded_model, f'./export/embedded_{filename}.obj')