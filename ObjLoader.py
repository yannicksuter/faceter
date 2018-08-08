# obj/wavefront specs: http://paulbourke.net/dataformats/obj/
import os, logging
import model

def catch(func, handle=lambda e : e, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # return handle(e)
        return None

class MaterialGroup(object):
    def __init__(self, material):
        self._material = material
        self._faces = []

class Mesh(object):
    def __init__(self, name):
        self._name = name
        self._groups = []

class ObjLoader(object):
    def __init__(self, filename):
        print(f'Loading {filename} ...')

        self._vertices = []
        self._normals = []
        self._texture_coords = []

        self._meshes = {}
        self._materials = {}

        mesh = None
        group = None
        material = None

        try:
            with open(filename) as f:
                for line in f:
                    line = self.__remove_comments(line)
                    if line.startswith('#'):
                        continue
                    values = line.split()
                    if not values:
                        continue

                    if values[0] == 'g':
                        mesh = Mesh(values[1])
                        self._meshes[mesh._name] = mesh
                        group = None
                    if values[0] == 'o':
                        mesh = Mesh(values[1])
                        self._meshes[mesh._name] = mesh
                        group = None
                    elif values[0] == 'mtllib':
                        path, filename = os.path.split(filename)
                        self.load_material_library(os.path.join(path, values[1]))
                    elif values[0] in ('usemtl', 'usemat'):
                        material = self._materials.get(values[1], None)
                        if material is None:
                            logging.warning('Unknown material: %s' % values[1])
                        if mesh is not None:
                            group = MaterialGroup(material)
                            mesh.groups.append(group)
                    elif values[0] == 'v':
                        vertex = list(map(float, values[1:4]))
                        self._vertices.append(vertex)
                    elif values[0] == 'vn':
                        normal = list(map(float, values[1:4]))
                        self._normals.append(normal)
                    elif values[0] == 'vt':
                        texcoords = list(map(float, values[1:3]))
                        self._texture_coords.append(texcoords)
                    elif values[0] == 'f':
                        if mesh is None:
                            mesh = Mesh('')
                            self.mesh_list.append(mesh)
                        if material is None:
                            material = model.Material("<unknown>")
                        if group is None:
                            group = MaterialGroup(material)
                            mesh._groups.append(group)

                        face = []
                        for i in line[2:].split():
                            f_vertice = tuple([catch(lambda: int(idx)) for idx in i.split('/')])
                            face.append(f_vertice)
                        group._faces.append(face)
        except IOError:
            print(f'Error loading {filename}. File not found.')

    def load_material_library(self, filename):
        material = None
        file = self.open_material_file(filename)
        for line in file:
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'newmtl':
                material = model.Material(values[1])
                self._materials[material._name] = material
            elif material is None:
                logging.warning('Expected "newmtl" in %s' % filename)
                continue

            try:
                if values[0] == 'Kd':
                    material._diffuse = map(float, values[1:])
                elif values[0] == 'Ka':
                    material._ambient = map(float, values[1:])
                elif values[0] == 'Ks':
                    material._specular = map(float, values[1:])
                elif values[0] == 'Ke':
                    material._emissive = map(float, values[1:])
                elif values[0] == 'Ns':
                    material._shininess = float(values[1])
                elif values[0] == 'd':
                    material._opacity = float(values[1])
                elif values[0] == 'map_Kd':
                    material._texture = values[1]
            except BaseException as ex:
                logging.warning('Parse error in %s.' % (filename, ex))

    def __remove_comments(self, line):
        try:
            return line[0:line.index('#')]
        except:
            return line

if __name__ == "__main__":
    obj_data = ObjLoader(f'./example/cube.obj')
    print(f'Vertices: {len(obj_data._vertices)}')
    print(f'Normals: {len(obj_data._vertices)}')
    print(f'TexCoords: {len(obj_data._texture_coords)}')
    print(f'Meshes: {len(obj_data._meshes)}\n')
    for mesh_idx, mesh in enumerate(obj_data._meshes.values()):
        print(f'mesh[{mesh_idx}]: {mesh._name}')
        for group_idx, group in enumerate(mesh._groups):
            print(f'\tgroup[{group_idx}]: material: {group._material._name} faces: {len(group._faces)}')