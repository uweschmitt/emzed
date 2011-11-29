print "LOAD ABUNDANCES"
print

from libms.Chemistry.Elements import Elements
from collections import defaultdict

abundances=defaultdict(dict)


elements = Elements()
for row in elements:
    sym = elements.get(row, "symbol")
    massnumber = elements.get(row, "massnumber")
    abu = elements.get(row, "abundance")
    exec("%s=abu" % (sym+str(massnumber)))
    abundances[sym][massnumber] = abu


for k in abundances.keys():
    exec("%s=abundances['%s']" % (k, k))

del elements
del abundances
del defaultdict
del Elements
try:
    del row
    del sym
    del abu
    del massnumber
    del k
except: # loops where empty
    pass


