# obj/wavefront specs: http://paulbourke.net/dataformats/obj/

def catch(func, handle=lambda e : e, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # return handle(e)
        return None

class ObjLoader(object):
    def __init__(self, fileName):
        print(f'Loading {fileName} ...')

        self._vertices = []
        self._normals = []
        self._texture_coords = []
        self._groups = []
        self._faces = None

        try:
            with open(fileName) as f:
                for line in f:
                    line = self.__remove_comments(line)
                    if line[:2] == "g ":
                        group_name = line[2:].strip()
                        if len(group_name) == 0:
                            group_name = "default"
                        self._faces = []
                        self._groups.append((group_name, self._faces))

                    if line[:2] == "v ":
                        vertex = [t(s) for t, s in zip((float, float, float), line[2:].split())]
                        self._vertices.append(vertex)

                    if line[:3] == "vn ":
                        normal = [t(s) for t, s in zip((float, float, float), line[3:].split())]
                        self._normals.append(normal)

                    if line[:3] == "vt ":
                        texture = [t(s) for t, s in zip((float, float), line[3:].split()[:2])]
                        self._texture_coords.append(texture)

                    elif line[:2] == "f ":
                        if len(self._groups) == 0:
                            # if no group was defined, create a default container
                            self._faces = []
                            self._groups.append(("default", self._faces))

                        face = []
                        for i in line[2:].split():
                            f_vertice = tuple([catch(lambda: int(idx)) for idx in i.split('/')])
                            face.append(f_vertice)
                        self._faces.append(face)
        except IOError:
            print(f'Error loading {fileName}. File not found.')

    def load_material_library(self, path, filename):
        material = None
        file = self.open_material_file(filename)

        for line in file:
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'newmtl':
                material = Material(values[1])
                self.materials[material.name] = material
            elif material is None:
                logging.warn('Expected "newmtl" in %s' % filename)
                continue

            try:
                if values[0] == 'Kd':
                    material.diffuse = map(float, values[1:])
                elif values[0] == 'Ka':
                    material.ambient = map(float, values[1:])
                elif values[0] == 'Ks':
                    material.specular = map(float, values[1:])
                elif values[0] == 'Ke':
                    material.emissive = map(float, values[1:])
                elif values[0] == 'Ns':
                    material.shininess = float(values[1])
                elif values[0] == 'd':
                    material.opacity = float(values[1])
                elif values[0] == 'map_Kd':
                    try:
                        material.texture = pyglet.resource.image(values[1]).texture
                    except BaseException as ex:
                        logging.warn('Could not load texture %s: %s' % (values[1], ex))
            except BaseException as ex:
                logging.warn('Parse error in %s.' % (filename, ex))

    def __remove_comments(self, line):
        try:
            return line[0:line.index('#')]
        except:
            return line

if __name__ == "__main__":
    obj_data = ObjLoader(f'./example/tri_strip.obj')
    print(f'Vertices: {len(obj_data._vertices)}')
    print(f'Faces: {len(obj_data._faces)}')
    print(f'Groups: {len(obj_data._groups)}')
