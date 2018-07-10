import numpy as np

def get_translation_mtx(v):
    return np.matrix('{} {} {} {}; {} {} {} {}; {} {} {} {}; {} {} {} {}'.format(1, 0, 0, v[0], 0, 1, 0, v[1], 0, 0, 1, v[2], 0, 0, 0, 1))