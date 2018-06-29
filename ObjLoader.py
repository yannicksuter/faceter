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
        self.faces = []
        ##
        try:
            f = open(fileName)
            for line in f:
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
                    face = []
                    for i in line[2:].split():
                        f_vertice = tuple([catch(lambda: int(idx)) for idx in i.split('/')])
                        face.append(f_vertice)
                    self.faces.append(face)

            f.close()
        except IOError:
            print(".obj file not found.")