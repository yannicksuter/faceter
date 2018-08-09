from euclid import euclid

def conv_to_euclid(np_m):
    m = euclid.Matrix4.new_identity()
    m.a = np_m.item((0,0))
    m.b = np_m.item((0,1))
    m.c = np_m.item((0,2))
    m.e = np_m.item((1,0))
    m.f = np_m.item((1,1))
    m.g = np_m.item((1,2))
    m.i = np_m.item((2,0))
    m.j = np_m.item((2,1))
    m.k = np_m.item((2,2))
    return m
