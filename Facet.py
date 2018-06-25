from Model import *
from ObjExporter import ObjExporter

class Facet(Model):
    def __init__(self, face):
        pass

if __name__ == "__main__":
    import ObjLoader

    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data)

    facet_model = Model()
    for face in obj_model._faces:
        facet_model.merge(Facet(face))

    ObjExporter.write(facet_model, './export/_faceted.obj')
