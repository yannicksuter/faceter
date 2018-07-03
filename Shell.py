from Model import Model
from Plane import Plane

def calculate_offset_vertex(vertex, faces, thickness):
    # no connected faces
    if len(faces) == 0:
        return None
    # if only on face connected, offset along face normal
    elif len(faces) == 1:
        return vertex - faces[0]._norm * thickness[faces[0]._id]
    else:
        planes = []
        for idx, face in enumerate(faces):
            planes.append(Plane(face.get_vertex(0) - face._norm * thickness[face._id],
                                face.get_vertex(1) - face._norm * thickness[face._id],
                                face.get_vertex(2) - face._norm * thickness[face._id],
                                -face._norm))
        #todo: calculate plane intersection
        return None

def generate_shell(model, thickness):
    """ Duplicate a surface and offsets it by thickness"""
    shell_vertices = []

    # generate the offset vertices
    for v_id in range(len(model._vertices)):
        connected_faces = model.get_faces_with_vertex_id(v_id)
        offset_vertex = calculate_offset_vertex(model._vertices[v_id], connected_faces, thickness)
        shell_vertices.append(offset_vertex)

    # todo: build the shell geometry

    # todo: merge into model

    return None

if __name__ == "__main__":

    obj_name = 'cube'

    import ObjLoader
    obj_data = ObjLoader.ObjLoader(f'./example/{obj_name}.obj')
    obj_model = Model.load_fromdata(obj_data, scale=100.)
    obj_model.simplify()

    # thickness = [0. if i == 0. else 10 for i in range(len(obj_model._faces))]
    thickness = [10.] * len(obj_model._faces)
    obj_shell = generate_shell(obj_model, thickness)

    if obj_shell:
        from Exporter import Exporter
        Exporter.write_obj(obj_shell, f'./export/_{obj_name}_shell.obj')