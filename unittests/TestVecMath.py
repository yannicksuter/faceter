import unittest

import numpy as np
from VecMath import VecMath

class TestVecMath(unittest.TestCase):
    def test_unit_vector(self):
        self.assertEqual(np.linalg.norm(VecMath.unit_vector(np.array([1., 2., 3.]))), 1.)

    def test_angle_between(self):
        self.assertEqual(VecMath.angle_between((1, 0, 0), (0, 1, 0)), 1.5707963267948966)
        self.assertEqual(VecMath.angle_between((1, 0, 0), (1, 0, 0)), 0.0)
        self.assertEqual(VecMath.angle_between((1, 0, 0), (-1, 0, 0)), 3.141592653589793)

    def test_get_rotation_mtx(self):
        a = np.array([1., 0., 0.])
        b = np.array([0., 1., 0.])
        rot = VecMath.get_rotation_matrix(a, b)
        self.assertIsNotNone(rot)

        a2 = rot.__matmul__(a)
        self.assertNotEqual(VecMath.angle_between(a, b), 0.0)
        self.assertEqual(VecMath.angle_between(a2, b), 0.0)

    def test_get_rotation_mtx_equal_vecs(self):
        """ edge case: would normaly break rot mtx. use identity mtx instead """
        a = np.array([1., 0., 0.])
        b = np.array([1., 0., 0.])
        rot = VecMath.get_rotation_matrix(a, b)
        self.assertIsNotNone(rot)

        a2 = rot.__matmul__(a)
        self.assertEqual(VecMath.angle_between(a2, b), 0.0)

    def test_dist_point_to_line(self):
        line_p = np.array([0., 0., 0.])
        line_dir = np.array([1., 0., 0.])

        dist = VecMath.dist_point_to_line(line_p, line_dir, np.array([-1., 2., 0.]))
        self.assertEqual(dist, 2.)

    def test_dist_point_to_line2(self):
        line_p = np.array([0., 0., 0.])
        line_dir = np.array([1., 1.,1.])

        dist = VecMath.dist_point_to_line(line_p, line_dir, np.array([0., .2, .5]))
        self.assertEqual(dist, 2.)


if __name__ == '__main__':
    unittest.main()