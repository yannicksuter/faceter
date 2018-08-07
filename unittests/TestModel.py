import unittest
import ObjLoader
from model import *

class TestModel(unittest.TestCase):
    def test_simplify_quad(self):
        obj_data = ObjLoader.ObjLoader('../example/quad.obj')
        obj_model = Model.load_fromdata(obj_data)
        obj_model.simplify()
        self.assertEqual(len(obj_model._faces), 1)

    def test_simplify_strip(self):
        # todo: unit test is still incorrect -> simplify should normaly reduce strip to 2 quads, ultimatively to 1 coplanar polygone
        obj_data = ObjLoader.ObjLoader('../example/tri_strip.obj')
        obj_model = Model.load_fromdata(obj_data)
        obj_model.simplify()
        self.assertEqual(len(obj_model._faces), 4)

    def test_simplify_cube(self):
        obj_data = ObjLoader.ObjLoader('../example/cube.obj')
        obj_model = Model.load_fromdata(obj_data)
        """ before simplification:
        
        0 6 4 <<--
        0 2 6 n0
        
        0 3 2
        0 1 3
        
        2 7 6 
        2 3 7
        
        4 6 7 n1
        4 7 5
        
        0 4 5 n1
        0 5 1
        
        1 5 7
        1 7 3
        """

        for faces in obj_model._faces:
            self.assertTrue(len(faces._neighbour_faces) == 3)

        # test neighbours for face[0] -> n0, n1, n2
        n_faces = obj_model._faces[0]._neighbour_faces
        self.assertTrue(n_faces[0] == obj_model._faces[1])
        self.assertTrue(n_faces[1] == obj_model._faces[6])
        self.assertTrue(n_faces[2] == obj_model._faces[8])

        obj_model.simplify()
        self.assertEqual(len(obj_model._faces), 6)

    def test_simplify_cube(self):
        obj_data = ObjLoader.ObjLoader('../example/cube.obj')
        obj_model = Model.load_fromdata(obj_data)
        obj_model.simplify()

        self.assertTrue(obj_model._faces[0].is_equal([0,2,6,4]))
        self.assertTrue(obj_model._faces[0].is_equal([6,4,0,2]))
        self.assertFalse(obj_model._faces[0].is_equal([0,1,2,3]))

    def test_cube_bbox(self):
        obj_data = ObjLoader.ObjLoader('../example/cube.obj')
        obj_model = Model.load_fromdata(obj_data)
        size = obj_model.get_size()
        self.assertTrue(size[0] == 1.)
        self.assertTrue(size[1] == 1.)
        self.assertTrue(size[2] == 1.)

if __name__ == '__main__':
    unittest.main()