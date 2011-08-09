#input-encoding: utf-8
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True


import glob, os



library_dirs=["e:/OpenMS-1.8_BUILD", r"e:\OpenMS-1.8\contrib_build\lib",
              r"c:/QtSDK/Desktop/Qt/4.7.3/msvc2008/lib"]
libraries=["OpenMS", "xerces-c_3", "QtCore4", "gsl",
                    "cblas",
          ]



def ext(name, sources):


    rv = Extension(
        name,
        sources = sources,
        language="c++",
        include_dirs=[
                      r"C:\QtSDK\Desktop\Qt\4.7.3\msvc2008\include",
                      r"C:\QtSDK\Desktop\Qt\4.7.3\msvc2008\include\QtCore",
                      "e:/OpenMS-1.8/contrib_build/include",
                    "e:/OpenMS-1.8/include", 
                    r"C:\Python26\Lib\site-packages\numpy\core\include\\",
                     ],
        library_dirs = library_dirs,
        libraries = libraries,
        # folgendes ist wichtig:    
        # /EHs impliziert _CPPUNWIND,
        # was in <boost/config/compiler/visualc.hpp> BOOST_NO_EXCEPTION
        # setzt, was wiederum in <boost/throw_excption.hpp> dazu führt, 
        # dass boost::throw_expction() deklariert aber nicht implementier
        # wird. und das führt zu "unresolved symbol" beim linken !
        extra_compile_args = [ "/EHs"]  
     
    )
    rv.pyrex_directives = {"boundscheck": False, "annotate": True }
    return rv

ext_modules = [ ext("_pyOpenMS", [ "pyOpenMS/_pyOpenMS.pyx" ]) ]
ext_modules = [ ext("_pyOpenMS", [ "_pyOpenMS.pyx" ]) ]

setup(

  name = "pyOpenMS",
  version="0.1",
  url="http://github.com/uweschmitt/msExpert",
  author="uwe schmitt",
  author_email="uschmitt@mineway.de",

  #packages = ["pyOpenMS"],

  #ext_package = "pyOpenMS",
  ext_modules = ext_modules,
  cmdclass = {'build_ext': build_ext},
  #package_data = { "pyOpenMS": [ "OpenMS.dll", "msvcr90.dll", "xerces-c_3_0.dll"] },
)

