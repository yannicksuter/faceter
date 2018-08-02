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

class Group:
    def __init__(self, model, name):
        self._model = model
        self._name = name

    @property
    def _faces(self):
        """Return all faces belonging to the group"""
        return [face for face in self._model._faces if face._group == self]

    @property
    def _bbox(self):
        """Get bounding box for group"""
        bbox = [np.array([0., 0., 0.]), np.array([0., 0., 0.])]
        for face in self._faces:
            for idx in face._vertex_ids:
                vertex = self._model._vertices[idx]
                bbox[0][0] = min(bbox[0][0], vertex[0])
                bbox[0][1] = min(bbox[0][1], vertex[1])
                bbox[0][2] = min(bbox[0][2], vertex[2])
                bbox[1][0] = max(bbox[1][0], vertex[0])
                bbox[1][1] = max(bbox[1][1], vertex[1])
                bbox[1][2] = max(bbox[1][2], vertex[2])
        return bbox

    def get_faces_by_tag(self, tag):
        return [face for face in self._faces if tag in face._tags]

class Model:
    def __init__(self):
        self._name = 'unknown'
        self._vertices = []
        self._groups = []
        self._cur_group = None
        self._faces = []
        self._vertices_norm = []
        self._bbox = [np.array([0.,0.,0.]), np.array([0.,0.,0.])]

    @classmethod
    def load_fromdata(cls, obj_data, scale=1.):
        cls = Model()
        cls._name = 'unknown'

        cls._vertices = []
        for v in obj_data._vertices:
            cls._vertices.append(np.array(v)*scale)

        cls._faces = []
        for group in obj_data._groups:
            cls.set_group(group[0])
            for face_data in group[1]:
                vertex_ids = []
                for f_id, t_id, n_id in face_data:
                    f_id -= 1
                    vertex_ids.append(f_id)
                cls._faces.append(Face(cls, cls._cur_group, vertex_ids))

        cls._update()
        return cls

    def add_group(self, name):
        """Add and return new group or will return existing group"""
        name = name.replace(' ', '_')
        group = None
        for g in self._groups:
            if name == g._name:
                group = g
        if group is None:
            group = Group(self, name)
            self._groups.append(group)
        return group

    def set_group(self, name):
        """Set active group by name."""
        self._cur_group = self.add_group(name)

    def delete_group(self, group):
        raise NotImplementedError

    def get_group_model(self, group):
        model = Model()
        model.set_group(group._name)
        for face in group._faces:
            model.add_face([self._vertices[vid].copy() for vid in face._vertex_ids], tags=face._tags)
        model._update()
        return model

    def get_faces_by_tag(self, tag):
        return [face for face in self._faces if face._tags == tag]

    def calculate_centers(self):
        for face in self._faces:
            face._center = np.array([0., 0., 0.])
            for vertex_id in face._vertex_ids:
                face._center += self._vertices[vertex_id]
            face._center /= float(len(face._vertex_ids))

    def calculate_face_norms(self):
        for face in self._faces:
            face.calculate_norm(self._vertices)

    def calculate_vertice_norms(self):
        self._vertices_norm = []
        for v_id in range(len(self._vertices)):
            v_norm = np.array([0.,0.,0.])
            for face in self._faces:
                if face.contains_vertex_id(v_id):
                    v_norm += face._norm
            self._vertices_norm.append(VecMath.unit_vector(v_norm))

    def calculate_neighbours(self):
        for face in self._faces:
            face._neighbour_faces = []
            for face_ in self._faces:
                if face is not face_ and face.is_neighbour(face_):
                    face._neighbour_faces.append(face_)

    def calculate_boundingbox(self):
        if len(self._vertices) > 0:
            self._bbox = [np.array([self._vertices[0][0],self._vertices[0][1],self._vertices[0][2]]), np.array([self._vertices[0][0],self._vertices[0][1],self._vertices[0][2]])]
            for vertex in self._vertices:
                self._bbox[0][0] = min(self._bbox[0][0], vertex[0])
                self._bbox[0][1] = min(self._bbox[0][1], vertex[1])
                self._bbox[0][2] = min(self._bbox[0][2], vertex[2])
                self._bbox[1][0] = max(self._bbox[1][0], vertex[0])
                self._bbox[1][1] = max(self._bbox[1][1], vertex[1])
                self._bbox[1][2] = max(self._bbox[1][2], vertex[2])
        else:
            self._bbox = [np.array([0., 0., 0.]), np.array([0., 0., 0.])]

    def get_size(self):
        """ Get size of bounding box """
        return np.absolute(self._bbox[1] - self._bbox[0])

    def get_center(self):
        """ Get size of bounding box """
        return self._bbox[0] + self.get_size() * 0.5

    def get_faces_with_vertex_id(self, vertex_id, in_group=None):
        """ Get list of faces that use vertex (defined bt vertex_id) """
        faces = []
        for face in self._faces:
            if face.contains_vertex_id(vertex_id):
                if in_group==face._group or in_group is None:
                    faces.append(face)
        return faces

    def get_vertId(self, vertex):
        for vid in range(len(self._vertices)):
            if np.linalg.norm(self._vertices[vid]-vertex) < EPSILON:
                return vid
        return None

    def add_face(self, vertices, tags=[], group=None):
        vertex_ids = []
        for vertex in vertices:
            vid = self.get_vertId(vertex)
            if vid is None:
                vid = len(self._vertices)
                self._vertices.append(vertex)
            vertex_ids.append(vid)

        # face group
        if group == None:
            if self._cur_group == None:
                self.set_group("default")
            group = self._cur_group

        face = Face(self, group, vertex_ids, tags)
        self._faces.append(face)
        return face

    def remove_face(self, face):
        # todo: remove unused verts when removing a face
        if face in self._faces:
            self._faces.remove(face)

    def merge(self, model, group_name=None):
        if not isinstance(model, Model):
            raise RuntimeError("Cannot merge object other than type Model.")
        if group_name:
            self.set_group(group_name)
        for face in model._faces:
            self.add_face([model._vertices[vid].copy() for vid in face._vertex_ids], face._tags)
        self._update()

    def flip(self, axis_y=False):
        if axis_y:
            c = self.get_center()
            for vertex in self._vertices:
                vertex[1] = c[1] - (vertex[1]-c[1])
            for face in self._faces:
                face.reverse()
            self._update()

    def simplify(self):
        face_count_before = len(self._faces)
        for face in list(self._faces): # very important to copy the list first as we modify while iteration is not done yet
            for neighbour in face._neighbour_faces:
                if VecMath.angle_between(face._norm, neighbour._norm) < EPSILON:
                    v_ids = face.merge_face_vids(neighbour)
                    # as we are modifying the list while iterating though it we need this test to check if the consolidation of this tri was already done
                    if v_ids and len(face._vertex_ids) < len(v_ids):
                        self.remove_face(face)
                        self.remove_face(neighbour)
                        self.add_face([self._vertices[id] for id in v_ids], group=face._group, tags=set(face._tags + neighbour._tags))
        self._update()
        print(f'Simplify: Face count {face_count_before} before -> {len(self._faces)} after')

    def triangulate(self):
        face_count_before = len(self._faces)

        # preprocess faces to find duplicates, in order to handle triangulation the same way / order!
        rev_triangulation = [False] * face_count_before
        for idx, face in enumerate(self._faces):
            for idx2, face2 in enumerate(self._faces):
                if  idx2 < idx and face2.is_equal(list(reversed(face._vertex_ids))):
                    rev_triangulation[idx] = True

        # triangulate
        for face_idx, face in enumerate(list(self._faces)):
            vert_count = len(face._vertex_ids)
            if vert_count > 3:
                self.remove_face(face)
                for i in range(vert_count - 2):
                    offset = 0
                    if rev_triangulation[face_idx]:
                        offset = 1
                    vertex_ids = [face._vertex_ids[0+offset], face._vertex_ids[(i+1+offset) % vert_count], face._vertex_ids[(i+2+offset) % vert_count]]
                    self.add_face([self._vertices[id] for id in vertex_ids], group=face._group)
        self._update()
        print(f'Triangulation: Face count {face_count_before} before -> {len(self._faces)} after')

    def _update(self):
        self.calculate_centers()
        self.calculate_neighbours()
        self.calculate_vertice_norms()
        self.calculate_face_norms()
        self.calculate_boundingbox()

if __name__ == "__main__":
    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data)

    for idx, face in enumerate(obj_model._faces):
        face._tags.append(f'f_{idx}')

    obj_model.simplify()

    for idx, face in enumerate(obj_model._faces):
        print(f'f[{idx+1}] -> ids:{face._vertex_ids}, n:{face._norm}')

    for idx, vertex in enumerate(obj_model._vertices):
        print(f'v[{idx+1}] -> p:{vertex}, n:{obj_model._vertices_norm[idx]}')

    print(f'bbox({obj_model._cur_group._name}): {obj_model._cur_group._bbox}')
    from Exporter import Exporter
    Exporter.write_obj(obj_model, './export/_cube.obj')