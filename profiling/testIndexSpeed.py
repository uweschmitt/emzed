
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
T  = db.table

# somme neutral masses are None, which causes problems when
# compairing
T = T.filter(T.m0 != None)

rows = [[i] for i in [500]] # range(0, 1000, 10)]
T0 = Table(["msoll"], [float], "%.2f", rows)

def runLJoin1():
    res =T0.leftJoin(T, (T.m0>=T0.msoll-0.01) & (T.m0 <= T0.msoll+0.01) )
def runLJoin2():
    res =T0.leftJoin(T, (T.m0+0.01>=T0.msoll) & (T.m0-0.01 <= T0.msoll) )
def runLJoin3():
    res =T0.leftJoin(T, (1*T.m0>=T0.msoll*(+1)-0.01) & (T.m0*(+1) <= T0.msoll*(+1)+0.01) )
def runLJoin4():
    res =T0.leftJoin(T, (-1*T.m0<=3) & (T.m0*(-1) >= T0.msoll*(-1)-0.01))

print "profile runLJoin"
print
print
cProfile.run("runLJoin2()", "runLJoin2.prof")
p=pstats.Stats("runLJoin2.prof")
p.strip_dirs().print_stats(10)
cProfile.run("runLJoin1()", "runLJoin1.prof")
p=pstats.Stats("runLJoin1.prof")
p.strip_dirs().print_stats(10)

print
cProfile.run("runLJoin3()", "runLJoin3.prof")
p=pstats.Stats("runLJoin3.prof")
p.strip_dirs().print_stats(10)
print
print
cProfile.run("runLJoin4()", "runLJoin4.prof")
p=pstats.Stats("runLJoin4.prof")
p.strip_dirs().print_stats(10)
print
