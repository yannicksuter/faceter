import math
from model import *
import Exporter

def generate_facet(dest_model, source_model, face, brick_height, top_height, top_size):
    # define upper and lower vertices
    verts = []
    verts_inner = []
    verts_top = []

    for vid in face._vertex_ids:
        verts.append(source_model._vertices[vid])
        verts_inner.append(source_model._vertices[vid] + (-1. * brick_height * source_model._vertices_norm[vid]))
        verts_top.append(face._center + ((source_model._vertices[vid] - face._center) * top_size) - (face._norm * top_height))
    dest_model.add_face(verts, tags=['bottom'])

    # reverse id order to generate the correct face orientation
    verts = list(reversed(verts))
    verts_inner = list(reversed(verts_inner))
    verts_top = list(reversed(verts_top))
    dest_model.add_face(verts_top, tags=['top'])

    # add sides
    cnt = len(face._vertex_ids)
    for i in range(cnt):
        side_verts = []
        side_verts.append(verts[i])
        side_verts.append(verts[(i + 1) % cnt])
        side_verts.append(verts_inner[(i + 1) % cnt])
        side_verts.append(verts_inner[i])
        dest_model.add_face(side_verts)
        top_side_verts = []
        top_side_verts.append(verts_inner[i])
        top_side_verts.append(verts_inner[(i + 1) % cnt])
        top_side_verts.append(verts_top[(i + 1) % cnt])
        top_side_verts.append(verts_top[i])
        dest_model.add_face(top_side_verts)

class Facet(Model):
    def __init__(self, face, model, brick_height, top_height, top_size):
        Model.__init__(self)

        # calculate the face data
        generate_facet(self, model, face, brick_height, top_height, top_size)

        #finalize model
        self._update()

if __name__ == "__main__":
    import ObjLoader

    obj_name = 'abstract'

    obj_data = ObjLoader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=1.)
    obj_model.simplify()

    print(f'Faces: {len(obj_model._faces)}')
    print(f'Vertices: {len(obj_model._vertices)}')
    bbox_size = obj_model._size
    print(f'Boundingbox: [{bbox_size[0]}, {bbox_size[1]}, {bbox_size[2]}]')

    Exporter.write(obj_model, f'./export/_{obj_name}.obj')

    target_lid_size = 100. #mm^2

    faceted_model = Model()
    for face_id in range(len(obj_model._faces)):
        ref_face = obj_model._faces[face_id]
        print(f'processing facet #{face_id}')

        # calculate scale factor to get a constant lid size
        face_surface = ref_face.get_area()
        ttop_size = (target_lid_size / math.sqrt(face_surface)) / 10

        facet = Facet(ref_face, obj_model, brick_height=10., top_height=15., top_size=ttop_size)
        faceted_model.merge(facet)

        # export single part
        Exporter.write(facet, f'./export/_{obj_name}_part_{face_id+1}.obj', obj_model._faces[face_id]._norm)

    # faceted_model.triangulate()
    Exporter.write(faceted_model, f'./export/_{obj_name}_faceted.obj')
