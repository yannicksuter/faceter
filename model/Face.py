import numpy as np
import math
from model import *
from VecMath import VecMath

class Face:
    def __init__(self, model, group, vertex_ids, tags=[]):
        self._model = model
        self._group =group
        self._tags = list(tags)
        self._vertex_ids = vertex_ids
        self._edges = []
        self._neighbour_faces = []
        self.__update()

    def __update(self):
        self._edges = []
        for i in range(len(self._vertex_ids)):
            v0_id = self._vertex_ids[i]
            v1_id = self._vertex_ids[(i + 1) % len(self._vertex_ids)]
            self._edges.append(Edge(v0_id, v1_id, np.linalg.norm(self._model._vertices[v1_id]-self._model._vertices[v0_id])))

        # face normal vector
        self.calculate_norm(self._model._vertices)

        # face center
        self._center = np.array([0., 0., 0.])
        for vid in self._vertex_ids:
            self._center += self._model._vertices[vid]
        self._center /= float(len(self._vertex_ids))

    def calculate_norm(self, vertices):
        self._norm = np.cross(vertices[self._vertex_ids[1]] - vertices[self._vertex_ids[0]], vertices[self._vertex_ids[2]] - vertices[self._vertex_ids[0]])
        self._norm = VecMath.unit_vector(self._norm)

    def reverse(self):
        self._vertex_ids = list(reversed(self._vertex_ids))
        self.__update()

    @property
    def _id(self):
        return self._model._faces.index(self)

    @property
    def _vertices(self):
        return [self._model._vertices[v_id] for v_id in self._vertex_ids]

    def get_vertex(self, idx):
        return self._model._vertices[self._vertex_ids[idx]]

    def contains_vertex_id(self, vertex_id):
        """ Returns True if vertex_id is used by the face """
        for id in self._vertex_ids:
            if id == vertex_id:
                return True
        return False

    def is_equal(self, vertex_ids):
        """Returns True if passed vertex_ids define the same face"""
        if not self.contains_vertex_id(vertex_ids[0]):
            return False

        offset = None
        for idx, vertex_id in enumerate(self._vertex_ids):
            if vertex_id == vertex_ids[0]:
                offset = idx

        for i in range(len(vertex_ids)):
            if vertex_ids[i] != self._vertex_ids[(i+offset) % len(self._vertex_ids)]:
                return False
        return True

    def is_neighbour(self, face):
        """ Returns True if face is neighbouring the current face """
        for edge in self._edges:
            for edge_ in face._edges:
                if edge.is_equal(edge_):
                    if face not in self._neighbour_faces:
                        return True
        return False

    def get_triangle_area(self, a, b, c):
        """
        Uses the heron formula to calculate the area
        of the triangle where `a`,`b` and `c` are the side lengths.
        """
        s = (a + b + c) / 2
        return math.sqrt(s * (s - a) * (s - b) * (s - c))

    def get_area(self):
        if len(self._vertex_ids) > 3:
            # todo: needs to be triangulated first, then sum(get_triangle_area(triangle) for triangles)
            raise NotImplementedError
        return self.get_triangle_area(self._edges[0].length, self._edges[1].length, self._edges[2].length)

    def merge_face_vids(self, face):
        v_ids = None
        if len(self._edges) > 2 and len(face._edges) > 2:
            v_ids = []
            for edge1 in self._edges:
                v_ids.append(edge1.v0_id)
                shared_edge_id = Edge.get_shared_edge(edge1, face._edges)
                if shared_edge_id:
                    edge_count = len(face._edges)
                    for i in range(edge_count-2):
                        insert_edge = face._edges[(i+shared_edge_id+1)%edge_count]
                        v_ids.append(insert_edge.v1_id)
        return v_ids