#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ObjLoader

def explode_obj(obj_filename):
    obj_scene = ObjLoader.ObjLoader(obj_filename)
    print(obj_scene)

if __name__ == "__main__":
    explode_obj('./example/cube.obj')