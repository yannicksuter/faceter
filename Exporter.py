import os
import numpy as np
from VecMath import VecMath
import MtxMath
from euclid import euclid

def write_obj_vertices(file, model, transform):
    """Write vertices to obj file"""
    file.write(f'\n')
    for v in model._vertices:
        vertex = transform * euclid.Point3(v[0], v[1], v[2])
        file.write('v %.4f %.4f %.4f\n' % tuple(vertex[:3]))

def write_obj_normals(file, model, transform):
    """Write vertex normals to obj file"""
    file.write(f'\n')
    for face in model._faces:
        n = transform * euclid.Point3(face._norm[0], face._norm[1], face._norm[2]).normalized()
        file.write('vn %.4f %.4f %.4f\n' % tuple(n[:3]))

def write_obj_facegroup(file, group):
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

def write_obj(model, export_filepath, transform=None):
    try:
        path, filename = os.path.split(export_filepath)
        mtl_filename = write_material_library(model, path, filename)

        if transform == None:
            transform = euclid.Matrix4.new_identity()

        with open(export_filepath, 'w') as obj_export:
            obj_export.write(f'# {filename}\n#\n')
            obj_export.write(f'mtllib {mtl_filename}\n')
            write_obj_vertices(obj_export, model, transform)
            write_obj_normals(obj_export, model, transform)
            for group in model._groups:
                write_obj_facegroup(obj_export, group)
            print(f'{filename} written. (Vertices: {len(model._vertices)} Faces: {len(model._faces)})')
    except:
        print(f'Export: {export_filepath} file could not be written.')

def write_obj_split(model, export_filepath, transform=None):
    try:
        path, filename = os.path.split(export_filepath)
        filename, ext = os.path.splitext(filename)

        if transform == None:
            transform = euclid.Matrix4.new_identity()

        for group in model._groups:
            filename_group = os.path.join(path, f'{filename}_{group._name}{ext}')
            with open(filename_group, 'w') as obj_export:
                obj_export.write(f'# {filename}\n#\n')
                write_obj_vertices(obj_export, model, transform)
                write_obj_normals(obj_export, model, transform)
                write_obj_facegroup(obj_export, group)
                print(f'Export: {filename_group} written. (Vertices: {len(model._vertices)} Faces: {len(group._faces)})')
    except:
        print(f'Export: {export_filepath} file could not be written.')

def write(model, filename, orientation_vec=None):
    """Rotate and center object to lay flat ob the heat-bead"""
    model._update()

    if orientation_vec is None:
        transform = euclid.Matrix4.new_translate(-model._center[0], -model._center[1], -model._center[2])
    else:
        transform = MtxMath.conv_to_euclid(VecMath.rotate_fromto_matrix(orientation_vec, np.array([0., 0., -1.])))
        n = transform * euclid.Point3(-model._center[0], -model._center[1], -model._center[2])
        transform = euclid.Matrix4.new_translate(n.x, n.y, n.z) * transform

    write_obj(model, filename, transform=transform)
