print "LOAD MASSES"
print

from libms.Chemistry.Elements import Elements, MonoIsotopicElements
from libms.Chemistry.Tools import monoisotopicMass
import installConstants

e = MASS_E
p = MASS_P
n = MASS_N

of = monoisotopicMass


elements = Elements()
for row in elements:
    sym = elements.get(row, "symbol")
    massnumber = elements.get(row, "massnumber")
    isomass = elements.get(row, "mass")
    exec("%s=isomass" % (sym+str(massnumber)))

monoelements = MonoIsotopicElements()
for row in monoelements:
    sym = monoelements.get(row, "symbol")
    m0 = monoelements.get(row, "m0")
    exec("%s=m0" % sym)

del installConstants
del monoisotopicMass
del elements
del monoelements
del Elements
del MonoIsotopicElements
try:
    del row
    del sym
    del isomass
    del massnumber
except: # loops where empty
    pass

try:
    del m0
except:
    pass



