from Model import Model
from Plane import Plane

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
        intersection_line = ref_plane.intersect_with_plane(planes[1])
        if intersection_line is not None:
            return planes[2].intersect_with_ray(intersection_line[0], intersection_line[1])

def generate_shell(model, thickness, visibility):
    """ Duplicate a surface and offsets it by thickness"""
    shell_vertices = []

    # generate the offset vertices
    for idx, vertex in enumerate(model._vertices):
        connected_faces = model.get_faces_with_vertex_id(idx)
        offset_vertex = calculate_offset_vertex(vertex, connected_faces, thickness)
        shell_vertices.append(offset_vertex)

    # build the shell geometry
    for face, visible in list(zip(model._faces, visibility)): # important to duplicate the list as we are modifing it while reading from it
        if visible:
            model.add_face(reversed([shell_vertices[v_id] for v_id in face._vertex_ids]))
        else:
            # remove face and close borders
            model.remove_face(face)
            for edge in face._edges:
                model.add_face([model._vertices[edge.v0_id], model._vertices[edge.v1_id], shell_vertices[edge.v1_id], shell_vertices[edge.v0_id]])
    return model

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