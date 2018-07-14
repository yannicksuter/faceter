import os, datetime
import numpy as np
from VecMath import VecMath
from Model import *

def write_obj_vertices(file, model, vertex_offset):
    """Write vertices to obj file"""
    file.write(f'\n')
    for vert in model._vertices:
        v = vert.copy()
        if vertex_offset is not None:
            v += vertex_offset
        file.write('v %.4f %.4f %.4f\n' % tuple(v[:3]))

def write_obj_normals(file, model):
    """Write vertex normals to obj file"""
    file.write(f'\n')
    for face in model._faces:
        file.write('vn %.4f %.4f %.4f\n' % tuple(face._norm[:3]))

def write_obj_facegroup(file, model, group):
    file.write(f'\ng {group._name}\n')
    for face_id, face in enumerate(group._faces):
        tags = f'# {", ".join(face._tags)}\n' if len(face._tags) > 0 else ''
        file.write(tags + 'f ' + ' '.join([f'{vertex_id+1}//{face._id+1}' for vertex_id in face._vertex_ids]) + '\n')

class Exporter:
    def __init__(self, model, export_filepath):
        pass

    @staticmethod
    def rotate_model(model, from_vec, to_vec=np.array([0., 0., -1.])):
        rot_mtx = VecMath.get_rotation_matrix(from_vec, to_vec)
        for vid in range(len(model._vertices)):
            vert = (rot_mtx.__matmul__(model._vertices[vid]))[0,:]
            model._vertices[vid] = np.asarray(vert).reshape(-1)

    @staticmethod
    def translate(model, v): #ref_vec, to_vec=np.array([0., 0., 0.])):
        for idx, vertex in enumerate(model._vertices):
            model._vertices[idx] = np.array(vertex+v)

    @staticmethod
    def write_obj(model, export_filepath, offset=None):
        try:
            path, filename = os.path.split(export_filepath)
            with open(export_filepath, 'w') as obj_export:
                obj_export.write(f'# {filename}\n#\n')
                write_obj_vertices(obj_export, model, offset)
                write_obj_normals(obj_export, model)
                for group in model._groups:
                    write_obj_facegroup(obj_export, model, group)
                print(f'Export: {filename} written. (Vertices: {len(model._vertices)} Faces: {len(model._faces)})')
        except:
            print(f'Export: {export_filepath} file could not be written.')

    @staticmethod
    def write_obj_split(model, export_filepath, offset=None):
        try:
            path, filename = os.path.split(export_filepath)
            filename, ext = os.path.splitext(filename)

            for group in model._groups:
                filename_group = os.path.join(path, f'{filename}_{group._name}{ext}')
                with open(filename_group, 'w') as obj_export:
                    obj_export.write(f'# {filename}\n#\n')
                    write_obj_vertices(obj_export, model, offset)
                    write_obj_normals(obj_export, model)
                    write_obj_facegroup(obj_export, model, group)
                    print(f'Export: {filename_group} written. (Vertices: {len(model._vertices)} Faces: {len(group._faces)})')
        except:
            print(f'Export: {export_filepath} file could not be written.')

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
            for v_id in face._vertex_ids:
                fh.write("    vertex %f %f %f\n" % tuple(model._vertices[v_id][:3]))
            fh.write('  endloop\n')
            fh.write('endfacet\n')
            fh.write(f'endsolid {name}\n')

if __name__ == "__main__":
    import ObjLoader
    obj_data = ObjLoader.ObjLoader('./example/cube.obj')
    obj_model = Model.load_fromdata(obj_data)

    obj_model.simplify()

    obj_model.add_group('cube2')
    for face in list(obj_model._faces):
        vertices = []
        for idx in face._vertex_ids:
            vertices.append(obj_model._vertices[idx] + obj_model.get_size())
        obj_model.add_face(vertices)

    Exporter.write_obj(obj_model, './export/_cube.obj')
    Exporter.write_obj_split(obj_model, './export/_cube.obj')
