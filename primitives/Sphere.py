import model
import math
from euclid import euclid


class Sphere:
    def __init__(self, radius, center=euclid.Vector3(0.,0.,0.)):
        self._center = euclid.Vector3(center[0], center[1], center[2])
        self._radius = radius

    def triangulate(self, iterations):
        return model.Model()