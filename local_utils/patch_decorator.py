import functools, inspect, sys

def replace( orig_func, target=None, verbose=False):
   
    def decorator(new_func, target=target):

        def wrapper(*a, **kw):
            return new_func(*a, **kw)

        wrapper.isPatched = True

        if inspect.ismethod(orig_func):
            if target is None:
                target =  orig_func.im_class
            if verbose:
                print "replace method", orig_func, "in", target, "with", new_func
            setattr(target, orig_func.__name__, wrapper)
            setattr(target, "_orig_%s" % orig_func.__name__, orig_func)
        elif inspect.isfunction(orig_func):
            if target is None:
                target = sys.modules[orig_func.__module__]
            if verbose:
                print "replace function", orig_func, "in", target, "with", new_func
            setattr(target, orig_func.func_name, wrapper)
            setattr(target, "_orig_%s" % orig_func.__name__, orig_func)
        else:
            raise Exception("can not wrap %s " % orig_func)

        return wrapper # not needed as new_func is not modified at all

    return decorator


def add(target, verbose=False):

    def decorator(new_func, target=target):

        if verbose:
            print "add ", new_func, "to", target
        setattr(target, new_func.__name__, new_func)

    return decorator
