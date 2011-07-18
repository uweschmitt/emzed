from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import glob

def merge_and_setup_files():

    with file("_pyOpenMS.pyx", "w") as fp:

        print >> fp, "from cython.operator cimport address, dereference as deref"

        for p in glob.glob("*.pxd"):
            print >> fp, "from %s cimport *" % (p[:-4])

        print >> fp
        for p in glob.glob("*.pyxp"):
            for line in file(p):
                print >> fp, line
            print >> fp

    with file("pyOpenMS.py", "w") as fp:

        print >> fp, "from _pyOpenMS import \\"

        def classnames():
            for p in glob.glob("*.pyxp"):
                yield  p[:-5]

        lines = ( "_%s as %s \\" % (cn,cn) for cn in \
                                   ( p[:-5] for p in glob.glob("*.pyxp")))

        print >> fp, "\n,      ".join(lines)
    


def ext(name, sources):

    merge_and_setup_files()

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


ext_modules = [ ext("_pyOpenMS", ["_pyOpenMS.pyx"]) ]

setup(
  name = 'minimal open ms wrapper',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)

