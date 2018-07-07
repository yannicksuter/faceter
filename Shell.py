import sys
from VecMath import VecMath as vm
from Model import Model
from Plane import Plane

def get_first_plane(vertex, faces):
    min_dist = sys.float_info.max
    min_idx = None
    for idx, face in enumerate(faces):
        dist = vm.dist_point_to_point(vertex, face._center)
        if dist < min_dist:
            min_idx = idx
            min_dist = dist
    print(f'ref_plane #1: {min_idx}')
    return min_idx

def get_second_plane(vector, planes, exclude_planes, epsilon=1e-6):
    min_angle = sys.float_info.max
    min_idx = None
    for idx, plane in enumerate(planes):
        if plane not in exclude_planes:
            angle_between = plane.angle_between(vector)
            if angle_between > epsilon and angle_between < min_angle:
                min_idx = idx
                min_angle = angle_between
    print(f'ref_plane #2: {min_idx}')
    return planes[min_idx]

def get_third_plane(vector, planes, exclude_planes):
    min_angle = sys.float_info.max
    min_idx = None
    for idx, plane in enumerate(planes):
        if plane not in exclude_planes:
            angle_between = plane.angle_between(vector)
            if angle_between < min_angle:
                min_idx = idx
                min_angle = angle_between
    print(f'ref_plane #3: {min_idx}')
    return planes[min_idx]

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
            planes.append(Plane(face.get_vertex(0) - face._norm * thickness[face._id], -face._norm))

        ref_plane1 = planes[get_first_plane(vertex, connected_faces)]
        ref_plane2 = get_second_plane(ref_plane1._norm, planes, [ref_plane1])

        intersection_line = ref_plane1.intersect_with_plane(ref_plane2)
        if intersection_line is not None:
            ref_plane3 = get_third_plane(intersection_line[1], planes, [ref_plane1, ref_plane2])
            return ref_plane3.intersect_with_ray(intersection_line[0], intersection_line[1])

def generate_shell(model, thickness, visibility):
    """ Duplicate a surface and offsets it by thickness"""
    if len(model._faces) != len(visibility):
        raise RuntimeError("visiblility config doesn't match face count")
    if len(model._faces) != len(thickness):
        raise RuntimeError("thickness config doesn't match face count")

    # generate the offset vertices
    shell_vertices = []
    for idx, vertex in enumerate(model._vertices):
        connected_faces = model.get_faces_with_vertex_id(idx)
        print(f'vertex[{idx}]: {len(connected_faces)} connected faces')
        offset_vertex = calculate_offset_vertex(vertex, connected_faces, thickness)
        shell_vertices.append(offset_vertex)

    # build the shell geometry
    shell = Model()
    for face, visible in list(zip(model._faces, visibility)): # important to duplicate the list as we are modifing it while reading from it
        if visible:
            # model.add_face(reversed([shell_vertices[v_id] for v_id in face._vertex_ids]))
            model.add_face([shell_vertices[v_id] for v_id in face._vertex_ids])
            shell.add_face([shell_vertices[v_id].copy() for v_id in face._vertex_ids])
        else:
            # remove face and close borders
            model.remove_face(face)
            for edge in face._edges:
                model.add_face([model._vertices[edge.v0_id], model._vertices[edge.v1_id], shell_vertices[edge.v1_id], shell_vertices[edge.v0_id]])
    return shell

if __name__ == "__main__":

    obj_name = 'cube'

    import ObjLoader
    obj_data = ObjLoader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=40.)
    obj_model.simplify()

    thickness = [5.] * len(obj_model._faces)
    visibility = [True] * len(obj_model._faces)
    thickness[0] = .2 # bottom face is 'transparent'
    visibility[5] = False # top face is removed

    obj_shell = generate_shell(obj_model, thickness, visibility)

    if obj_shell:
        from Exporter import Exporter
        Exporter.write_obj(obj_shell, f'./export/_{obj_name}_shell.obj')