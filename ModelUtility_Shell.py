import sys
import VecMath as vm
from model import *
from primitives.Plane import Plane
import ObjExporter
from TimeIt import timeit

def get_first_plane(vertex, faces):
    """ First plane: Find the plane which center is closest to the vertex """
    min_dist = sys.float_info.max
    min_idx = None
    for idx, face in enumerate(faces):
        dist = vm.dist_point_to_point(vertex, face._center)
        if dist < min_dist:
            min_idx = idx
            min_dist = dist
    # print(f'ref_plane #1: {min_idx} -> ref: {faces[min_idx]._id}')
    return min_idx

def get_second_plane(vector, planes, exclude_planes):
    """ Second plane: Find the plane with the smallest angle between the normal vectors """
    min_angle = 0
    min_idx = None
    for idx, plane in enumerate(planes):
        if plane not in exclude_planes:
            angle_between = abs(plane.angle_between(vector))
            if angle_between > min_angle:
                min_idx = idx
                min_angle = angle_between
    # print(f'ref_plane #2: {min_idx} -> ref: {planes[min_idx]._ref_id}')
    return min_idx

def get_third_plane(vector, planes, exclude_planes):
    """ Thirst plane: Find the plane with the smallest angle with its normal and the ray-dir """
    min_angle = sys.float_info.max
    min_idx = None
    for idx, plane in enumerate(planes):
        if plane not in exclude_planes:
            angle_between = min(abs(plane.angle_between(vector)),abs(plane.angle_between(-vector)))
            if angle_between < min_angle:
                min_idx = idx
                min_angle = angle_between
    # print(f'ref_plane #3: {min_idx} -> ref: {planes[min_idx]._ref_id}')
    return min_idx

def calculate_offset_vertex(vertex, connected_faces, thickness):
    # no connected faces
    if len(connected_faces) == 0:
        return None
    # if only on face connected, offset along face normal
    elif len(connected_faces) == 1:
        return vertex - connected_faces[0]._norm * thickness[connected_faces[0]._id]
    elif len(connected_faces) == 2:
        # todo: enother special case
        raise RuntimeError("not implemented yet.")
    else:
        planes = []
        for face in connected_faces:
            planes.append(Plane(face.get_vertex(0) - face._norm * thickness[face._id], -face._norm, ref_id=face._id))

        ref_plane1 = planes[get_first_plane(vertex, connected_faces)]
        ref_plane2 = planes[get_second_plane(ref_plane1._norm, planes, [ref_plane1])]

        intersection_line = ref_plane1.intersect_with_plane(ref_plane2)
        if intersection_line is not None:
            ref_plane3 = planes[get_third_plane(intersection_line[1], planes, [ref_plane1, ref_plane2])]
            return ref_plane3.intersect_with_ray(intersection_line[0], intersection_line[1])

@timeit
def generate_shell(model, thickness, visibility):
    """ Duplicate a surface and offsets it by thickness"""
    if len(model._faces) != len(visibility):
        raise RuntimeError("visiblility config doesn't match face count")
    if len(model._faces) != len(thickness):
        raise RuntimeError("thickness config doesn't match face count")

    # generate the offset vertices
    shell_vertices = []
    for idx, vertex in enumerate(model._vertices):
        connected_faces = model.get_faces_with_vertex(idx)
        offset_vertex = calculate_offset_vertex(vertex, connected_faces, thickness)
        shell_vertices.append(offset_vertex)

    # build the shell geometry
    for face, visible in list(zip(model._faces, visibility)): # important to duplicate the list as we are modifing it while reading from it
        if visible:
            # model.add_face(reversed([shell_vertices[v_id] for v_id in face._vertex_ids]))
            model.add_face([shell_vertices[v_id] for v_id in face._vertex_ids], group=face._group)
        else:
            # remove face and close borders
            model.remove_face(face)
            for edge in face._edges:
                model.add_face([model._vertices[edge.v0_id], model._vertices[edge.v1_id], shell_vertices[edge.v1_id], shell_vertices[edge.v0_id]], group=face._group)

    model._update()

if __name__ == "__main__":

    obj_name = 'cube'

    import ObjReader
    obj_data = ObjReader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=40.)
    obj_model.simplify()

    thickness = [5.] * len(obj_model._faces)
    visibility = [True] * len(obj_model._faces)
    thickness[0] = .2 # bottom face is 'transparent'
    visibility[5] = False # top face is removed

    generate_shell(obj_model, thickness, visibility)

    ObjExporter.write(obj_model, f'./export/_{obj_name}_shell.obj')