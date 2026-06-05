from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "main",
        ["main.pyx"],
        extra_compile_args = ["-O3"],
        extra_link_args = ["-O3"]
    ),
    Extension(
        "helpers",
        ["helpers.pyx"],
        extra_compile_args = ["-O3"],
        extra_link_args = ["-O3"]
    )
]

setup(
    ext_modules = cythonize(
        extensions,
        compiler_directives = {
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False
        }
    ),
    include_dirs=[numpy.get_include()]
)