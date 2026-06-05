import cython
import numpy as np
cimport numpy as np

 
cpdef recolorImage(np.ndarray[char, ndim=2] img, char rO, char gO, char bO,
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
    cdef char row, col, v
    cdef char N = img.shape[0]
    cdef char D = img.shape[1]

    output = np.empty((N, D), dtype = (int, 3))
    for row in range(N):
        for col in range(D):
            v = img[row, col]
            output[row, col] = tuple(
                [rO + rM * v,
                gO + gM * v,
                bO + bM * v]
            )
    
    return output