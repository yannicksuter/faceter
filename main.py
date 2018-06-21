#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ObjLoader
import Visualizer
from Facet import Facet

def explode_obj(obj_filename):
    obj_scene = ObjLoader.ObjLoader(obj_filename)

    facet_list = []
    for face in obj_scene.faces:
        if len(face) == 3: #only triangles supported yet
            vertices = []
            vert_normales = []
            for f_id, t_id, n_id in face:
                vertices += obj_scene.vertices[f_id-1]
                vert_normales += obj_scene.normals[n_id-1]
            facet_list.append(Facet(vertices, vert_normales))

    return facet_list

if __name__ == "__main__":
    Visualizer.show(explode_obj('./example/cube.obj'))
