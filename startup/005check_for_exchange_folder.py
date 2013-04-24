from userConfig import getVersionedExchangeFolder
if  getVersionedExchangeFolder() is None:
    print "CAN NOT REACH EXCHANGE FOLDER !!!!"
    raw_input("PRESS ENTER TO CONTINUE")
