#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ObjLoader, math
from Shell import *
from Exporter import Exporter
from Model import Model
from Facet import Facet

if __name__ == "__main__":
    obj_name = 'abstract'

    obj_data = ObjLoader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=1.)

    print(f'Faces: {len(obj_model._faces)}')
    print(f'Vertices: {len(obj_model._vertices)}')
    bbox_size = obj_model.get_size()
    print(f'Boundingbox: [{bbox_size[0]}, {bbox_size[1]}, {bbox_size[2]}]')

    target_lid_size = 120. #mm^2

    faceted_model = Model()
    for face_id in range(len(obj_model._faces)):
        ref_face = obj_model._faces[face_id]
        print(f'processing facet #{face_id}')

        # calculate scale factor to get a constant lid size
        face_surface = ref_face.get_area()
        ttop_size = (target_lid_size / math.sqrt(face_surface)) / 10

        facet = Facet(ref_face, obj_model, brick_height=15., top_height=25., top_size=ttop_size)
        thickness = [2.] * len(facet._faces)
        visibility = [True] * len(obj_model._faces)

        thickness[0] = .2  # bottom face is 'transparent'
        visibility[1] = False  # top face is removed
        facet = generate_shell(facet, thickness)

        # add facet to overview
        faceted_model.merge_model(facet)

        # export single part
        facet = Exporter.rotate_model(facet, obj_model._faces[face_id]._norm)
        facet._update()
        Exporter.write_obj(facet, f'./export/_{obj_name}_part_{face_id+1}.obj')

    Exporter.write_obj(faceted_model, f'./export/_{obj_name}_faceted.obj')
