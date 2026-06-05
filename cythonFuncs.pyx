import cython
import numpy as np
cimport numpy as np

cpdef recolorImage(int[:, :] img, int rO, int gO, int bO,
    rM, gM, bM):
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
    cdef int N = img.shape[0]
    cdef int D = img.shape[1]

    output = np.zeros((N, D), dtype = int)
    for row in range(N):
        for col in range(D):
            v = img[row, col]
            output[row, col] = tuple(
                round(rO + rM * v),
                round(gO + gM * v),
                round(bO + bM * v)
            )
    
    return output