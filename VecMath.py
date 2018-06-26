import numpy as np

EPSILON = 0.00001

class VecMath:
    @staticmethod
    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    @staticmethod
    def angle_between(v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2' """
        v1_u = VecMath.unit_vector(v1)
        v2_u = VecMath.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    @staticmethod
    def get_rotation_matrix(ref_vec, to_vec=np.array([1., 0., 0.])):
        a, b = VecMath.unit_vector(ref_vec), VecMath.unit_vector(to_vec)

        if VecMath.angle_between(a,b) == 0:
            return np.matrix("1.0 0.0 0.0; 0.0 1.0 0.0; 0.0 0.0 1.0", dtype="float16")

        if np.linalg.norm(a+b) == 0:
            # todo: remove this hack, edge case when from -> to spans an angle of PI(rad)
            b = VecMath.unit_vector((to_vec[0]+EPSILON, to_vec[1]+EPSILON, to_vec[2]))

        v = np.cross(a, b)
        c = np.dot(a, b)
        s = np.linalg.norm(v)
        I = np.identity(3)
        k = np.matrix('{} {} {}; {} {} {}; {} {} {}'.format(0, -v[2], v[1], v[2], 0, -v[0], -v[1], v[0], 0))
        r = I + k + np.matmul(k, k) * ((1 - c) / (s ** 2))

        return r

if __name__ == "__main__":
    import doctest
    doctest.testmod()