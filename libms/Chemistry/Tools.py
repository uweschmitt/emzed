import Elements
import re

def monoisotopicMass(mf):
    elements = Elements.MonoIsotopicElements()
    sum_ = 0.0
    for sym, n in re.findall("([A-Z][a-z]?)(\d*)", mf):
        m0 = elements.getProperty(sym, "m0") # (elements.getRowFor(a), "m0")
        if m0 is None:
            return None
        if n == "":
            sum_ += m0
        else:
            sum_ += m0*int(n)
    return sum_



