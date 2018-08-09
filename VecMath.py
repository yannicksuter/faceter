import numpy as np

EPSILON = 0.0001

class VecMath:
    _X = 0
    _Y = 1
    _Z = 2

    @staticmethod
    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        if np.linalg.norm(vector) == 0.:
            return vector
        return vector / np.linalg.norm(vector)

    @staticmethod
    def equal(v1, v2):
        return all(abs(u0-u1) < EPSILON for u0, u1 in zip(v1, v2))
        # return np.array_equal(v1, v2)

    @staticmethod
    def angle_between(v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2' """
        v1_u = VecMath.unit_vector(v1)
        v2_u = VecMath.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    @staticmethod
    def dist_point_to_point(p1, p2):
        return np.linalg.norm(p2 - p1)

    @staticmethod
    def len(v):
        """Return the len of a n-dimentional vector"""
        return np.linalg.norm(v)

    @staticmethod
    def dist_point_to_line(line_point, line_dir, point):
        """Calculate the distance of a point perpendicular to a line defined by line_point and dir."""
        return np.linalg.norm(np.abs(np.cross(line_dir, line_point - point) / np.linalg.norm(line_dir)))

    @staticmethod
    def rotate_fromto_matrix(ref_vec, to_vec=np.array([1., 0., 0.])):
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