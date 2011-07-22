from pyOpenMS import *

import sys, time

def dump(path):

    started = time.time()
    dataset = loadMzXMLFile(path)
    ended = time.time()

    print
    print "loading needed %.1f secs" % (ended-started)
    print "dataset has", len(dataset), "specs"
    print
    dataset.removeZeroIntensities()
    ended2 = time.time()
    print "zero intensity removal needed %.1f secs" % (ended2-ended)
    print

    for i, spec in enumerate(dataset):
        print "%3d  RT=%f  MSLevel=%d,  polarity %s " %( i, spec.RT, spec.msLevel, spec.polarization)
        print "     from %s   to %s" % ( spec.peaks[0], spec.peaks[-1], )
        if spec.msLevel > 1:
            print "      PRECURSORS: ",
            for pc in spec.precursors:
                print pc, 
            print
        print


if __name__ == "__main__":
    dump(sys.argv[1])
