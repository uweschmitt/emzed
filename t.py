import ms
import numpy as np
#d=ms.loadTable(r"unittests\data\ftab_for_mzalign.table")

#d = d.filter(d.id < 100)
#d=ms.integrate(d, "trapez")
#d.store("integrated.table", True)
d=ms.loadTable("integrated.table")
d.info()
#d.dropColumn("area") # not integrated any more
#print "loaded"
#pm = d.get(d.rows[0], "peakmap")
#ms.inspectPeakMap(pm)
#print d.colNames
d2=d.copy()
d2.dropColumn("area")
d3=d.copy()
d3.dropColumn("mz")
import os
os.environ["WITHOUT_PUBCHEM"]="1"
import tab
ms.inspect([d,d2,d3,tab.elements ])
#ms.mzalign(d, interactive=True, destination=".")
#ms.mzalign(d, interactive=True)
