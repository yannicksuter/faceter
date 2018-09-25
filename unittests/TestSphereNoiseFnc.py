import primitives
import ObjExporter
import numpy as np
import VecMath as vm
import MtxMath
import random
from euclid import euclid

def get_random_norm():
    d = euclid.Vector3(random.uniform(0, 1), random.uniform(0, 1), 0.).normalize()
    # d = euclid.Vector3(0., 0., 0.)
    # d.x = random.uniform(-1, 1)
    # d.y = random.uniform(-1, 1)
    # d.z = random.uniform(-1, 1)
    # d.z = 1.
    return d

if __name__ == "__main__":
    radius = 100.
    sphere = primitives.Sphere(radius)
    sphere_model = sphere.triangulate(recursion_level=3)

    l = min(sphere_model._faces[0]._edges[0].length, sphere_model._faces[0]._edges[1].length, sphere_model._faces[0]._edges[2].length)*.5

    for vertex in sphere_model._vertices:
        rnd_d = get_random_norm()
        # rnd_h = radius+random.uniform(0, 1)*radius*.1
        dir = vm.unit_vector(vertex)
        transf = MtxMath.conv_to_euclid(vm.rotate_fromto_matrix(np.array([0., 0., 1.]), dir))
        tv = transf * (rnd_d*euclid.Vector3(l,l,10))
        print(f'{vertex}/{vm.len(vertex)} -> {vertex + tv}/{vm.len(vertex+tv)}')
        vertex += tv

    # sphere_model.triangulate()
    ObjExporter.write(sphere_model, f'./export/_sphere_noise.obj')
