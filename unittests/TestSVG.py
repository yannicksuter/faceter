import unittest
import svg
import numpy as np

class TestSVG(unittest.TestCase):
    def test_load_path(self):
        paths = svg.Path.read(f'../example/svg/0123.svg')
        self.assertTrue(paths)

    def test_intersect_line(self):
        s1 = svg.Segment2D(None, None, np.array([0, 1]), np.array([2, 3]))
        s2 = svg.Segment2D(None, None, np.array([2, 3]), np.array([0, 4]))
   L     R = s1.intersect_line(s2)
        # True: valid intersection
        self.assertTrue(R)

        s1 = svg.Segment2D(None, None, np.array([0, 1]), np.array([2, 1]))
        s2 = svg.Segment2D(None, None, np.array([0, 2]), np.array([2, 2]))
        R = s1.intersect_line(s2)
        # False as lines are parallel
        self.assertTrue(not R)

if __name__ == '__main__':
    unittest.main()
