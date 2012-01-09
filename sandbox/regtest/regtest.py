from optparse import OptionParser
import difflib
import StringIO
import sys
import types

def run_callable(obj, out, name):
    try:
        sys.stdout = out
        print "RUN", name
        obj()
    finally:
        sys.stdout = sys.__stdout__

def run_test(path):
    mod = __import__(path[:-3])
    out = StringIO.StringIO()
    collected = []
    for name in mod.__dict__:
        if name.upper().startswith("TEST"):
            obj = getattr(mod, name)
            if type(obj) == type: # class
                for mname in obj.__dict__:
                    if mname.upper().startswith("TEST"):
                        name = name+"."+mname
                        collected.append((name, getattr(obj(), mname)))
            elif type(obj) == types.FunctionType:
                collected.append((name, obj))

    collected.sort()
    for name, fun in collected:
        run_callable(fun, out, name)
    return out.getvalue()

usage="usage: %prog [options] file1.py .."
parser = OptionParser(usage)
parser.add_option("-r", "--reset", dest="reset", 
                  help="reset regressiontest",
                  action="store_true", default=False)

options, args = parser.parse_args()
if not len(args):
    parser.error("nead at least one input file")

exitstatus = 0
for f in args:
    if not f.endswith(".py"):
        raise Exception("can not handle file %s" % f)

    out = run_test(f)
    out_file = f[:-3]+".tobe"
    if options.reset:
        open(out_file,"w").write(out)
    else:
        try:
            tobe = [ l.rstrip("\n") for l in open(out_file, "r") ]
        except:
            raise Exception("could not read %s. maybe you have to reset "\
                            "the test." % out_file)
        is_ = [ l.rstrip("\n") for l in out.split("\n") ]
        is_ = [ l for l in is_ if l ]

        tobe = [ l for l in tobe if l ]

        is_file = f[:-3]+".is"
        with open(is_file, "w") as fp:
            for line in is_:
                print >> fp, line

        for line in difflib.unified_diff(tobe, is_, "tobe", "is", n=3):
            print line
            exitstatus = 1

exit(exitstatus)
