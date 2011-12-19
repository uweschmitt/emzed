import ms
import numpy as np
import copy
#d=ms.loadTable(r"unittests\data\ftab_for_mzalign.table")

#d = d.filter(d.id < 100)
#d=ms.integrate(d, "trapez")
#d.store("integrated.table", True)
d=ms.loadTable("joined.table")
d.info()
pm = copy.deepcopy(d.peakmap_1.values[0])
for s in pm.spectra:
    s.peaks[:,0] *= 1.001
d.replaceColumn("peakmap_1", pm)

#d.dropColumn("area") # not integrated any more
#print "loaded"
#pm = d.get(d.rows[0], "peakmap")
#ms.inspectPeakMap(pm)
#print d.colNames
import os
os.environ["WITHOUT_PUBCHEM"]="1"
import tab
ms.inspect([d, tab.elements], True)
#ms.mzalign(d, interactive=True, destination=".")
#ms.mzalign(d, interactive=True)
