import math
from model import *
import ObjExporter

class Facet(Model):
    def __init__(self, face, source_model, brick_height, top_height, top_size):
        Model.__init__(self)

        # calculate the face data
        self._top_side_labels = {}
        self.generate_facet(source_model, face, brick_height, top_height, top_size)

        #finalize model
        self._update()

    def generate_facet(self, source_model, face, brick_height, top_height, top_size):
        # define upper and lower vertices
        verts = []
        verts_inner = []
        verts_top = []

        for vid in face._vertex_ids:
            verts.append(source_model._vertices[vid])
            verts_inner.append(source_model._vertices[vid] + (-1. * brick_height * source_model._vertices_norm[vid]))
            verts_top.append(face._center + ((source_model._vertices[vid] - face._center) * top_size) - (face._norm * top_height))
        self.add_face(verts, tags=['bottom'])

        # reverse id order to generate the correct face orientation
        verts = list(reversed(verts))
        verts_inner = list(reversed(verts_inner))
        verts_top = list(reversed(verts_top))
        self.add_face(verts_top, tags=['top'])

        # add sides
        cnt = len(face._vertex_ids)
        for i in range(cnt):
            side_verts = []
            side_verts.append(verts[i])
            side_verts.append(verts[(i + 1) % cnt])
            side_verts.append(verts_inner[(i + 1) % cnt])
            side_verts.append(verts_inner[i])
            self.add_face(side_verts, tags=['facet_bottom_layer'])
            top_side_verts = []
            top_side_verts.append(verts_inner[i])
            top_side_verts.append(verts_inner[(i + 1) % cnt])
            top_side_verts.append(verts_top[(i + 1) % cnt])
            top_side_verts.append(verts_top[i])
            top_side = self.add_face(top_side_verts, tags=['facet_top_layer'])
            if face._edges[i]._neighbour_faces:
                label_id = hash(tuple(sorted([id(face), id(face._edges[i]._neighbour_faces[0])])))
                # edge_A = verts_inner[i]
                # edge_B = verts_inner[(i + 1) % cnt]
                edge_A = source_model._vertices[face._edges[i].v0_id] + (-1. * brick_height * source_model._vertices_norm[face._edges[i].v0_id])
                edge_B = source_model._vertices[face._edges[i].v1_id] + (-1. * brick_height * source_model._vertices_norm[face._edges[i].v1_id])
                self._top_side_labels[label_id] = [edge_A, edge_B]
                # print(f'{label_id} = {edge_A} - {edge_B}')
