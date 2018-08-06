#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ObjLoader
from Exporter import Exporter
from Model import Model

if __name__ == "__main__":
    filename = 'cube'
    obj_data = ObjLoader.ObjLoader(f'../example/{filename}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=10)
    obj_model.simplify()

    obj_model.extrude(5., faces=obj_model._faces)

    Exporter.translate(obj_model, -obj_model.get_center())  # center object
    Exporter.write_obj(obj_model, f'../export/_{filename}_extruded.obj')