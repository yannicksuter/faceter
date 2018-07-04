import unittest
import numpy as np
from Plane import Plane

class TestPlane(unittest.TestCase):
    def test_intersect_plane_ray(self):
        plane = Plane(np.array([0., 0., 5.]), np.array([0., 0., 1.]))
        intersection_point = plane.intersect_with_ray(np.array([0., -1., -1.]), np.array([0., 0., 10.]))
        np.testing.assert_array_equal(intersection_point, np.array([0., -5., 5.]))

if __name__ == '__main__':
    unittest.main()