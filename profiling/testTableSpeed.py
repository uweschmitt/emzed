
import cProfile, time, pstats
import sys
sys.path.insert(0, "..")

from libms.DataBases import PubChemDB
from libms.DataStructures import Table

def timeit(c):
    s = time.time()
    c()
    return time.time()-s

db = PubChemDB("C:/TMP/pubchem.db")
T  = db.table.filter(db.table.m0 != None)
rows = [[i] for i in range(0, 1000, 10)]
T0 = Table(["msoll"], [float], "%.2f", rows)


def runLJoin():
    res =T0.leftJoin(T, (T.m0>=T0.msoll-0.01) & (T.m0 <= T0.msoll+0.01) )
def runJoin():
    res =T0.join(T, (T.m0>=T0.msoll-0.01) & (T.m0 <= T0.msoll+0.01) )

def runFilter():
    for r in rows[:10]:
        res = T.filter( (T.m0 >= r[0]) & (T.m0 <=r[0]+10) )

print "profile runLJoin"
print
cProfile.run("runLJoin()", "runLJoin.prof")
p=pstats.Stats("runLJoin.prof")
p.strip_dirs().print_stats(25)
print
print "profile runJoin"
print
cProfile.run("runJoin()", "runJoin.prof")
p=pstats.Stats("runJoin.prof")
p.strip_dirs().print_stats(25)
print
print "profile runFilter"
print
cProfile.run("runFilter()", "runFilter.prof")
p=pstats.Stats("runFilter.prof")
p.strip_dirs().print_stats(25)
print

print
print "100 LJoins %.2f sec" % timeit(runLJoin)
print "100 Joins  %.2f sec" % timeit(runJoin) 
print "100 Filter %.2f sec" % timeit(runFilter)
print

