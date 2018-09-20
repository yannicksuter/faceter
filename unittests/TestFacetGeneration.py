#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model import Model
import ObjExporter
import math

if __name__ == "__main__":
    import ObjReader

    obj_name = 'abstract'

    obj_data = ObjReader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=1.)
    obj_model.simplify()

    print(f'Faces: {len(obj_model._faces)}')
    print(f'Vertices: {len(obj_model._vertices)}')
    bbox_size = obj_model._size
    print(f'Boundingbox: [{bbox_size[0]}, {bbox_size[1]}, {bbox_size[2]}]')

    ObjExporter.write(obj_model, f'./export/_{obj_name}.obj')

    target_lid_size = 100.  # mm^2

    faceted_model = Model()
    for face_id in range(len(obj_model._faces)):
        ref_face = obj_model._faces[face_id]
        print(f'processing facet #{face_id}')

        # calculate scale factor to get a constant lid size
        face_surface = ref_face._area
        ttop_size = (target_lid_size / math.sqrt(face_surface)) / 10

        facet = Facet(ref_face, obj_model, brick_height=10., top_height=15., top_size=ttop_size)
        faceted_model.merge(facet)

        # export single part
        ObjExporter.write(facet, f'./export/_{obj_name}_part_{face_id+1}.obj', obj_model._faces[face_id]._norm)

    # faceted_model.triangulate()
    ObjExporter.write(faceted_model, f'./export/_{obj_name}_faceted.obj')
