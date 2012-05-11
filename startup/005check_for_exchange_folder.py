from userConfig import getExchangeFolder
if  getExchangeFolder() is None:
    print "CAN NOT REACH EXCHANGE FOLDER !!!!"
    raw_input("PRESS ENTER TO CONTINUE")
