import ObjLoader
import numpy as np

DEBUG = True

class Edge:
    def __init__(self, v0, v0_id, v1, v1_id):
        self.v0 = v0
        self.v0_id = v0_id
        self.v1 = v1
        self.v1_id = v1_id
        if DEBUG:
            print(f'EDGE: {v0_id}:{v0} -> {v1_id}:{v1}')

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
            v0 = vertices[i]
            v1_id = vertices_ids[(i+1)%len(vertices_ids)]
            v1 = vertices[(i+1)%len(vertices_ids)]
            self._edges.append(Edge(v0, v0_id, v1, v1_id))

        # face normal vector
        self._vids = vertices_ids
        self._norm = np.cross(vertices[1]-vertices[0], vertices[2]-vertices[0])
        self._norm /= np.linalg.norm(self._norm)

    def contains_v(self, vid):
        for id in self._vids:
            if id == vid:
                return True
        return False

    def detect_neighbour(self, face):
        for edge in self._edges:
            for edge_ in face._edges:
                if edge.is_equal(edge_):
                    if face not in self._neighbour_faces:
                        self._neighbour_faces.append(face)

class Model:
    def __init__(self, obj_data):
        self._vertices = []
        for v in obj_data.vertices:
            self._vertices.append(np.array(v))

        self._faces = []
        for face_data in obj_data.faces:
            vertices = []
            vertices_ids = []
            for f_id, t_id, n_id in face_data:
                vertices.append(self._vertices[f_id - 1])
                vertices_ids.append(f_id)
            self._faces.append(Face(vertices, vertices_ids))

        # detect face neighbours
        for face in self._faces:
            for face_ in self._faces:
                if face is not face_:
                    face.detect_neighbour(face_)

        #calculate vertice normals
        self._vertices_norm = []
        for v_id in range(len(obj_data.vertices)):
            v_norm = np.array([0.,0.,0.])
            for face in self._faces:
                if face.contains_v(v_id+1):
                    v_norm += face._norm
            v_norm /= np.linalg.norm(v_norm)
            self._vertices_norm.append(v_norm)

if __name__ == "__main__":
    obj_data = ObjLoader.ObjLoader('./example/quad.obj')
    obj_model = Model(obj_data)

    for f_id in range(len(obj_model._faces)):
        print(f'f[{f_id+1}] -> ids:{obj_model._faces[f_id]._vids}, n:{obj_model._faces[f_id]._norm}')

    for v_id in range(len(obj_model._vertices)):
        print(f'v[{v_id+1}] -> p:{obj_model._vertices[v_id]}, n:{obj_model._vertices_norm[v_id]}')
