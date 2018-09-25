import model
from euclid import euclid
import numpy as np
import VecMath as vm

class Sphere:
    __octahedron_vertices = np.array([
        [1.0, 0.0, 0.0],  # 0
        [-1.0, 0.0, 0.0],  # 1
        [0.0, 1.0, 0.0],  # 2
        [0.0, -1.0, 0.0],  # 3
        [0.0, 0.0, 1.0],  # 4
        [0.0, 0.0, -1.0]  # 5
    ])
    __octahedron_triangles = np.array([
        [0, 4, 2],
        [2, 4, 1],
        [1, 4, 3],
        [3, 4, 0],
        [0, 2, 5],
        [2, 1, 5],
        [1, 3, 5],
        [3, 0, 5]])

    def __init__(self, radius, center=euclid.Vector3(0.,0.,0.)):
        self._center = euclid.Vector3(center[0], center[1], center[2])
        self._radius = radius

    def triangulate(self, recursion_level=2):
        vertex_array, index_array = self.__create_unit_sphere(recursion_level)
        sphere_model = model.Model()
        for face in index_array:
            vertices = []
            for v_id in face:
                vertices.extend([vertex_array[v_id]*self._radius])
            sphere_model.add_face(list(reversed(vertices)))
            # sphere_model.add_face(vertices)
        return sphere_model

    def __normalize_v3(self, arr):
        ''' Normalize a numpy array of 3 component vectors shape=(n,3) '''
        lens = np.sqrt(arr[:, 0] ** 2 + arr[:, 1] ** 2 + arr[:, 2] ** 2)
        arr[:, 0] /= lens
        arr[:, 1] /= lens
        arr[:, 2] /= lens
        return arr

    def __divide_all(self, vertices, triangles):
        # Subdivide each triangle in the old approximation and normalize
        #  the new points thus generated to lie on the surface of the unit
        #  sphere.
        # Each input triangle with vertices labelled [0,1,2] as shown
        #  below will be turned into four new triangles:
        #
        #            Make new points
        #                 a = (0+2)/2
        #                 b = (0+1)/2
        #                 c = (1+2)/2
        #        1
        #       /\        Normalize a, b, c
        #      /  \
        #    b/____\ c    Construct new triangles
        #    /\    /\       t1 [0,b,a]
        #   /  \  /  \      t2 [b,1,c]
        #  /____\/____\     t3 [a,b,c]
        # 0      a     2    t4 [a,c,2]

        v = []
        for tri in triangles:
            v0 = vertices[tri[0]]
            v1 = vertices[tri[1]]
            v2 = vertices[tri[2]]
            a = vm.unit_vector((v0 + v2) * 0.5)
            b = vm.unit_vector((v0 + v1) * 0.5)
            c = vm.unit_vector((v1 + v2) * 0.5)
            v += [v0, b, a, b, v1, c, a, b, c, a, c, v2]
        return v, np.arange(len(v)).reshape((-1, 3))

    def __create_unit_sphere(self, recursion_level=2):
        vertex_array, index_array = self.__octahedron_vertices, self.__octahedron_triangles
        for i in range(recursion_level - 1):
            vertex_array, index_array = self.__divide_all(vertex_array, index_array)
        return vertex_array, index_array

    def __vertex_array_only_unit_sphere(self, recursion_level=2):
        vertex_array, index_array = self.__create_unit_sphere(recursion_level)
        if recursion_level > 1:
            return vertex_array.reshape((-1))
        else:
            return vertex_array[index_array].reshape((-1))