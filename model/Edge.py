
class Edge:
    def __init__(self, v0_id, v1_id, len):
        self.v0_id = v0_id
        self.v1_id = v1_id
        self.length = len

    def to_string(self):
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