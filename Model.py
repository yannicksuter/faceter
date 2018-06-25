import ObjLoader
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
        self._norm /= np.linalg.norm(self._norm)

    def contains_v(self, vid):
        for id in self._vids:
            if id == vid:
                return True
        return False

    def detect_neighbour(self, face):
        self._neighbour_faces = []
        for edge in self._edges:
            for edge_ in face._edges:
                if edge.is_equal(edge_):
                    if face not in self._neighbour_faces:
                        self._neighbour_faces.append(face)

class Model:
    def __init__(self):
        self._name = 'unknown'
        self._vertices = []
        self._faces = []
        self._vertices_norm = []

    @classmethod
    def load_fromdata(cls, obj_data):
        cls = Model()
        cls._name = 'unknown'

        cls._vertices = []
        for v in obj_data.vertices:
            cls._vertices.append(np.array(v))

        cls._faces = []
        for face_data in obj_data.faces:
            vertices_ids = []
            for f_id, t_id, n_id in face_data:
                f_id -= 1
                vertices_ids.append(f_id)
            cls._faces.append(Face(cls._vertices, vertices_ids))

        # detect face neighbours
        for face in cls._faces:
            for face_ in cls._faces:
                if face is not face_:
                    face.detect_neighbour(face_)

        #calculate vertice normals
        cls._vertices_norm = []
        for v_id in range(len(obj_data.vertices)):
            v_norm = np.array([0.,0.,0.])
            for face in cls._faces:
                if face.contains_v(v_id):
                    v_norm += face._norm
            v_norm /= np.linalg.norm(v_norm)
            cls._vertices_norm.append(v_norm)

        return cls

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

    def merge(self, model):
        for face in model._faces:
            verts = []
            for vid in face._vids:
                verts.append(model._vertices[vid])
            self.add_face(verts)

if __name__ == "__main__":
    obj_data = ObjLoader.ObjLoader('./example/quad.obj')
    obj_model = Model.load_fromdata(obj_data)

    for f_id in range(len(obj_model._faces)):
        print(f'f[{f_id+1}] -> ids:{obj_model._faces[f_id]._vids}, n:{obj_model._faces[f_id]._norm}')

    for v_id in range(len(obj_model._vertices)):
        print(f'v[{v_id+1}] -> p:{obj_model._vertices[v_id]}, n:{obj_model._vertices_norm[v_id]}')
