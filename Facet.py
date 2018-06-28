from Model import *
from ObjExporter import ObjExporter

class Facet(Model):
    def __init__(self, face, model, height, top_height, top_size):
        Model.__init__(self)

        # define upper and lower vertices
        verts = []
        verts_inner = []
        verts_top = []

        for vid in face._vids:
            verts.append(model._vertices[vid])
            verts_inner.append(model._vertices[vid] + (-1. * height * model._vertices_norm[vid]))
            verts_top.append(face._center + ((model._vertices[vid]-face._center) * top_size) - (face._norm * top_height))
        self.add_face(verts)
        # self.add_face(verts_inner)
        self.add_face(verts_top)

        # add sides
        cnt = len(face._vids)
        for i in range(cnt):
            side_verts = []
            side_verts.append(verts[i])
            side_verts.append(verts[(i+1)%cnt])
            side_verts.append(verts_inner[(i+1)%cnt])
            side_verts.append(verts_inner[i])
            self.add_face(side_verts)

            top_side_verts = []
            top_side_verts.append(verts_inner[i])
            top_side_verts.append(verts_inner[(i+1)%cnt])
            top_side_verts.append(verts_top[(i+1)%cnt])
            top_side_verts.append(verts_top[i])
            self.add_face(top_side_verts)

if __name__ == "__main__":
    import ObjLoader

    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data, scale=10.)
    obj_model.simplify()
    ObjExporter.write(obj_model, './export/_cube.obj')

    z = 0.

    facet_model = Model()
    for face_id in range(len(obj_model._faces)):
        facet = Facet(obj_model._faces[face_id], obj_model, 2., top_size=.1, top_height=3.)
        facet = ObjExporter.rotate_model(facet, obj_model._faces[face_id]._norm)
        ObjExporter.write(facet, f'./export/_rpart[{face_id+1}].obj')

        z += 11.
        facet.calculate_centers()
        facet = ObjExporter.translate_model(facet, np.array([0., z, 0.]), facet._faces[0]._center)
        facet_model.merge_model(facet)

    ObjExporter.write(facet_model, './export/_faceted.obj')
