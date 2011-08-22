from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


def ext(name, sources):
        return Extension(
            name,
            #sources = [ "wrap.pyx", ],
            sources = sources,
            language="c++",
            include_dirs=["e:/OpenMS-1.8/include", 
                          "e:/OpenMS-1.8/contrib_build/include",
                          r"C:\QtSDK\Desktop\Qt\4.7.3\msvc2008\include",
                          r"C:\QtSDK\Desktop\Qt\4.7.3\msvc2008\include\QtCore",
                         ],
            library_dirs=["e:/OpenMS-1.8_BUILD", r"e:\OpenMS-1.8\contrib_build\lib",
    r"c:/QtSDK/Desktop/Qt/4.7.3/msvc2008/lib"],
            libraries=["OpenMS", "xerces-c_3", "QtCore4"],
        )
    

ext_modules = []
ext_modules.append(ext("_pyOpenMS", ["pyOpenMS.pyx"]))

setup(
  name = 'minimal open ms wrapper',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)

