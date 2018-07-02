import os, datetime
import numpy as np
from VecMath import VecMath
from Model import *

class Exporter:
    def __init__(self, model, export_filepath):
        pass

    @staticmethod
    def rotate_model(model, from_vec, to_vec=np.array([0., 0., -1.])):
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
    def write_obj(model, export_filepath):
        try:
            path, filename = os.path.split(export_filepath)
            with open(export_filepath, 'w') as obj_export:
                obj_export.write(f'# {filename}\n#\n\ng {model._name}\n')

                # export vertices
                obj_export.write(f'\n')
                for vert in model._vertices:
                    obj_export.write('v %.3f %.3f %.3f\n' % tuple(vert[:3]))

                obj_export.write(f'\n')
                for face in model._faces:
                    obj_export.write('vn %.3f %.3f %.3f\n' % tuple(face._norm[:3]))

                # export faces
                obj_export.write(f'\n')
                # for face in model._faces:
                for f_id in range(len(model._faces)):
                    face = model._faces[f_id]
                    obj_export.write('f ' + ' '.join([f'{vid+1}//{f_id+1}' for vid in face._vids]) + '\n')

                print(f'Export: {filename} successfully written.')
        except:
            print("Export: .obj file could not be written.")

    STL_AUTO = 0
    STL_ASCII = 1
    STL_BINARY = 2

    @staticmethod
    def write_stl(model, export_filepath, mode=STL_ASCII):
        filename = os.path.split(export_filepath)[-1]

        if mode is Exporter.STL_ASCII:
            save_func = Exporter.__save_stl_ascii
        else:
            save_func = Exporter.__save_stl_binary

        with open(export_filepath, 'w') as fh:
            save_func(fh, filename, model)
            print(f'Export: {filename} successfully written.')

    @staticmethod
    def __save_stl_binary(fh, name, model):
        raise NotImplementedError

    @staticmethod
    def __save_stl_ascii(fh, name, model):
        fh.write(f'solid {name}\n')
        for i in range(len(model._faces)):
            face = model._faces[i]
            fh.write("facet normal %f %f %f\n" % tuple(face._norm[:3]))
            fh.write("  outer loop\n")
            for v_id in face._vids:
                fh.write("    vertex %f %f %f\n" % tuple(model._vertices[v_id][:3]))
            fh.write('  endloop\n')
            fh.write('endfacet\n')
            fh.write(f'endsolid {name}\n')

if __name__ == "__main__":
    import ObjLoader
    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data)

    obj_model.simplify()

    Exporter.write_obj(obj_model, './export/_cube.obj')
