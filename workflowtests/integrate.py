#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms

table = ms.loadTable("features.table")

reinttab = ms.integrate(table, "std")
reinttab = ms.integrate(reinttab, "std")

reinttab.store("integrated_features.table", True)
