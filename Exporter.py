import os
import numpy as np
from VecMath import VecMath
from model import *

def rotate_model(model, from_vec, to_vec=np.array([0., 0., -1.])):
    rot_mtx = VecMath.get_rotation_matrix(from_vec, to_vec)
    for vid in range(len(model._vertices)):
        vert = (rot_mtx.__matmul__(model._vertices[vid]))[0,:]
        model._vertices[vid] = np.asarray(vert).reshape(-1)

def translate(model, v): #ref_vec, to_vec=np.array([0., 0., 0.])):
    for idx, vertex in enumerate(model._vertices):
        model._vertices[idx] = np.array(vertex+v)

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
        try:
            file.write('vn %.4f %.4f %.4f\n' % tuple(face._norm[:3]))
        except:
            pass

def write_obj_facegroup(file, model, group):
    file.write(f'\ng {group._name}\n')

    if group._material:
        file.write(f'usemtl {group._material._name}\n')

    for face_id, face in enumerate(group._faces):
        tags = f'# {", ".join(face._tags)}\n' if len(face._tags) > 0 else ''
        file.write(tags + 'f ' + ' '.join([f'{vertex_id+1}//{face._id+1}' for vertex_id in face._vertex_ids]) + '\n')

def write_material_library(model, path, filename):
    mtl_filename = f'{os.path.splitext(filename)[0]}.mtl'

    with open(os.path.join(path, mtl_filename), 'w') as mtl_file:
        mtl_file.write(f'# {mtl_filename}\n')

        for group in model._groups:
            if group._material:
                mtl_file.write(f'\nnewmtl {group._material._name}\n')
                mtl_file.write(f'Kd {group._material._diffuse[0]} {group._material._diffuse[1]} {group._material._diffuse[2]}\n')
                mtl_file.write(f'Ka {group._material._ambient[0]} {group._material._ambient[1]} {group._material._ambient[2]}\n')
                mtl_file.write(f'Ks {group._material._specular[0]} {group._material._specular[1]} {group._material._specular[2]}\n')
                mtl_file.write(f'Ns {group._material._shininess}\n')
                mtl_file.write(f'd {group._material._opacity}\n')

                if group._material._texture:
                    mtl_file.write(f'map_Kd {group._material._texture}\n')

    print(f'{mtl_filename} written.')
    return mtl_filename

def write_obj(model, export_filepath, offset=None):
    try:
        path, filename = os.path.split(export_filepath)

        mtl_filename = write_material_library(model, path, filename)

        with open(export_filepath, 'w') as obj_export:
            obj_export.write(f'# {filename}\n#\n')
            obj_export.write(f'mtllib {mtl_filename}\n')
            write_obj_vertices(obj_export, model, offset)
            write_obj_normals(obj_export, model)
            for group in model._groups:
                write_obj_facegroup(obj_export, model, group)
            print(f'{filename} written. (Vertices: {len(model._vertices)} Faces: {len(model._faces)})')
    except:
        print(f'Export: {export_filepath} file could not be written.')

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
