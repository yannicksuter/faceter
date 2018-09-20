import MtxMath
import VecMath
from euclid import euclid
import numpy as np
import svg
import model

def get_path_from_face(face):
    transform = MtxMath.conv_to_euclid(VecMath.rotate_fromto_matrix(face._norm, np.array([0., 0., 1.])))
    vertices = [transform * euclid.Point3(v[0], v[1], v[2]) for v in face._vertices]
    path = svg.Path.from_shape(svg.Shape([np.array([v[0], v[1]]) for v in vertices]))
    return path, transform

def get_path_from_faces(faces):
    if isinstance(faces, list):
        return get_path_from_face(faces[0])
    if isinstance(faces, model.Face):
        return get_path_from_face(faces)
    return False

def get_bbox_for_path(paths):
    """Returns the bounding box for a path or a list of paths"""
    if isinstance(paths, list):
        bbox = paths[0]._bbox
        for path in paths:
            bbox.combine(path._bbox)
        return bbox
    if isinstance(paths, svg.Path):
        return paths[0]._bbox
    return None