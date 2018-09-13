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

def rotation_angle(v1, v2):
    angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
    if angle < 0.:
        angle += (2. * math.pi)
    return angle

def fit_rect_in_triangle(tri_vertice, side_idx, rectangle):
    """ http://mathcountsnotes.blogspot.com/2013/05/the-largest-rectangle-inscribed-in-any.html """
    A = euclid.Point2(tri_vertice[side_idx%3+0].x, tri_vertice[side_idx%3+0].y)
    B = euclid.Point2(tri_vertice[side_idx%3+1].x, tri_vertice[side_idx%3+1].y)
    C = euclid.Point2(tri_vertice[side_idx%3+2].x, tri_vertice[side_idx%3+2].y)
    side = euclid.Line2(A, B)
    height = side.distance(C)

    # Largest inscribing rectangle
    a = euclid.LineSegment2(side).length * 0.5
    b = height * 0.5
    n = euclid.Vector2(side.v[1], side.v[0]).normalized()

    position = side.p + side.v*.5
    dir = (C - position).normalized()
    position = position + dir

    rotation = rotation_angle(n, euclid.Vector2(0., rectangle._size[1]))
    scaling = euclid.Point2(0.1, 0.1)

    return position, scaling, rotation

def embed_label(model, face, side, label, glyph):
    # transform face to shape (into which we will embed the label)
    transform = MtxMath.conv_to_euclid(VecMath.rotate_fromto_matrix(face._norm, np.array([0., 0., 1.])))
    vertices = [transform * euclid.Point3(v[0], v[1], v[2]) for v in face._vertices]
    target_path = svg.Path.from_shape(svg.Shape([np.array([v[0], v[1]]) for v in vertices]))

    # render label into path
    label_path = svg.Path.combine([(glyph[int(c)], np.array([1., 0.])) for c in label])

    # move/scale label to fit into target triangle
    p, s, r = fit_rect_in_triangle(vertices, side, label_path._bbox)
    label_path.scale(s[0], s[1])
    pivot = label_path._bbox._center+np.array([0, label_path._bbox._size[1]*-.5])
    label_path.rotate(r, anchor=pivot)
    label_path.translate(p-pivot)

    # embed the label
    embedded_model = target_path.embed([label_path.triangulate(z=vertices[0].z)], group_name='svg', z=vertices[0].z)
    embedded_model.transform(transform.inverse())

    # (optional) extrude the label
    embedded_model.get_group('svg')._material._diffuse = [1., 0., 0.]
    embedded_model.extrude(1., faces=embedded_model.get_group('svg')._faces)

    # replace initial face with new 'labeled face'
    model.remove_face(face)
    model.merge(embedded_model)

    return embedded_model

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

    facets = []
    for face_id, face in enumerate(obj_model._faces):
        print(f'processing facet #{face_id}')
        face_surface = face._area
        ttop_size = (target_lid_size / math.sqrt(face_surface)) / 10
        facet = Facet(face, obj_model, brick_height=15., top_height=25., top_size=ttop_size)
        facets.append((face, facet))
        faceted_model.merge(facet, group_name=f'facet_{face_id}')

    # LUT: merge edge labels
    labels = {}
    for facet in facets:
        labels = {**labels, **facet[1]._top_side_labels}
    # for label, key in enumerate(labels):
    #     print(f'{label} -> {key} = {labels[key][0]} - {labels[key][1]}')

    faceted_model.triangulate()

    shell_model = Model()
    paths_0123 = svg.Path.read(f'./example/svg/0123.svg', flip_y=True)

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
        lbl_group = model.add_group('label')
        lbl_group._material._diffuse = [1., 0., 0.]
        for lbl_face in model.get_faces_by_tag('facet_top_layer'):
            for side_idx, edge in enumerate(lbl_face._edges):
                for label, key in enumerate(labels):
                    if edge.is_equal(labels[key]):
                        print(f'obj#{idx+1} adding label=\'{label}\' to side={side_idx}')
                        embedded_model = embed_label(model, lbl_face, side_idx, f'{label}', paths_0123)
                        # Exporter.write(embedded_model, f'./export/_{obj_name}_part_{idx+1}_embedded.obj', embedded_model._faces[0]._norm)

        shell_model.merge(model, group_name=group._name)
        Exporter.write(model, f'./export/_{obj_name}_part_{idx+1}.obj', model._faces[0]._norm)

    # Exporter.write(faceted_model, f'./export/_{obj_name}_faceted.obj')
    Exporter.write(shell_model, f'./export/_{obj_name}_shell.obj')
