import ObjLoader
from VecMath import VecMath
import numpy as np

EPSILON = 0.00001
DEBUG = False

class Edge:
    def __init__(self, v0_id, v1_id):
        self.v0_id = v0_id
        self.v1_id = v1_id
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

        self._edges = []
        self._neighbour_faces = []
        for i in range(len(vertices_ids)):
            v0_id = vertices_ids[i]
            v1_id = vertices_ids[(i+1)%len(vertices_ids)]
            self._edges.append(Edge(v0_id, v1_id))

        # face normal vector
        self._vids = vertices_ids
        self._norm = np.cross(vertices[vertices_ids[1]]-vertices[vertices_ids[0]], vertices[vertices_ids[2]]-vertices[vertices_ids[0]])
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

    def combine_face(self, face):
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

    def calculate_neighbours(self):
        for face in self._faces:
            face._neighbour_faces = []
            for face_ in self._faces:
                if face is not face_ and face.is_neighbour(face_):
                    face._neighbour_faces.append(face_)

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

        # detect face neighbours
        cls.calculate_neighbours()

        #calculate vertice normals
        cls.calculate_vertice_norms()

        cls._vertices_norm = []
        for v_id in range(len(obj_data.vertices)):
            v_norm = np.array([0.,0.,0.])
            for face in cls._faces:
                if face.contains_v(v_id):
                    v_norm += face._norm
            cls._vertices_norm.append(VecMath.unit_vector(v_norm))

        return cls

    def calculate_vertice_norms(self):
        self._vertices_norm = []
        for v_id in range(len(self._vertices)):
            v_norm = np.array([0.,0.,0.])
            for face in self._faces:
                if face.contains_v(v_id):
                    v_norm += face._norm
            self._vertices_norm.append(VecMath.unit_vector(v_norm))

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
        self._faces.append(Face(self._vertices, vertices_ids))

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
                    v_ids = face.combine_face(neighbour)
                    # as we are modifying the list while iterating though it we need this test to check if the consolidation of this tri was already done
                    if v_ids and len(face._vids) < len(v_ids):
                        self.remove_face(face)
                        self.remove_face(neighbour)
                        self.add_face([self._vertices[id] for id in v_ids])

        # recalculate neighbours and v_norms
        self.calculate_neighbours()
        self.calculate_vertice_norms()

if __name__ == "__main__":
    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data)
    obj_model.simplify()

    for f_id in range(len(obj_model._faces)):
        print(f'f[{f_id+1}] -> ids:{obj_model._faces[f_id]._vids}, n:{obj_model._faces[f_id]._norm}')

    for v_id in range(len(obj_model._vertices)):
        print(f'v[{v_id+1}] -> p:{obj_model._vertices[v_id]}, n:{obj_model._vertices_norm[v_id]}')
