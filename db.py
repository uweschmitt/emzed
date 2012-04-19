print "LOAD PUBCHEM DB"
import userConfig
from libms.DataBases import PubChemDB
import os

exchangeFolder = userConfig.getExchangeFolder()
dbPath = os.path.join(exchangeFolder, "pubchem.db")
pubChemDB = PubChemDB(dbPath)

if not os.environ.get("NO_PUBCHEM_UPDATE"):
    newIds, missingIds = pubChemDB.getDiff()
    if newIds or missingIds:
        print "PUBCHEM NOT UP TO DATE"
        if newIds:
            print len(newIds), "NEW ENTRIES"
        if missingIds:
            print len(missingIds), "DELETED ENTRIES"
        writable = True
        try:
            open(os.path.join(exchangeFolder, "_test"), "w")
        except IOError:
            writable = False
        if writable:
            pubChemDB.update()
            print "WRITE CURRENT DB"
            pubChemDB.store()
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
