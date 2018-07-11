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

        self.vertices = []
        self.normals = []
        self.texture_coords = []
        self.groups = []
        self.faces = None

        try:
            with open(fileName) as f:
                for line in f:
                    if line[:2] == "g ":
                        group_name = line[2:].strip()
                        if len(group_name) == 0:
                            group_name = "default"
                        self.faces = []
                        self.groups.append((group_name, self.faces))

                    if line[:2] == "v ":
                        vertex = [t(s) for t, s in zip((float, float, float), line[2:].split())]
                        self.vertices.append(vertex)

                    if line[:3] == "vn ":
                        normal = [t(s) for t, s in zip((float, float, float), line[3:].split())]
                        self.normals.append(normal)

                    if line[:3] == "vt ":
                        texture = [t(s) for t, s in zip((float, float), line[3:].split()[:2])]
                        self.texture_coords.append(texture)

                    elif line[:2] == "f ":
                        if len(self.groups) == 0:
                            # if no group was defined, create a default container
                            self.faces = []
                            self.groups.append(("default", self.faces))

                        face = []
                        for i in line[2:].split():
                            f_vertice = tuple([catch(lambda: int(idx)) for idx in i.split('/')])
                            face.append(f_vertice)
                        self.faces.append(face)
        except IOError:
            print(".obj file not found.")