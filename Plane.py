from VecMath import VecMath
import numpy as np
from VecMath import VecMath as vm


class Plane:
    def __init__(self, point, norm, ref_id=None):
        """ Create a new plane from a point on the plane and it's normal """
        self._ref_id = ref_id
        self._point = point
        self._norm = norm
        self._d = -(np.dot(self._norm, self._point))

    @classmethod
    def from_points(cls, p0, p1, p2, norm_dir = 1.):
        """ Create a plane from 3 points that span the plane """
        return Plane(p0, VecMath.unit_vector(np.cross(p1 - p0, p2 - p0) * norm_dir))

    def angle_between(self, other):
        """ Return the angle in radians between this plane and another plane or vector """
        if isinstance(other, Plane):
            other_v = other._norm
        elif len(other) == 3:
        # elif isinstance(other, np.array) and len(other) == 3:
            other_v = other
        return VecMath.angle_between(self._norm, other_v)

    def intersect_with_plane(self, other_plane, epsilon=1e-6):
        """Finds the intersection of this plane with another plane. """
        if isinstance(other_plane, Plane):
            u = np.cross(self._norm, other_plane._norm)
            u_abs = np.abs(u)

            if np.linalg.norm(u_abs) < epsilon:
                # the planes are parallel and do not intersect
                return None

            max_value = np.amax(u_abs)
            max_id = list(u_abs).index(max_value)
            p = np.array([0., 0., 0.])
            if max_id == 0:
                p[vm._Y] = (other_plane._d * self._norm[vm._Z] - self._d * other_plane._norm[vm._Z]) / u[vm._X]
                p[vm._Z] = (self._d * other_plane._norm[vm._Y] - other_plane._d * self._norm[vm._Y]) / u[vm._X]
            elif max_id == 1:
                p[vm._X] = (self._d * other_plane._norm[vm._Z] - other_plane._d * self._norm[vm._Z]) / u[vm._Y]
                p[vm._Z] = (other_plane._d * self._norm[vm._X] - self._d * other_plane._norm[vm._X]) / u[vm._Y]
            else:
                p[vm._X] = (other_plane._d * self._norm[vm._Y] - self._d * other_plane._norm[vm._Y]) / u[vm._Z]
                p[vm._Y] = (self._d * other_plane._norm[vm._X] - other_plane._d * self._norm[vm._X]) / u[vm._Z]

            return [p, u]
        return None

    def intersect_with_ray(self, ray_start, ray_dir, epsilon=1e-6):
        ndotu = self._norm.dot(ray_dir)
        if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or ray is within plane")

        w = ray_start - self._point
        si = -self._norm.dot(w) / ndotu
        return (w + si * ray_dir + self._point)

# if __name__ == "__main__":
    # todo:
