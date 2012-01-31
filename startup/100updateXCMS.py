from libms.RConnect.XCMSConnector import doXcmsUpgrade, installXcmsIfNeeded

print
print "INSTALL XCMS IF NEEDED"
print
installXcmsIfNeeded()
print
print "LOOK FOR XCMS UPDATES"
print
doXcmsUpgrade()

del installXcmsIfNeeded
del doXcmsUpgrade
