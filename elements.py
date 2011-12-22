print "LOAD ELEMENTS"

from libms.Chemistry.Elements import (Elements as _Elements,
                                      MonoIsotopicElements as _Mono)

_elements = _Elements()
for _row in _elements.rows:
    _symbol = _elements.get(_row, "symbol")
    _massnumber = _elements.get(_row, "massnumber")
    _data = _elements.get(_row)
    del _data["symbol"]
    del _data["massnumber"]
    exec("%s=_data" % (_symbol+str(_massnumber)))

_monoelements = _Mono()
for _row in _monoelements.rows:
    _symbol = _monoelements.get(_row, "symbol")
    _data = _monoelements.get(_row)
    del _data["symbol"]
    exec("%s=_data" % _symbol)


