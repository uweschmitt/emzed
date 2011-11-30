import os
import pyOpenMS
from collections import defaultdict

from ..DataStructures import Table

class NestedBunchDict(dict):

   def __missing__(self, k):
       self[k] = NestedBunchDict()
       return self[k]

   def __getattr__(self, k):
       return self[k]


class Elements(Table):

    __we_are_all_one = dict() # borg pattern, data is only loaded once

    def __init__(self):
        self.__dict__ = Elements.__we_are_all_one  # shared state

        if not hasattr(self, "rows"):
            path = os.path.dirname(os.path.abspath(__file__))
            param = pyOpenMS.Param()
            param.load(os.path.join(path, "Elements.xml"))

            getters = {
                    pyOpenMS.DataType.STRING_VALUE: "toString",
                    pyOpenMS.DataType.INT_VALUE: "toInt",
                    pyOpenMS.DataType.DOUBLE_VALUE: "toDouble",
            }


            data = NestedBunchDict()
            for k in param.getKeys():
                fields = k.split(":")
                element = fields[1]
                kind = fields[2]
                if kind in ["Name", "Symbol", "AtomicNumber"]:
                    entry = param.getValue(pyOpenMS.String(k))
                    value = getattr(entry, getters[entry.valueType()])()
                    data[element][kind] =  value
                if kind == "Isotopes":
                    massnumber = int(fields[3])
                    kind = fields[4]
                    if kind in ["RelativeAbundance", "AtomicMass"]:
                        entry = param.getValue(pyOpenMS.String(k))
                        value = getattr(entry, getters[entry.valueType()])()
                    data[element]["Isotopes"][massnumber][kind]=value

            colNames = ["number", "symbol", "name", "massnumber", "mass", "abundance"]
            colTypes = [int, str, str, int, float, float]
            colFormats = ["%d", "%s", "%s", "%d", "%.10f", "%.3f" ]

            rows = []
            for props in data.values():
                row0 = [props.AtomicNumber, props.Symbol, props.Name]
                for k, isoprop in props.Isotopes.items():
                    row = row0 + [ k, isoprop.AtomicMass, isoprop.RelativeAbundance / 100.0 ]
                    rows.append(row)

            super(Elements, self).__init__(colNames, colTypes, colFormats, rows,
                                           title="Elements")
            self.sortBy("number")


class MonoIsotopicElements(Table):

    # borg pattern
    __we_are_all_one = dict()

    def __init__(self):
        self.__dict__ = MonoIsotopicElements.__we_are_all_one

        if not hasattr(self, "rows"): # empty on first run
            elements = Elements()
            self.rows = []
            # find monoisotopic data for each element
            for s in set(elements.symbol.values): # unique symbols
                tsub = elements.filter(elements.symbol == s)
                massnumber = tsub.massnumber.values
                t0   = tsub.filter(tsub.massnumber == min(massnumber))
                self.rows.append(t0.rows[0][:])

            self.colNames = elements.colNames
            self.colTypes = elements.colTypes
            self.colFormats = elements.colFormats
            self.title = "Monoisotopic Elements"
            self.meta  = dict()

            self.updateIndices()
            self.setupFormatters()
            self.emptyColumnCache()
            self.renameColumns(mass="m0")
            self.dropColumn("abundance")
            self.sortBy("number")

    def buildSymbolIndex(self):
        symbols = self.symbol.values
        self.symbolIndex = dict( (s,i) for (i,s) in enumerate(symbols))

    def sortBy(self, *a, **kw):
        super(MonoIsotopicElements, self).sortBy(*a, **kw)
        self.buildSymbolIndex()

    def getProperty(self, symbol, name):
        if not symbol in self.symbolIndex:
            return None
        row = self.rows[self.symbolIndex.get(symbol)]
        return self.get(row, name)



if __name__ == "__main__":
    print ElementData().getElements()
    print ElementData().getSymbols()



