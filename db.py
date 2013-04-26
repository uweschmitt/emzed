print "LOAD PUBCHEM DB"
import userConfig
from libms.DataBases import PubChemDB
import os

exchangeFolder = userConfig.getVersionedExchangeFolder()
if exchangeFolder is not None:
    dbPath = os.path.join(exchangeFolder, "pubchem.db")
    pubChemDB = PubChemDB(dbPath)

    if not os.environ.get("NO_PUBCHEM_UPDATE"):
        try:
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
                    print "YOU ARE NOT ALLOWED TO UPDATE GLOBAL DB"
                    print "PLEASE INFORM YOUR ADMINISTRATOR"
                    print "*"*65
                    print
            # cleanup namespace
            del newIds, missingIds
        except:
            import traceback
            traceback.format_exc()
            print "PUBCHEM NOT AVAILABLE"

    # cleanup namespace
    del dbPath
    del PubChemDB

else:
    pubChemDB = None

# cleanup namespace
del os
del userConfig
del exchangeFolder

