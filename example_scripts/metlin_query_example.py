import sys
sys.path.insert(0, "..")
sys.path.insert(0, ".")
import ms

a=ms.toTable("m0",[282.2282])
a.title="example"
a.addColumn("polarity", "-")

b = ms.matchMetlin(a, "m0", 50)

b.info()

ms.inspect(b)
