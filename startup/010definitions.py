print "LOAD DEFINITIONS"
print
__builtins__["MMU"] = 0.001
__builtins__["MASS_E"] = 5.4857990946e-4
__builtins__["MASS_P"] = 1.007276466812
__builtins__["MASS_N"] = 1.00866491600

from libms.Chemistry.Elements import Elements, MonoIsotopicElements
import new
mass = new.module("mass")

mass.e = MASS_E
mass.p = MASS_P
mass.n = MASS_N

elements = Elements()
for row in elements:
    sym = elements.get(row, "symbol")
    massnumber = elements.get(row, "massnumber")
    isomass = elements.get(row, "mass")
    setattr(mass, sym+str(massnumber), isomass)

monoelements = MonoIsotopicElements()
for row in monoelements:
    sym = monoelements.get(row, "symbol")
    m0 = monoelements.get(row, "m0")
    setattr(mass, sym, m0)

del elements
del monoelements
del Elements
del MonoIsotopicElements
del new
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



