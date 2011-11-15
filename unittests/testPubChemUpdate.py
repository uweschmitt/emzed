from libms.DataBases import PubChemDB
import os.path

def testPubChemUpdate():

    dp = "temp_output"
    dbPath = os.path.join(dp, "pubchem.db")
    db = PubChemDB(dbPath)
    assert len(db.table)==0
    newIds, missing = db.synchronize(100)
    assert len(newIds)==100
    assert len(missing)==0
    db.update(newIds[:100])
    assert len(db.table) == 100
    db = PubChemDB(dbPath)
    assert len(db.table) == 100
    assert db.table.rows[0][-1].startswith("http")
    assert len(db.table.rows[0]) == len(db.colNames)
