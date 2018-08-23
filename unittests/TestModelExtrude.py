#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ObjLoader
import Exporter
from model import Model

if __name__ == "__main__":
    filename = 'cube'
    obj_data = ObjLoader.ObjLoader(f'../example/{filename}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=10)
    obj_model.simplify()

    obj_model._groups[0]._material._diffuse = [1., 0., 0.]
    for face in obj_model._faces.copy():
        obj_model.extrude(5., faces=[face])

    Exporter.write(obj_model, f'../export/_{filename}_extruded.obj')