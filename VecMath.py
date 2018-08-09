import numpy as np

EPSILON = 0.0001
_X = 0
_Y = 1
_Z = 2

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    if np.linalg.norm(vector) == 0.:
        return vector
    return vector / np.linalg.norm(vector)

def equal(v1, v2):
    return all(abs(u0-u1) < EPSILON for u0, u1 in zip(v1, v2))

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2' """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def dist_point_to_point(p1, p2):
    return np.linalg.norm(p2 - p1)

def len(v):
    """Return the len of a n-dimentional vector"""
    return np.linalg.norm(v)

def dist_point_to_line(line_point, line_dir, point):
    """Calculate the distance of a point perpendicular to a line defined by line_point and dir."""
    return np.linalg.norm(np.abs(np.cross(line_dir, line_point - point) / np.linalg.norm(line_dir)))

def rotate_fromto_matrix(ref_vec, to_vec=np.array([1., 0., 0.])):
    a, b = unit_vector(ref_vec), unit_vector(to_vec)

    if angle_between(a,b) == 0:
        return np.matrix("1.0 0.0 0.0; 0.0 1.0 0.0; 0.0 0.0 1.0", dtype="float16")

    if np.linalg.norm(a+b) == 0:
        # todo: remove this hack, edge case when from -> to spans an angle of PI(rad)
        b = unit_vector((to_vec[0]+EPSILON, to_vec[1]+EPSILON, to_vec[2]))

    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    I = np.identity(3)
    k = np.matrix('{} {} {}; {} {} {}; {} {} {}'.format(0, -v[2], v[1], v[2], 0, -v[0], -v[1], v[0], 0))
    r = I + k + np.matmul(k, k) * ((1 - c) / (s ** 2))

    return r