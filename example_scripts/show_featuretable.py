import libms

data=file("xcms_output.csv").readlines()
tab = libms.XCMSFeatureParser().parse(data)

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
libms.viewTable(tab)
