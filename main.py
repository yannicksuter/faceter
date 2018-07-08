#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ObjLoader, math
from Shell import *
from Exporter import Exporter
from Model import Model
from Facet import Facet

def export_centered(model, filename, orientation_vec=None):
    model._update()
    Exporter.translate(model, -model.get_center()) # center object
    if orientation_vec is not None:
        Exporter.rotate_model(model, orientation_vec) # rotate for optimal printing
    model._update()
    Exporter.write_obj(model, filename)

if __name__ == "__main__":
    obj_name = 'abstract'

    obj_data = ObjLoader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=1.)

    print(f'Faces: {len(obj_model._faces)}')
    print(f'Vertices: {len(obj_model._vertices)}')
    bbox_size = obj_model.get_size()
    print(f'Boundingbox: [{bbox_size[0]}, {bbox_size[1]}, {bbox_size[2]}]')

    target_lid_size = 100. #mm^2

    faceted_model = Model()
    for face_id, face in enumerate(obj_model._faces):
        print(f'processing facet #{face_id}')

        # calculate scale factor to get a constant lid size
        face_surface = face.get_area()
        ttop_size = (target_lid_size / math.sqrt(face_surface)) / 10

        facet = Facet(face, obj_model, brick_height=15., top_height=20., top_size=ttop_size)
        facet.triangulate()
        facet._update()

        thickness = [2.] * len(facet._faces)
        visibility = [True] * len(facet._faces)
        thickness[0] = .2  # bottom face is 'transparent'
        # visibility[1] = False  # top face is removed

        shell = generate_shell(facet, thickness, visibility)
        Exporter.write_obj(facet, f'./export/_{obj_name}_shell_{face_id+1}.obj')
        # export_centered(shell, f'./export/_{obj_name}_shell_{face_id+1}.obj', face._norm)

        # add facet to overview
        faceted_model.merge_model(facet)

        # export single part
        export_centered(facet, f'./export/_{obj_name}_part_{face_id+1}.obj', face._norm)

    Exporter.write_obj(faceted_model, f'./export/_{obj_name}_faceted.obj')
