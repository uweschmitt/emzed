from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import glob

mergedModule = "pyOpenMS_"

def merge_and_setup_files():


    def filesToMerge():
        for p in glob.glob("_*.pyx"):
            yield p

    with file(mergedModule+".pyx", "w") as fp:

        print >> fp, "from cython.operator cimport address as addr, dereference as deref"

        for p in glob.glob("*.pxd"):
            print >> fp, "from %s cimport *" % (p[:-4])

        print >> fp
        for p in filesToMerge():
            print >> fp, """include "%s" """ % p

    return

    # inaktiv:
    with file("pyOpenMS.py", "w") as fp:

        print >> fp, "from %s import \\" % mergedModule

        def classnames():
            for p in filesToMerge():
                yield  p[:-5]

        lines = ( "%s as %s \\" % (cn,cn[1:]) for cn in \
                                   ( p[:-4] for p in filesToMerge() ) \
                )

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


ext_modules = [ ext(mergedModule, [mergedModule+".pyx"]) ]

setup(
  name = 'minimal open ms wrapper',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)

