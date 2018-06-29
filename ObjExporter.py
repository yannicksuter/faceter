import os
import numpy as np
from VecMath import VecMath
from Model import *

class ObjExporter:
    def __init__(self, model, export_filepath):
        pass

    @staticmethod
    def rotate_model(model, from_vec, to_vec=np.array([-1., 0., 0.])):
        rot_mtx = VecMath.get_rotation_matrix(from_vec, to_vec)
        for vid in range(len(model._vertices)):
            vert = (rot_mtx.__matmul__(model._vertices[vid]))[0,:]
            model._vertices[vid] = np.asarray(vert).reshape(-1)
        return model

    @staticmethod
    def translate_model(model, ref_vec, to_vec=np.array([0., 0., 0.])):
        t = to_vec - ref_vec
        for vid in range(len(model._vertices)):
            model._vertices[vid] -= t
        return model

    @staticmethod
    def move_model(model, vec):
        for vid in range(len(model._vertices)):
            model._vertices[vid] -= vec
        return model

    @staticmethod
    def write(model, export_filepath):
        try:
            path, filename = os.path.split(export_filepath)
            with open(export_filepath, 'w') as obj_export:
                obj_export.write(f'# {filename}\n#\n\ng {model._name}\n')

                # export vertices
                obj_export.write(f'\n')
                for vert in model._vertices:
                    obj_export.write('v %.3f %.3f %.3f\n' % (vert[0], vert[1], vert[2]))

                # export faces
                obj_export.write(f'\n')
                for face in model._faces:
                    obj_export.write('f ' + ' '.join([f'{vid+1}//' for vid in face._vids]) + '\n')

                print(f'Export: {filename} successfully written.')
        except:
            print("Export: .obj file could not be written.")

if __name__ == "__main__":
    import ObjLoader
    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data)

    obj_model.simplify()

    ObjExporter.write(obj_model, './export/_cube.obj')
