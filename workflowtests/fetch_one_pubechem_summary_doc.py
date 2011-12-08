import sys
sys.path.insert(0, "..")
from libms.DataBases import PubChemDB as p

try:
    il = sys.argv[1:]
except:
    il = p._get_uilist(1)
data = p._get_summary_data(il)
with open("summary.xml","w") as fp:
    fp.write(data)
