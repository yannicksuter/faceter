
class Edge:
    def __init__(self, face, v0_id, v1_id, len):
        self.v0_id = v0_id
        self.v1_id = v1_id
        self.length = len
        self._face = face
        self._neighbour_faces = []

    def to_string(self):
        print(f'EDGE: {v0_id} -> {v1_id}')

    def is_equal(self, edge):
        return (self.v0_id == edge.v0_id and self.v1_id == edge.v1_id) or (self.v1_id == edge.v0_id and self.v0_id == edge.v1_id)

    def calculate_neighbours(self, faces):
        self._neighbour_faces = []
        for face in faces:
            for edge in face._edges:
                if self.is_equal(edge):
                    self._neighbour_faces.append(face)

    @staticmethod
    def get_shared_edge(edge, edge_list):
        for e_id, e_other in enumerate(edge_list):
            if e_other.is_equal(edge):
                return e_id
        return None