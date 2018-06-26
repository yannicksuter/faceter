from Model import *
from ObjExporter import ObjExporter

class Facet(Model):
    def __init__(self, face, model, height):
        Model.__init__(self)

        # define upper and lower vertices
        verts = []
        verts_inner = []
        for vid in face._vids:
            verts.append(model._vertices[vid])
            verts_inner.append(model._vertices[vid] + (-1. * height * model._vertices_norm[vid]))
        self.add_face(verts)
        self.add_face(verts_inner)

        # add sides
        cnt = len(face._vids)
        for i in range(cnt):
            side_verts = []
            side_verts.append(verts[i])
            side_verts.append(verts[(i+1)%cnt])
            side_verts.append(verts_inner[(i+1)%cnt])
            side_verts.append(verts_inner[i])
            self.add_face(side_verts)

if __name__ == "__main__":
    import ObjLoader

    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data, scale=10.)
    obj_model.simplify()
    ObjExporter.write(obj_model, './export/_cube.obj')

    for face_id in range(len(obj_model._faces)):
        facet = Facet(obj_model._faces[face_id], obj_model, 2.)
        ObjExporter.write(facet, f'./export/_part[{face_id+1}].obj')

    # facet_model = Model()
    # for face in obj_model._faces:
    #     facet_model.merge(Facet(face, obj_model, 0.1))
    # ObjExporter.write(facet_model, './export/_faceted.obj')
