class Edge:
    def __init__(self, idx0, idx1, v0, v1):
        self._idx0 = idx0
        self._v0= v0
        self._idx1 = idx1
        self._v1= v1
        A = (v0[1] - v1[1])
        B = (v1[0] - v0[0])
        C = (v0[0] * v1[1] - v1[0] * v0[1])
        self._line = A, B, -C

    @classmethod
    def ray(cls, p, dir):
        return cls(None, None, p, p+dir)

    def __intersect_line(self, other):
        D = self._line[0] * other._line[1] - self._line[1] * other._line[0]
        Dx = self._line[2] * other._line[1] - self._line[1] * other._line[2]
        Dy = self._line[0] * other._line[2] - self._line[2] * other._line[0]
        if D != 0:
            x = Dx / D
            y = Dy / D
            return x, y
        else:
            return False

    def intersect(self, other):
        pt = self.__intersect_line(other)
        print(pt)
        if pt:
            return (pt[0] >= self._v0[0] and pt[0] <= self._v1[0])
        return False
