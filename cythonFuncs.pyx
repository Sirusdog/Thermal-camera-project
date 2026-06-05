import cython
import numpy as np
cimport numpy as np
from cython.parallel cimport prange


 
cpdef recolorImage(np.ndarray[int, ndim=2] img, int rO, int gO, int bO,
    char rM, char gM, char bM):
    """
    Recolors 8 bit images based on modes for rM, gM and bM.
    
    Inputs:
    img : 2D numpy array in grayscale.
    rO, gO, bO : The constants to add/take away from the grascale value,
        i.e rO, gO, bO = 0, means the image will be white-hot, 
        rO, gO, = 0, bO = 255 means the image will be blue-cold.
    rM, gM, bM : The value to multiply the inputs by. Currently only works with
        -1, 0, 1.
    """
    cdef int row, col, v
    cdef int r, g, b
    cdef short N = img.shape[0]
    cdef short D = img.shape[1]

    output = np.empty((N, D), dtype = (int, 3))
    for row in prange(N, nogil = True):
        for col in range(D):
            v = img[row, col]
            r = rO + v
            g = rO + v
            b = bO + v
            output[row, col] = (r, g, b)
    
    return output