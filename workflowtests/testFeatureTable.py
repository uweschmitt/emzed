#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms

table = ms.loadTable("features.table")

print table.rows[0]
ms.inspect([table])

