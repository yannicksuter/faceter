import numpy as np

class BoundingBox:
    def __init__(self):
        self._min = np.array([0., 0.])
        self._max = np.array([0., 0.])

    @classmethod
    def from_vertices(cls, vertices):
        cls = BoundingBox()
        cls._min = vertices[0].copy()
        cls._max = vertices[0].copy()
        for vertex in vertices:
            cls._min[0] = min(cls._min[0], vertex[0])
            cls._min[1] = min(cls._min[1], vertex[1])
            cls._max[0] = max(cls._max[0], vertex[0])
            cls._max[1] = max(cls._max[1], vertex[1])
        return cls

    @classmethod
    def from_other(cls, other):
        cls = BoundingBox()
        cls._min = other._min.copy()
        cls._max = other._max.copy()
        return cls

    def is_inside(self, other):
        """Check if bounding box is inside the other bounding box."""
        if isinstance(other, BoundingBox):
          if all(m_s >= m_o for m_s,m_o in zip(self._min, other._min)) and all(m_s <= m_o for m_s,m_o in zip(self._max, other._max)):
              return True
        return False

    def expand(self, w, h):
        self._min[0] -= w
        self._min[1] -= h
        self._max[0] += w
        self._max[1] += h
        return self

    def combine(self, other):
        if isinstance(other, BoundingBox):
            self._min = np.minimum(self._min, other._min)
            self._max = np.maximum(self._max, other._max)

    @property
    def _size(self):
        """Get size of bounding box."""
        return np.absolute(self._max - self._min)
