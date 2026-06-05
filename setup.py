from setuptools import setuptools
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("main.pyx")
)