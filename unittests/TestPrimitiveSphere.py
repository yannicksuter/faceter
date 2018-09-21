import primitives
import ObjExporter

if __name__ == "__main__":
    sphere = primitives.Sphere(100.)
    sphere_model = sphere.triangulate(2)

    sphere_model.triangulate()
    ObjExporter.write(sphere_model, f'./export/_logo_badge.obj')

