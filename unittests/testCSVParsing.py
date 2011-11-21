
import ms
def testCSVParsing():
    tab = ms.loadCSV("data/mass.csv", )
    fms = '"%.2fm" % (o/60.0)'
    assert tab.getFormat("RT min") == "%.2f"
    tab.setFormat("RT min", fms)
    assert tab.getFormat("RT min") == fms

