#!/usr/bin/env python
# -*- coding: utf-8 -*-

import primitives
import svg
import PathUtility
import ObjExporter
from euclid import euclid

if __name__ == "__main__":
    filename = 'logo_tamedia_black'
    logo_path = svg.Path.read(f'./example/svg/{filename}.svg', flip_y=True)
    logo_bbox = PathUtility.get_bbox_for_path(logo_path)

    cylinder = primitives.Cylinder(logo_bbox._size[0], -10., center=euclid.Vector3(logo_bbox._center[0], logo_bbox._center[1], 0.))
    cylinder_model = cylinder.triangulate(32)

    path, transform = PathUtility.get_path_from_faces(cylinder_model.get_faces_by_tag('top'))

    ObjExporter.write(cylinder_model, f'./export/_logo_badge.obj')
