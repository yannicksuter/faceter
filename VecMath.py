import numpy as np

class VecMath:
    @staticmethod
    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    @staticmethod
    def angle_between(v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                >>> VecMath.angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                >>> VecMath.angle_between((1, 0, 0), (1, 0, 0))
                0.0
                >>> VecMath.angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = VecMath.unit_vector(v1)
        v2_u = VecMath.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

if __name__ == "__main__":
    import doctest
    doctest.testmod()