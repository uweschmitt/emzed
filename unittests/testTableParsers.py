from libms.RConnect import *

def test_XCMSParser():
    import os
    print os.getcwd()
    lines = file("data/xcms_output.csv").readlines()
    table = XCMSFeatureParser.parse(lines)
    assert len(table.rows)==8, len(table.rows)
    assert len(table.colNames)==11, len(table.colNames)
    assert len(table.colTypes)==11, len(table.colTypes)

    table.storeCSV("temp_output/test.csv")
