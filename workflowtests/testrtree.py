#encoding: utf-8
import sys, time
sys.path.insert(0, "..")

import ms

table = ms.loadTable("features.table")

pm = table.rows[0][table.getIndex("peakmap")]

import rtree


def generate():
    i = 0
    print len(pm)
    for j, spec in enumerate(pm.spectra):
        print j,
        sys.stdout.flush()
        for (x,y) in spec.peaks:
            yield (i, (x,y, x+1, y+1), None)
            i += 1

print "build tree"
s = time.time()
idx = rtree.Rtree(generate())

print time.time() -s, "seconds for building rtree"




