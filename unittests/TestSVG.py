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
        R = s1.intersect_line(s2)
        # True: valid intersection
        self.assertTrue(R)

        s1 = svg.Segment2D(None, None, np.array([0, 1]), np.array([2, 1]))
        s2 = svg.Segment2D(None, None, np.array([0, 2]), np.array([2, 2]))
        R = s1.intersect_line(s2)
        # False as lines are parallel
        self.assertTrue(not R)

    def test_split_twisted_shape(self):
        path = svg.Path.read(f'../example/svg/0123.svg')[0]
        vertices=[np.array([0., 0., 0.]),
                  np.array([1., 1., 0.]),
                  np.array([2., 0., 0.]),
                  np.array([3., 1., 0.]),
                  np.array([4., 0., 0.]),
                  np.array([5., 1., 0.]),
                  np.array([6., 0., 0.]),
                  np.array([5., -1., 0.]),
                  np.array([4., 0., 0.]),
                  np.array([3., -1., 0.]),
                  np.array([2., 0., 0.]),
                  np.array([1., -1., 0.])
                  ]
        res = path.split_twisted_shape(vertices)
        self.assertTrue(len(res)==3)

        # still fails
        # vertices=[np.array([0., 0., 0.]),
        #           np.array([1., 1., 0.]),
        #           np.array([0., 2., 0.]),
        #           np.array([-1., 1., 0.]),
        #           np.array([0., 0., 0.]),
        #           np.array([1., 0., 0.]),
        #           np.array([2., -1., 0.]),
        #           np.array([0., 0., 0.]),
        #           np.array([-1., 0., 0.]),
        #           np.array([-2., -1., 0.]),
        #           ]
        # res = path.split_twisted_shape(vertices)
        # self.assertTrue(len(res)==3)

if __name__ == '__main__':
    unittest.main()
