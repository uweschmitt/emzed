#encoding: utf-8
import sys
sys.path.insert(0, "..")

import ms

import tab


table = tab.pc_full

print "got", len(table), "rows"

def show():
    ms.inspect(table)

show()

