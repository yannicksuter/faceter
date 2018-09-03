#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import ObjLoader, Exporter
from Shell import *
from model import *
from Facet import Facet
import svg
import VecMath
import MtxMath
from euclid import euclid
import numpy as np

def embed_label(model, face, label, glyph):
    transform = MtxMath.conv_to_euclid(VecMath.rotate_fromto_matrix(face._norm, np.array([0., 0., 1.])))
    vertices = [transform * euclid.Point3(v[0], v[1], v[2]) for v in face._vertices]
    target_path = svg.Path.from_shape(svg.Shape([np.array([v[0], v[1]]) for v in vertices]))

    label_path = glyph.combine([(glyph[int(c)], np.array([1., 0.])) for c in label])

    # move/scale label to fit into target triangle
    

    embedded_model = target_path.embed([path.triangulate() for path in label_path], group_name='svg')
    embedded_model.transform(transform.inverse())

    model.remove_face(face)
    model.merge(embedded_model)

if __name__ == "__main__":
    obj_name = 'abstract'

    obj_data = ObjLoader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=1.5)

    print(f'Faces: {len(obj_model._faces)}')
    print(f'Vertices: {len(obj_model._vertices)}')
    bbox_size = obj_model._size
    print(f'Boundingbox: [{bbox_size[0]}, {bbox_size[1]}, {bbox_size[2]}]')

    target_lid_size = 100. #mm^2
    faceted_model = Model()

    for face_id, face in enumerate(obj_model._faces):
        print(f'processing facet #{face_id}')
        face_surface = face._area
        ttop_size = (target_lid_size / math.sqrt(face_surface)) / 10
        facet = Facet(face, obj_model, brick_height=15., top_height=25., top_size=ttop_size)
        faceted_model.merge(facet, group_name=f'facet_{face_id}')

    faceted_model.triangulate()

    shell_model = Model()
    paths_0123 = svg.Path.read(f'./example/svg/0123.svg')

    for idx, group in enumerate(faceted_model._groups):
        # create shell
        model = faceted_model.get_group_model(group)
        thickness = [2.] * len(model._faces)
        visibility = [True] * len(model._faces)
        for face in model.get_faces_by_tag('bottom'):
            thickness[face._id] = .2  # bottom face is 'transparent'
        for face in model.get_faces_by_tag('top'):
            visibility[face._id] = False  # top face is removed
        generate_shell(model, thickness, visibility)

        #add label
        lbl_face = max([(face, face._area) for face in model.get_faces_by_tag('facet_top_layer')], key=lambda item: item[1])[0]
        lbl_group = model.add_group('label')
        lbl_group._material._diffuse = [1., 0., 0.]
        lbl_face._group = lbl_group
        embed_label(model, lbl_face, f'{idx}', paths_0123)

        shell_model.merge(model, group_name=group._name)
        Exporter.write(model, f'./export/_{obj_name}_part_{idx+1}.obj', model._faces[0]._norm)

    Exporter.write(faceted_model, f'./export/_{obj_name}_faceted.obj')
    Exporter.write(shell_model, f'./export/_{obj_name}_shell.obj')
