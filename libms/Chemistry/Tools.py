import Elements
import re

def monoisotopicMass(mf):
    elements = Elements.MonoIsotopicElements()
    sum_ = 0.0
    for a, n in re.findall("([A-Z][a-z]?)(\d*)", mf):
        m0 = elements.get(elements.rowFor(a), "m0")
        if n == "":
            sum_ += m0
        else:
            sum_ += m0*int(n)
    return sum_



