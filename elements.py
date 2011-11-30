print "LOAD ELEMENTS"

from libms.Chemistry.Elements import Elements, MonoIsotopicElements

elements = Elements()
for row in elements:
    symbol = elements.get(row, "symbol")
    massnumber = elements.get(row, "massnumber")
    data = elements.get(row)
    del data["symbol"]
    del data["massnumber"]
    exec("%s=data" % (symbol+str(massnumber)))

monoelements = MonoIsotopicElements()
for row in monoelements:
    symbol = monoelements.get(row, "symbol")
    data = monoelements.get(row)
    del data["symbol"]
    exec("%s=data" % symbol)

del elements
del monoelements
del Elements
del MonoIsotopicElements
try:
    del row
    del symbol
    del data
    del massnumber
except: # loops where empty
    pass


