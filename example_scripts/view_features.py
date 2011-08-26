from DataStructures import *
from FeatureExplorer import *

tab = XCMSFeatureParser().parse(file("xcms_output.csv").readlines())

print tab.colNames
print

print tab.colTypes
print

print tab.rows[0]
print

viewTable(tab)
