import numpy as np

from model.Face import Face
from model.Group import Group
import VecMath

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
        for mesh_idx, mesh in enumerate(obj_data._meshes.values()):
            for group_idx, group in enumerate(mesh._groups):
                cls.set_group(f'{mesh._name}_{group._material._name}')
                for face in group._faces:
                    vertex_ids = []
                    for f_id, t_id, n_id in face:
                        vertex_ids.append(f_id-1)
                    cls._faces.append(Face(cls, cls._cur_group, vertex_ids))

        cls._update()
        return cls

    def _update(self):
        self.calculate_centers()
        self.calculate_neighbours()
        self.calculate_vertice_norms()
        self.calculate_face_norms()
        self.calculate_boundingbox()

    def add_group(self, name):
        """Add and return new group or will return existing group"""
        name = name.replace(' ', '_')
        group = self.get_group(name)
        if group is None:
            group = Group(self, name)
            self._groups.append(group)
        return group

    def get_group(self, name):
        for group in self._groups:
            if name == group._name:
                return group
        return None

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
        return [face for face in self._faces if tag in face._tags]

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
            for edge in face._edges:
                edge.calculate_neighbours([f for f in self._faces if face != f])
            #
            # face._neighbour_faces = []
            # for face_ in self._faces:
            #     if face is not face_ and face.is_neighbour(face_):
            #         face._neighbour_faces.append(face_)

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

    @property
    def _size(self):
        """ Get size of bounding box """
        return np.absolute(self._bbox[1] - self._bbox[0])

    @property
    def _center(self):
        """ Get size of bounding box """
        return self._bbox[0] + self._size * 0.5

    def get_faces_with_vertex_id(self, vertex_id, in_group=None):
        """ Get list of faces that use vertex (defined bt vertex_id) """
        faces = []
        for face in self._faces:
            if face.contains_vertex_id(vertex_id):
                if in_group==face._group or in_group is None:
                    faces.append(face)
        return faces

    def get_vertId(self, vertex, epsilon=.00001):
        for vid in range(len(self._vertices)):
            if np.linalg.norm(self._vertices[vid]-vertex) < epsilon:
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
            c = self._center
            for vertex in self._vertices:
                vertex[1] = c[1] - (vertex[1]-c[1])
            for face in self._faces:
                face.reverse()
            self._update()

    def simplify(self, epsilon=.00001):
        face_count_before = len(self._faces)
        for face in list(self._faces): # very important to copy the list first as we modify while iteration is not done yet
            for neighbour in face._neighbour_faces:
                if VecMath.angle_between(face._norm, neighbour._norm) < epsilon:
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

    ####
    ## Extrude
    ####

    def _extrude_face(self, face, dir, length, group=None):
        """Extrudes a single face, given a direction and a extrusion length"""
        vertices = [v+dir*length for v in face._vertices]
        #add new top face
        self.add_face(vertices, tags=face._tags, group=face._group)
        #add side faces/quads
        self._cur_group = group
        for i in range(len(vertices)):
            self.add_face([face._vertices[i],
                           face._vertices[(i+1)%len(vertices)],
                           vertices[(i+1)%len(vertices)],
                           vertices[i]])
        #remove old face
        self.remove_face(face)

    def extrude_face(self, face, dir, length, edges, assign_group=None):
        """Extrudes a single face, given a direction and a extrusion length"""
        offset = dir*length
        #add new top face
        self.add_face([v+offset for v in face._vertices], tags=face._tags, group=face._group)

        #add side faces/quads
        self._cur_group = assign_group
        for e in edges:
            self.add_face([self._vertices[e.v0_id], self._vertices[e.v1_id], self._vertices[e.v1_id]+offset, self._vertices[e.v0_id]+offset])

        self.remove_face(face)

    def extrude(self, length, faces=None, group=None):
        """Convenience method to extrude multiple faces/groups with a single call."""
        if faces:
            for face in faces.copy():
                edges = [edge for edge in face._edges if is_border_edge(edge, faces)]
                self.extrude_face(face, face._norm, length, edges, assign_group=group)

def is_border_edge(edge, faces):
    for face in faces:
        if face != edge._face and face in edge._neighbour_faces:
            return False
    return True
