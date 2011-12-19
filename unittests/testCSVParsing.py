import ms
def testCSVParsing():
    tab = ms.loadCSV("data/mass.csv", )
    fms = '"%.2fm" % (o/60.0)'
    assert tab.getFormat("RT_min") == "%.2f", tab.getFormat("RT_min")
    tab.setFormat("RT_min", fms)
    assert tab.getFormat("RT_min") == fms
