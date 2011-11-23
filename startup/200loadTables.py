print "LOAD LOCAL DATA TABLES"
print
from configs import repositoryPathes
import os, ms, glob, new
from  libms.Chemistry import Elements

tab = new.module("tab")

for path in repositoryPathes:
    for p in glob.glob("%s/*.csv" % path):
        try:
            table = ms.loadCSV(p)
        except Exception, e:
            print "PARSTING",p,"FAILED"
            continue
        name, _ = os.path.splitext(os.path.basename(p))
        setattr(tab, name, table)
    # table files overrun csv files !
    for p in glob.glob("%s/*.table" % path):
        try:
            table = ms.loadTable(p)
        except Exception, e:
            print "PARSTING",p,"FAILED"
            continue
        name, _ = os.path.splitext(os.path.basename(p))
        table.meta["loaded_from"] = os.path.abspath(p)
        setattr(tab, name, table)

tab.elements = Elements()
del repositoryPathes
del path

try:
    del table
except:
    pass

try:
    del name
except:
    pass
    
del os
del glob
del new
del Elements
