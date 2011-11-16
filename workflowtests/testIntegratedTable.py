#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms

table = ms.loadTable("integrated_features.table")
print
print table.rows[0]
print
print table.colFormatters
print
print table.colNames
ms.inspect(table)

