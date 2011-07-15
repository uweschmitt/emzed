from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


ext = Extension(
    "_pyOpenMS",
    #sources = [ "helpers.cpp", "wrap.pyx", ],
    sources = [ "pyOpenMS.pyx", ],
    language="c++",
    include_dirs=["e:/OpenMS-1.8/include", 
                  "e:/OpenMS-1.8/contrib_build/include",
                  r"C:\QtSDK\Desktop\Qt\4.7.3\msvc2008\include",
                 ],
    library_dirs=["e:/OpenMS-1.8_BUILD"],
    libraries=["OpenMS"],
)

setup(
  name = 'minimal open ms wrapper',
  cmdclass = {'build_ext': build_ext},
  ext_modules = [ext]
)

