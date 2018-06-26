import unittest

import ObjLoader
from Model import Model

class TestModel(unittest.TestCase):
    def test_simplify_quad(self):
        obj_data = ObjLoader.ObjLoader('../example/quad.obj')
        obj_model = Model.load_fromdata(obj_data)
        obj_model.simplify()
        self.assertEqual(len(obj_model._faces), 1)

    def test_simplify_cube(self):
        obj_data = ObjLoader.ObjLoader('../example/cube.obj')
        obj_model = Model.load_fromdata(obj_data)
        obj_model.simplify()
        self.assertEqual(len(obj_model._faces), 6)

if __name__ == '__main__':
    unittest.main()