import unittest

import ObjLoader
from Model import Model

class TestModel(unittest.TestCase):
    def test_simplify_quad(self):
        obj_data = ObjLoader.ObjLoader('../example/quad.obj')
        obj_model = Model.load_fromdata(obj_data)
        obj_model.simplify()
        self.assertEqual(len(obj_model._faces), 1)

    def test_simplify_strip(self):
        obj_data = ObjLoader.ObjLoader('../example/tri_strip.obj')
        obj_model = Model.load_fromdata(obj_data)
        obj_model.simplify()
        self.assertEqual(len(obj_model._faces), 1)

    def test_simplify_cube(self):
        obj_data = ObjLoader.ObjLoader('../example/cube.obj')
        obj_model = Model.load_fromdata(obj_data)
        """
        before simplification:
        
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

if __name__ == '__main__':
    unittest.main()