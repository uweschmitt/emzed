print "LOAD MASSES"

from libms.Chemistry.Elements import Elements, MonoIsotopicElements
from libms.Chemistry.Tools import monoisotopicMass
import installConstants

e = 5.4857990946e-4
p = 1.007276466812
n = 1.00866491600

of = monoisotopicMass


elements = Elements()
for row in elements.rows:
    sym = elements.get(row, "symbol")
    massnumber = elements.get(row, "massnumber")
    isomass = elements.get(row, "mass")
    exec("%s=isomass" % (sym+str(massnumber)))

monoelements = MonoIsotopicElements()
for row in monoelements.rows:
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



