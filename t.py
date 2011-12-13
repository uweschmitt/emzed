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
ms.inspect(d)
#ms.mzalign(d, interactive=True, destination=".")
#ms.mzalign(d, interactive=True)
