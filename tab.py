print "LOAD LOCAL DATA TABLES"
print

from configs import repositoryPathes
import os, ms, glob, new
from  libms.Chemistry.Elements import Elements
from libms.DataBases import PubChemDB

for path in ["tables"] + repositoryPathes:
    for p in glob.glob("%s/*.csv" % path):
        try:
            table = ms.loadCSV(p)
        except Exception, e:
            print "PARSTING",p,"FAILED"
            continue
        name, _ = os.path.splitext(os.path.basename(p))
        exec("%s=table" % name)
    # table files overrun csv files !
    for p in glob.glob("%s/*.table" % path):
        try:
            table = ms.loadTable(p)
        except Exception, e:
            print "PARSTING",p,"FAILED"
            continue
        name, _ = os.path.splitext(os.path.basename(p))
        table.meta["loaded_from"] = os.path.abspath(p)
        exec("%s=table" % name)


elements = Elements()
# next line only valid after execution of 100loadpubchem.py during
# startup:

import db

pc_full = db.pubChemDB.table
pc_kegg = pc_full.filter(pc_full.is_in_kegg == 1)
pc_hmdb = pc_full.filter(pc_full.is_in_hmdb == 1)


del db
del repositoryPathes

try:
    del path
except:
    pass


try:
    del p
except:
    pass

try:
    del table
except:
    pass

try:
    del name
    del _
except:
    pass

del ms
del os
del glob
del new
del Elements
del PubChemDB
