#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms

table = ms.loadTable("integrated_features.table")
table.editableColumns = ["mzmin"]
ms.inspect(table)
print table.mzmin.values

