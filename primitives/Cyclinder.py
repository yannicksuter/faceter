from model import Model

class Cylinder:
    def __init__(self, radius, height):
        self._radius = radius
        self._height = height

    def triangulate(self, sides):
        return Model()