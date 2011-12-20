#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms

table = ms.loadTable("features.table")

ms.alignFeatureTables([table, table.copy(), table], table, destination=".")

