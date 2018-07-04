import unittest
import numpy as np
from Plane import Plane

class TestPlane(unittest.TestCase):
    def test_intersect_plane_ray(self):
        plane = Plane(np.array([0., 0., 5.]), np.array([0., 0., 1.]))
        intersection_point = plane.intersect_with_ray(np.array([0., -1., -1.]), np.array([0., 0., 10.]))
        np.testing.assert_array_equal(intersection_point, np.array([0., -5., 5.]))

    def test_intersect_planes(self):
        plane1 = Plane(np.array([0., 0., 0.]), np.array([0., 0., 1.]))
        self.assertTrue(plane1.intersect_with_plane(plane1) == None)

        plane2 = Plane(np.array([1., 1., 1.]), np.array([1., 0., 0.]))
        p, dir = plane1.intersect_with_plane(plane2)
        np.testing.assert_array_equal(p, np.array([1., 0., 0.]))
        np.testing.assert_array_equal(dir, np.array([0., 1., 0.]))

if __name__ == '__main__':
    unittest.main()