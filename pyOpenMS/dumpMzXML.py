from pyOpenMS import *

import sys

def dump(path):

    dataset = loadMzXMLFile(path)

    print
    print "dataset has", len(dataset), "specs"
    print

    for spec in dataset:
        print "%3d  RT=%f  MSLevel=%d" %( i, spec.getRT(), spec.getMSLevel())
        print "     from %s   to %s " % ( spec[0], spec[-1])
        if spec.getMSLevel()>1:
            print "      PRECURSORS: ",
            for pc in spec.getPrecursors():
                print pc, 
            print
        print


if __name__ == "__main__":
    dump(sys.argv[1])
