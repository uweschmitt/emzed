
def unpack(li, prefix="tab"):

    try:
        ns = __builtins__["__IPYTHON__"].user_ns
    except Exception ,e:
        raise Exception("only works if called from IPython shell")
    
    for i, item in enumerate(li):
        ns["%s%03d" % (prefix, i)] = item

