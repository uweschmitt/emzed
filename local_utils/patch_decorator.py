import functools, inspect, sys

def patch( orig_func, target=None, verbose=False):
   
    def decorator(new_func, target=target):

        def wrapper(*a, **kw):
            return new_func(orig_func, *a, **kw)

        if inspect.ismethod(orig_func):
            if target is None:
                target =  orig_func.im_class
            if verbose:
                print "replace method", orig_func, "in", target, "with", new_func
            setattr(target, orig_func.__name__, wrapper)
        elif inspect.isfunction(orig_func):
            if target is None:
                target = sys.modules[orig_func.__module__]
            if verbose:
                print "replace function", orig_func, "in", target, "with", new_func
            setattr(target, orig_func.func_name, wrapper)
        else:
            raise Exception("can not wrap %s " % orig_func)

        return wrapper # not needed as new_func is not modified at all

    return decorator
