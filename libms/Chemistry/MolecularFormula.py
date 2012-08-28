#encoding: latin-1


import FormulaParser
import Elements


class MolecularFormula(object):

    def __init__(self, form):
        if isinstance(form, str):
            self.stringForm = form
            self.dictForm = FormulaParser.parseFormula(form)
        elif isinstance(form, dict):
            self.stringForm = FormulaParser.joinFormula(form)
            # cleanup zero counts:
            self.dictForm = dict( (e,c) for (e,c) in form.items() if c)

    def asDict(self):
        return self.dictForm

    def __str__(self):
        return self.stringForm

    asString = __str__

    def __add__(self, mf):
        dd = self.asDict().copy()
        for elem, count in mf.asDict().items():
            dd[elem] = dd.get(elem, 0) + count
        return MolecularFormula(dd)

    def __sub__(self, mf):
        dd = self.asDict().copy()
        for elem, count in mf.asDict().items():
            dd[elem] = dd.get(elem, 0) - count
        assert all(c>=0 for c in dd.values()), "negative counts not allowed"
        return MolecularFormula(dd)

    def mass(self):
        el = Elements.Elements()
        items = self.dictForm.items()
        masses = list(el.getMass(sym, massnum) for (sym, massnum), _  in items)
        if None in masses:
            return None
        return sum(m * c for m, (_, c) in zip(masses, items) )
