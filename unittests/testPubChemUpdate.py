from libms.DataBases.PubChemDB import PubChemDB
import os.path

def testPubChemUpdate():

    dp = "temp_output"
    dbPath = os.path.join(dp, "pubchem.db")
    db = PubChemDB(dbPath)
    assert len(db.table)==0

    unknown, missing = db.synchronize(100)
    assert len(unknown)==100, len(unknown)
    assert len(missing)==0, len(missing)

    db.update(unknown)
    assert len(db.table) == 100
    assert db.table.rows[0][-1].startswith("http")
    assert len(db.table.rows[0]) == len(db.colNames)

    unknown, missing = db.synchronize(200)
    assert len(unknown)==100, len(unknown)
    assert len(missing)==0, len(missing)

    db.store()
    db = PubChemDB(dbPath)
    assert len(db.table) == 100
    assert db.table.rows[0][-1].startswith("http")
    assert len(db.table.rows[0]) == len(db.colNames)

