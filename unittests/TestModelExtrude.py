#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ObjLoader
from Exporter import *
from model import Model

if __name__ == "__main__":
    filename = 'cube'
    obj_data = ObjLoader.ObjLoader(f'../example/{filename}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=10)
    obj_model.simplify()

    obj_model._groups[0]._material._diffuse = [1., 0., 0.]
    obj_model.extrude(5., faces=obj_model._faces)

    translate(obj_model, -obj_model._center)  # center object
    write_obj(obj_model, f'../export/_{filename}_extruded.obj')