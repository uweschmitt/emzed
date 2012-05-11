
def cleanup(*emzedObjects):
    """
        frees some memory for large objects
    """

    try:
        ns = __builtins__["__IPYTHON__"].user_ns
    except Exception ,e:
        raise Exception("only works if called from IPython shell")


    from libms.DataStructures import Table, PeakMap
    def is_emzed_container(o):
        return isinstance(o, Table) or isinstance(o, PeakMap)

    if not emzedObjects:
        emzedObjects = [ o for o in ns.values() if is_emzed_container(o) ]

    print "clean", emzedObjects

    for k, o in ns.items():
        if o in emzedObjects:
            if isinstance(o, PeakMap):
                print "cleanup", o
                o.spectra = []  # this consumes most memory !
            elif isinstance(o, Table):
                for row in o.rows:
                    for cell in row:
                        if isinstance(cell, PeakMap):
                            print "cleanup", cell
                            cell.spectra = [] # see above
            else:
                print "can not cleanup", o
                continue
            del ns[k]


    

