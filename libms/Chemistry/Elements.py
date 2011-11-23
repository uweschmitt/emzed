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
            dataPath = os.environ.get("OPENMS_DATA_PATH")
            if dataPath is None:
                raise Exception("OPENMS_DATA_PATH env variable not set. Your "\
                                "pyOpenMS installations seems to be broken")

            elementPath = os.path.join(dataPath, "CHEMISTRY", "Elements.xml")
            param = pyOpenMS.Param()
            param.load(elementPath)

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
                if kind in ["Name", "Symbol", "AtomicNumber", "AverageWeight",
                            "MonoWeight"]:
                    entry = param.getValue(pyOpenMS.String(k))
                    value = getattr(entry, getters[entry.valueType()])()
                    data[element][kind] =  value
                if kind == "Isotopes":
                    neutrons = int(fields[3])
                    distribution = param.getValue(pyOpenMS.String(k)).toDouble()
                    data[element]["Isotopes"][neutrons]=distribution

            maxNumIsotopes = max(len(e["Isotopes"]) for e in data.values())
            colNames = ["number", "symbol", "name", "mw", "m0", "min_neutrons"]
            colNames += ["prob_%d" % i for i in range(maxNumIsotopes)]
            colTypes = [int, str, str, float, float, int]
            colTypes += [float] * maxNumIsotopes
            colFormats = ["%d", "%s", "%s", "%.6f", "%.6f", "%d" ]
            colFormats += ["%.2f"] * maxNumIsotopes

            rows = []
            for props in data.values():
                row = [props.AtomicNumber, props.Symbol, props.Name,
                       props.AverageWeight, props.MonoWeight]
                row.append(min(props.Isotopes.keys()))
                props = [d for n, d  in sorted(props.Isotopes.items())]
                props += [None] * (maxNumIsotopes - len(props)) # fill row
                row  += props
                rows.append(row)

            super(Elements, self).__init__(colNames, colTypes, colFormats, rows,
                                           title="Elements")


if __name__ == "__main__":
    print ElementData().getElements()
    print ElementData().getSymbols()



