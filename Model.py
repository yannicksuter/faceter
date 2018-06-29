import ObjLoader
from VecMath import VecMath
import numpy as np
import math

EPSILON = 0.00001
DEBUG = False

class Edge:
    def __init__(self, v0_id, v1_id, len):
        self.v0_id = v0_id
        self.v1_id = v1_id
        self.length = len
        if DEBUG:
            print(f'EDGE: {v0_id} -> {v1_id}')

    def is_equal(self, edge):
        if (self.v0_id == edge.v0_id and self.v1_id == edge.v1_id) or \
                (self.v1_id == edge.v0_id and self.v0_id == edge.v1_id):
            return True
        return False

    @staticmethod
    def get_shared_edge(edge, edge_list):
        for e_id in range(len(edge_list)):
            if edge_list[e_id].is_equal(edge):
                return e_id
        return None

class Face:
    def __init__(self, vertices, vertices_ids):
        if DEBUG:
            print(f'FACE: {vertices_ids}')

        self._vids = vertices_ids
        self._edges = []
        self._neighbour_faces = []

        for i in range(len(vertices_ids)):
            v0_id = vertices_ids[i]
            v1_id = vertices_ids[(i+1)%len(vertices_ids)]
            self._edges.append(Edge(v0_id, v1_id, np.linalg.norm(vertices[v1_id]-vertices[v0_id])))

        # face normal vector
        self.calculate_norm(vertices)

        # face center
        self._center = np.array([0., 0., 0.])
        for vid in self._vids:
            self._center += vertices[vid]
        self._center /= float(len(self._vids))

    def calculate_norm(self, vertices):
        self._norm = np.cross(vertices[self._vids[1]]-vertices[self._vids[0]], vertices[self._vids[2]]-vertices[self._vids[0]])
        self._norm = VecMath.unit_vector(self._norm)

    def contains_v(self, vid):
        for id in self._vids:
            if id == vid:
                return True
        return False

    def is_neighbour(self, face):
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
        if len(self._vids) > 3:
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

class Model:
    def __init__(self):
        self._name = 'unknown'
        self._vertices = []
        self._faces = []
        self._vertices_norm = []
        self._bbox = [np.array([0.,0.,0.]), np.array([0.,0.,0.])]

    @classmethod
    def load_fromdata(cls, obj_data, scale=1.):
        cls = Model()
        cls._name = 'unknown'

        cls._vertices = []
        for v in obj_data.vertices:
            cls._vertices.append(np.array(v)*scale)

        cls._faces = []
        for face_data in obj_data.faces:
            vertices_ids = []
            for f_id, t_id, n_id in face_data:
                f_id -= 1
                vertices_ids.append(f_id)
            cls._faces.append(Face(cls._vertices, vertices_ids))

        # detect face neighbours and vertice-normals
        cls.calculate_neighbours()
        cls.calculate_vertice_norms()
        cls.calculate_boundingbox()

        return cls

    def calculate_centers(self):
        for face in self._faces:
            face._center = np.array([0., 0., 0.])
            for vid in face._vids:
                face._center += self._vertices[vid]
            face._center /= float(len(face._vids))

    def calculate_face_norms(self):
        for face in self._faces:
            face.calculate_norm(self._vertices)

    def calculate_vertice_norms(self):
        self._vertices_norm = []
        for v_id in range(len(self._vertices)):
            v_norm = np.array([0.,0.,0.])
            for face in self._faces:
                if face.contains_v(v_id):
                    v_norm += face._norm
            self._vertices_norm.append(VecMath.unit_vector(v_norm))

    def calculate_neighbours(self):
        for face in self._faces:
            face._neighbour_faces = []
            for face_ in self._faces:
                if face is not face_ and face.is_neighbour(face_):
                    face._neighbour_faces.append(face_)

    def calculate_boundingbox(self):
        self._bbox = [np.array([self._vertices[0][0],self._vertices[0][1],self._vertices[0][2]]), np.array([self._vertices[0][0],self._vertices[0][1],self._vertices[0][2]])]
        for vert in self._vertices:
            self._bbox[0][0] = min(self._bbox[0][0], vert[0])
            self._bbox[0][1] = min(self._bbox[0][1], vert[1])
            self._bbox[0][2] = min(self._bbox[0][2], vert[2])
            self._bbox[1][0] = max(self._bbox[1][0], vert[0])
            self._bbox[1][1] = max(self._bbox[1][1], vert[1])
            self._bbox[1][2] = max(self._bbox[1][2], vert[2])

    def get_size(self):
        return np.absolute(self._bbox[1] - self._bbox[0])

    def get_vertId(self, vert):
        for vid in range(len(self._vertices)):
            if np.linalg.norm(self._vertices[vid]-vert) < EPSILON:
                return vid
        return None

    def add_face(self, verts):
        vertices_ids = []
        for vert in verts:
            vid = self.get_vertId(vert)
            if vid is None:
                vid = len(self._vertices)
                self._vertices.append(vert)
            vertices_ids.append(vid)
        face = Face(self._vertices, vertices_ids)
        self._faces.append(face)
        return face

    def remove_face(self, face):
        # todo: remove unused verts when removing a face
        if face in self._faces:
            self._faces.remove(face)

    def merge_model(self, model):
        for face in model._faces:
            self.add_face([model._vertices[vid] for vid in face._vids])

    def simplify(self):
        for face in list(self._faces): # very important to copy the list first as we modify while iteration is not done yet
            for neighbour in face._neighbour_faces:
                if VecMath.angle_between(face._norm, neighbour._norm) < EPSILON:
                    v_ids = face.merge_face_vids(neighbour)
                    # as we are modifying the list while iterating though it we need this test to check if the consolidation of this tri was already done
                    if v_ids and len(face._vids) < len(v_ids):
                        self.remove_face(face)
                        self.remove_face(neighbour)
                        self.add_face([self._vertices[id] for id in v_ids])

        # recalculate neighbours and v_norms
        self.calculate_centers()
        self.calculate_neighbours()
        self.calculate_vertice_norms()
        self.calculate_boundingbox()

if __name__ == "__main__":
    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data)
    obj_model.simplify()

    for f_id in range(len(obj_model._faces)):
        print(f'f[{f_id+1}] -> ids:{obj_model._faces[f_id]._vids}, n:{obj_model._faces[f_id]._norm}')

    for v_id in range(len(obj_model._vertices)):
        print(f'v[{v_id+1}] -> p:{obj_model._vertices[v_id]}, n:{obj_model._vertices_norm[v_id]}')
