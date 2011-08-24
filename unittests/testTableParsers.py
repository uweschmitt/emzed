
import sys
sys.path.insert(0, "..")

from pyOpenMS import *
from DataStructures import *

def test_XCMSParser():
    lines = file("data/xcms_output.csv").readlines()
    table = XCMSFeatureParser.parse(lines)
    assert len(table.rows)==8, len(table.rows)
    assert len(table.colNames)==11, len(table.colNames)
    assert len(table.colTypes)==11, len(table.colTypes)


