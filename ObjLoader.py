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
