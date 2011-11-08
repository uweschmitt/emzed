print "LOAD PUBCHEM DB"
print
from configs import globalDataPath
from libms.DataBases import PubChemDB
import os, new

dbPath = os.path.join(globalDataPath, "pubchem.db")
data = PubChemDB.load(dbPath)
newIds = PubChemDB.getNewIds(data)
if len(newIds):
    print "PUBCHEM OUT OF SYNC"
    if os.access(globalDataPath, os.W_OK):
        PubChemDB.update(dbPath, data, newIds)
        data = PubChemDB.load(dbPath)
    else:
        print
        print "*"*65
        print "YOU ARE NOT ALLOW TO UPDATE GLOBAL DB"
        print "PLEASE INFORM YOUR ADMINISTRATOR"
        print "*"*65
        print

# cleanup namespace
db = new.module("db")
db.pubchemData=data
del data
del new
del dbPath
del newIds
del globalDataPath
del PubChemDB
