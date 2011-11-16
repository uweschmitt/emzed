#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms

table = ms.loadTable("pubchem_reduced.table")
table.rows[0][table.getIndex("iupac")] = "IUPAC-Test. aflkljad lfjasdflöjasdlö fsdlafö jalödfjasdflasdjö"
print len(table)
ms.inspect(table)

