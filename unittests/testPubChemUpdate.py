from libms.DataBases import PubChemDB
import os.path

def testPubChemUpdate():

    dp = "temp_output"
    dbPath = os.path.join(dp, "pubchem.db")
    data = PubChemDB.load(dbPath)
    assert len(data)==0
    newIds = PubChemDB.getNewIds(data, 100)
    assert len(newIds)==100
    PubChemDB.update(dbPath, data, newIds[:100])
    assert len(data) == 100
    data = PubChemDB.load(dbPath)
    assert len(data) == 100
