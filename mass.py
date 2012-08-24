from libms.Chemistry.Elements import (Elements as _Elements,
                                      MonoIsotopicElements as _Mono)

from libms.Chemistry.Tools import monoisotopicMass as _monoisotopicMass

e = 5.4857990946e-4
p = 1.007276466812
n = 1.00866491600

of = _monoisotopicMass

_elements = _Elements()
_symbols = _elements.symbol.values
_massnumbers = _elements.massnumber.values
_isomasses = _elements.mass.values

for (_sym, _massnumber, _isomass) in zip(_symbols, _massnumbers, _isomasses):
    exec("%s=_isomass" % (_sym+str(_massnumber)))

_mono =  _Mono()
_symbols = _mono.symbol.values
_m0s = _mono.m0.values
for (_sym, _m0) in zip (_symbols, _m0s):
    exec("%s=_m0" % _sym)



