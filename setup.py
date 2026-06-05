from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules = cythonize("cythonFuncs.pyx", compiler_directives = {
        "boundscheck": False,
        "wraparound": False
    }, extra_compile_args=["-O3"]),
    include_dirs=[numpy.get_include()]
)