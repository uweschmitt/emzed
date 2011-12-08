#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms, cProfile

table = ms.loadTable("x.table")

print "got", len(table), "rows"

def show():
    ms.inspect(table)

show()
#cProfile.run("show()")

