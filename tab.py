print "LOAD LOCAL DATA TABLES"

from configs import repositoryPathes
import os, ms, glob
from  libms.Chemistry.Elements import Elements

here = os.path.abspath(os.path.dirname(__file__))

for path in [os.path.join(here, "tables")] + repositoryPathes:
    for p in glob.glob("%s/*.csv" % path):
        try:
            table = ms.loadCSV(p)
        except Exception, e:
            import traceback
            traceback.print_exc()
            print "PARSING",p,"FAILED"
            continue
        name, _ = os.path.splitext(os.path.basename(p))
        name = name.replace(" ","_")
        table.title = name
        exec("%s=table" % name)
        print "LOADED", name, "FROM", p
    # table files overrun csv files !
    for p in glob.glob("%s/*.table" % path):
        try:
            table = ms.loadTable(p)
        except Exception, e:
            import traceback
            traceback.print_exc()
            print "PARSING",p,"FAILED"
            continue
        name, _ = os.path.splitext(os.path.basename(p))
        name = name.replace(" ","_")
        table.title = name
        table.meta["loaded_from"] = os.path.abspath(p)
        exec("%s=table" % name)
        print "LOADED", name, "FROM", p

elements = Elements()
# next line only valid after execution of 100loadpubchem.py during
# startup:

if not os.environ.get("WITHOUT_PUBCHEM"):
    import db
    pc_full = db.pubChemDB.table
    pc_kegg = pc_full.filter(pc_full.isInKEGG == 1)
    pc_hmdb = pc_full.filter(pc_full.isInHMDB == 1)
    del db

del repositoryPathes
del here
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
del Elements
