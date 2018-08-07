class Material:
    _diffuse = [.8, .8, .8]
    _ambient = [.2, .2, .2]
    _specular = [0., 0., 0.]
    _emission = [0., 0., 0.]
    _shininess = 0.
    _opacity = 1.
    _texture = None

    def __init__(self, name):
        self._name = name

    def __eq__(self, other):
        if self._texture is None:
            return super(Material, self).__eq__(other)
        return (self.__class__ is other.__class__ and
                self._texture == other._texture)

    def __hash__(self):
        if self._texture is None:
            return super(Material, self).__hash__()
        return hash(self._texture)
