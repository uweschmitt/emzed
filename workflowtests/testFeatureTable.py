#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms

table = ms.loadTable("features.table")

pm = table.rows[0][table.getIndex("peakmap")]



