import sys
from Model import Model
from Plane import Plane

def get_min_angle(vector, planes, exclude_planes):
    min_angle = sys.float_info.max
    min_idx = None
    for idx, plane in enumerate(planes):
        if plane not in exclude_planes:
            angle_between = plane.angle_between(vector)
            if angle_between < min_angle:
                min_idx = idx
                min_angle = angle_between
    return planes[min_idx]

def get_min_angle_plane(vector, planes):
    min_angle = sys.float_info.max
    min_idx = None
    for idx, plane in enumerate(planes):
        angle_between = plane.angle_between(vector)
        if angle_between > 0 and angle_between < min_angle:
            min_idx = idx
            min_angle = angle_between
    return planes[min_idx]

def calculate_offset_vertex(vertex, faces, thickness):
    # no connected faces
    if len(faces) == 0:
        return None
    # if only on face connected, offset along face normal
    elif len(faces) == 1:
        return vertex - faces[0]._norm * thickness[faces[0]._id]
    elif len(faces) == 2:
        # todo: enother special case
        return None
    else:
        planes = []
        for face in faces:
            planes.append(Plane(face.get_vertex(0) - face._norm * thickness[face._id], -face._norm))

        ref_plane = planes[0]
        ref_plane2 = get_min_angle_plane(planes[0]._norm, planes)

        intersection_line = ref_plane.intersect_with_plane(ref_plane2)
        if intersection_line is not None:
            ref_plane3 = get_min_angle(intersection_line[1], planes, [ref_plane, ref_plane2])
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
        offset_vertex = calculate_offset_vertex(vertex, connected_faces, thickness)
        shell_vertices.append(offset_vertex)

    # build the shell geometry
    shell = Model()
    for face, visible in list(zip(model._faces, visibility)): # important to duplicate the list as we are modifing it while reading from it
        if visible:
            model.add_face(reversed([shell_vertices[v_id] for v_id in face._vertex_ids]))
            shell.add_face([shell_vertices[v_id] for v_id in face._vertex_ids])
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