from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


ext = Extension(
    "wrap",
    ["wrap.pyx"],
    language="c++",
    include_dirs=[".."], 
    library_dirs=[".."],
    libraries=["ExampleLib"],
)

setup(
  name = 'Hello world app',
  cmdclass = {'build_ext': build_ext},
  ext_modules = [ext]
)

