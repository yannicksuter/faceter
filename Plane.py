from VecMath import VecMath
import numpy as np

class Plane:
    def __init__(self, point, norm):
        """ Create a new plane from a point on the plane and it's normal """
        self._point = point
        self._norm = norm

    @classmethod
    def from_points(cls, p0, p1, p2, norm_dir = 1.):
        """ Create a plane from 3 points that span the plane """
        return Plane(p0, VecMath.unit_vector(np.cross(p1 - p0, p2 - p0) * norm_dir))

    def intersect_with_plane(self):
        # todo: implement
        pass

    def intersect_with_ray(self, ray_dir, ray_start, epsilon=1e-6):
        ndotu = self._norm.dot(ray_dir)
        if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or ray is within plane")

        w = ray_start - self._point
        si = -self._norm.dot(w) / ndotu
        return (w + si * ray_dir + self._point)

# if __name__ == "__main__":
    # todo:
