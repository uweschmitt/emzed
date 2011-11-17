print "LOAD PUBCHEM DB"
print
from configs import globalDataPath
from libms.DataBases import PubChemDB
import os, new

dbPath = os.path.join(globalDataPath, "pubchem.db")
pubChemDB = PubChemDB(dbPath)
newIds, missingIds = pubChemDB.synchronize()
if len(newIds) and not len(missingIds):
    print "PUBCHEM NOT UP TO DATE"
    if os.access(globalDataPath, os.W_OK):
        pubChemDB.update(newIds)
        pubChemDB.store()
    else:
        print
        print "*"*65
        print "YOU ARE NOT ALLOW TO UPDATE GLOBAL DB"
        print "PLEASE INFORM YOUR ADMINISTRATOR"
        print "*"*65
        print
elif len(missingIds):
    print "PUBCHEM OUT OF SYNC"
    if os.access(globalDataPath, os.W_OK):
        print 
        print "PLEASE RUN db.pubChemDB.reset() TO"
        print "GET A NEW VERSION OF pubChemDB"
        print

    else:
        print
        print "*"*65
        print "YOU ARE NOT ALLOW TO UPDATE GLOBAL DB"
        print "PLEASE INFORM YOUR ADMINISTRATOR"
        print "*"*65
        print

# cleanup namespace
db = new.module("db")
db.pubChemDB=pubChemDB
del pubChemDB
del new
del dbPath
del newIds
del missingIds
del globalDataPath
del PubChemDB
