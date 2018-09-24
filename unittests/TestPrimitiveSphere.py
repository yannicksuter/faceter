import primitives
import ObjExporter
import numpy as np

#https://sites.google.com/site/dlampetest/python/triangulating-a-sphere-recursively

if __name__ == "__main__":
    sphere = primitives.Sphere(100.)
    sphere_model = sphere.triangulate(2)

    sphere_model.triangulate()
    ObjExporter.write(sphere_model, f'./export/_sphere.obj')
