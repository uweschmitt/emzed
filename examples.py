import sys
import cStringIO
import ms
def run(txt):
    print "sample::\n"
    for line in txt.split("\n"):
        print "    >>>", line
    captured = cStringIO.StringIO()
    sys.stdout = captured
    exec(txt)
    sys.stdout = sys.__stdout__
    out= captured.getvalue()
    for line in out.split("\n"):
        print"   ", line
    print


run("""t=ms.toTable("col0", [1,2,3])
t._print() """)


