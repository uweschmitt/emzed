#input-encoding: utf-8
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import glob



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
        library_dirs=["e:/OpenMS-1.8_BUILD", r"e:\OpenMS-1.8\contrib_build\lib",
r"c:/QtSDK/Desktop/Qt/4.7.3/msvc2008/lib"],
        libraries=["OpenMS", "xerces-c_3", "QtCore4", "gsl",
                         #   "libboost_date_time-vc90-mt" ,
                            #"libboost_iostreams-vc90-mt" ,
                         #   "libboost_math_c99-vc90-mt" ,
                         #   "libboost_math_c99f-vc90-mt" ,
                         #   "libboost_math_c99l-vc90-mt" ,
                         #   "libboost_math_tr1-vc90-mt" ,
                         #   "libboost_math_tr1f-vc90-mt" ,
                         #   "libboost_math_tr1l-vc90-mt" ,
                            "cblas",
                  ],
        #define_macros= [ (n, None) for n in \
               #"_SCL_SECURE_NO_WARNINGS _CRT_SECURE_NO_WARNINGS _CRT_SECURE_NO_DEPRECATE".split() ],
        #undef_macros= "BOOST_NO_EXCEPTIONS".split(),

        # folgendes ist wichtig:    
        # /EHs impliziert _CPPUNWIND,
        # was in <boost/config/compiler/visualc.hpp> BOOST_NO_EXCEPTION
        # setzt, was wiederum in <boost/throw_excption.hpp> dazu führt, 
        # dass boost::throw_expction() deklariert aber nicht implementier
        # wird. und das führt zu "unresolved symbol" beim linken !
        extra_compile_args = [ "/EHs"]  
     
    )
    rv.pyrex_directives = {"boundscheck": False}
    return rv


ext_modules = [ ext("pyOpenMS", [ "pyOpenMS.pyx" ]) ]

setup(
  name = 'minimal open ms wrapper',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)

