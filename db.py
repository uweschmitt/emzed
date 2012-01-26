print "LOAD PUBCHEM DB"
import userConfig
from libms.DataBases import PubChemDB
import os

exchangeFolder = userConfig.getExchangeFolder()
dbPath = os.path.join(exchangeFolder, "pubchem.db")
pubChemDB = PubChemDB(dbPath)

if not os.environ.get("NO_PUBCHEM_UPDATE"):
    newIds, missingIds = pubChemDB.synchronize()
    if len(newIds) and not len(missingIds):
        print "PUBCHEM NOT UP TO DATE"
        if os.access(exchangeFolder, os.W_OK):
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
        if os.access(exchangeFolder, os.W_OK):
            print
            print "PLEASE RUN db.pubchem.reset() AND RESTART SHELL TO"
            print "GET A NEW VERSION OF pubChemDB"
            print
            #pubChemDB.reset(100)

        else:
            print
            print "*"*65
            print "YOU ARE NOT ALLOW TO UPDATE GLOBAL DB"
            print "PLEASE INFORM YOUR ADMINISTRATOR"
            print "*"*65
            print
    del newIds, missingIds


# cleanup namespace
del os
del dbPath
del userConfig
del exchangeFolder
del PubChemDB
