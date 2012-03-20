from libms.DataBases.PubChemDB import PubChemDB
import os.path

def testPubChemUpdate():

    dp = "temp_output"
    dbPath = os.path.join(dp, "pubchem.db")
    db = PubChemDB(dbPath)
    assert len(db.table)==0

    unknown, missing = db.getDiff(100)
    assert len(unknown)==100, len(unknown)
    assert len(missing)==0, len(missing)

    db.update(100)
    assert len(db.table) == 100
    assert db.table.rows[0][-1].startswith("http")
    assert len(db.table.rows[0]) == len(db.colNames)
    assert db.table.colNames[0] == "m0"

    row = db.table.rows[0]
    assert db.table.get(row, "is_in_kegg") in [0,1]
    assert db.table.get(row, "is_in_hmdb") in [0,1]

    unknown, missing = db.getDiff(100)
    assert len(unknown)==100, len(unknown)
    #assert len(missing)==100, len(missing)
    assert len(set(unknown) & set(db.table.cid.values)) == 0 # no interscetion

    db.store()
    db = PubChemDB(dbPath)
    assert len(db.table) == 100
    assert db.table.rows[0][-1].startswith("http")
    assert len(db.table.rows[0]) == len(db.colNames)

