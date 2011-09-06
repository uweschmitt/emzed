import libms

def test_XCMSParser():
    lines = file("data/xcms_output.csv").readlines()
    table = libms.XCMSFeatureParser.parse(lines)
    assert len(table.rows)==8, len(table.rows)
    assert len(table.colNames)==11, len(table.colNames)
    assert len(table.colTypes)==11, len(table.colTypes)

    table.saveCSV("temp_output/test.csv")
    
    #lines = file("temp_output/test.csv").readlines()
    #table = ms.XCMSFeatureParser.parse(lines)
    #assert len(table.rows)==8, len(table.rows)
    #assert len(table.colNames)==11, len(table.colNames)
    #assert len(table.colTypes)==11, len(table.colTypes)


