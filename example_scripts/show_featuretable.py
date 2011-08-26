import ms

data=file("xcms_output.csv").readlines()
tab = ms.XCMSFeatureParser().parse(data)

print tab.colNames
print
print tab.colTypes
print
print tab.colFormats
print
print tab.rows[0]
print
print tab.rows[-1]
print
ms.viewTable(tab)
