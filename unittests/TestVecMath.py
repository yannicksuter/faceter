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

if __name__ == '__main__':
    unittest.main()