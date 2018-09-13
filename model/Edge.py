import VecMath as vm

class Edge:
    def __init__(self, face, v0_id, v1_id, len, tags=[]):
        self.v0_id = v0_id
        self.v1_id = v1_id
        self.length = len
        self._face = face
        self._tags = list(tags)
        self._neighbour_faces = []

    @property
    def _v0(self):
        return self._face.get_vertex_by_id(self.v0_id)

    @property
    def _v1(self):
        return self._face.get_vertex_by_id(self.v1_id)

    def to_string(self):
        print(f'EDGE: {v0_id} -> {v1_id}')

    def is_equal(self, other):
        if isinstance(other, Edge):
            return (self.v0_id == other.v0_id and self.v1_id == other.v1_id) or (
                        self.v1_id == other.v0_id and self.v0_id == other.v1_id)
        if isinstance(other, list):
            return (vm.equal(self._v0, other[0]) and vm.equal(self._v1, other[1])) or (
                        vm.equal(self._v1, other[0]) and vm.equal(self._v0, other[1]))
        return False

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