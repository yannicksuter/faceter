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

    cylinder = primitives.Cylinder(logo_bbox._radius, -15., center=euclid.Vector3(logo_bbox._center[0], logo_bbox._center[1], 0.))
    cylinder_model = cylinder.triangulate(64)

    path, transform = PathUtility.get_path_from_faces(cylinder_model.get_faces_by_tag('top'))
    embedded_model = path.embed([logo_path[0].triangulate()], group_name='svg')
    embedded_model.transform(transform.inverse())
    embedded_model.extrude(15., faces=embedded_model.get_group('svg')._faces)

    # replace top face with logo
    cylinder_model.remove_face(cylinder_model.get_faces_by_tag('top'))
    cylinder_model.merge(embedded_model)
    # cylinder_model.get_group('svg')._material._diffuse = [1., 0., 0.]

    ObjExporter.write(cylinder_model, f'./export/_logo_badge.obj')
