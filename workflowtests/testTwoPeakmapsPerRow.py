import sys
sys.path.insert(0, "..")
import ms

t = ms.loadTable("integrated_features.table")

t2 = t.copy()

tj = t.join(t2, t.id == t2.id)

tj.rtmin__0 -= 20
tj.rtmax__0 -= 20

pm = tj.peakmap__0.values[0]
for s in pm.spectra:
    s.rt -= 20

ms.inspect(tj)
