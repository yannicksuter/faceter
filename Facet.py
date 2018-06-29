from Model import *
from ObjExporter import ObjExporter

class Facet(Model):
    def __init__(self, face, model, brick_height, top_height, top_size):
        Model.__init__(self)

        # define upper and lower vertices
        verts = []
        verts_inner = []
        verts_top = []

        for vid in face._vids:
            verts.append(model._vertices[vid])
            verts_inner.append(model._vertices[vid] + (-1. * brick_height * model._vertices_norm[vid]))
            verts_top.append(face._center + ((model._vertices[vid]-face._center) * top_size) - (face._norm * top_height))
        self.add_face(verts)

        # reverse id order to generate the correct face orientation
        verts = list(reversed(verts))
        verts_inner = list(reversed(verts_inner))
        verts_top = list(reversed(verts_top))
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

    obj_name = 'abstract'

    obj_data = ObjLoader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=1.)
    obj_model.simplify()

    print(f'Faces: {len(obj_model._faces)}')
    print(f'Vertices: {len(obj_model._vertices)}')
    bbox_size = obj_model.get_size()
    print(f'Boundingbox: [{bbox_size[0]}, {bbox_size[1]}, {bbox_size[2]}]')

    ObjExporter.write(obj_model, f'./export/_{obj_name}.obj')

    y = 0.

    faceted_model = Model()
    striped_model = Model()
    for face_id in range(len(obj_model._faces)):
        ref_face = obj_model._faces[face_id]
        print(f'processing facet #{face_id}')
        facet = Facet(ref_face, obj_model, brick_height=10., top_size=.1, top_height=15.)
        # facet.translate(ref_face._norm * 10)
        faceted_model.merge_model(facet)

        facet = ObjExporter.rotate_model(facet, obj_model._faces[face_id]._norm)
        ObjExporter.write(facet, f'./export/_{obj_name}_part_{face_id+1}.obj')

        # calculate facet meta data for proper export
        facet.calculate_centers()
        facet.calculate_boundingbox()
        y += facet.get_size()[1]

        facet = ObjExporter.translate_model(facet, np.array([0., y, 0.]), facet._faces[0]._center)
        striped_model.merge_model(facet)

    striped_model = ObjExporter.move_model(striped_model, np.array([0., -.5*y, 0.]))
    ObjExporter.write(striped_model, f'./export/_{obj_name}_striped.obj')
    ObjExporter.write(faceted_model, f'./export/_{obj_name}_faceted.obj')
