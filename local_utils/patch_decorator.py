import functools, inspect, sys

try:
    LLL
except:
    LLL = lambda s: None

def replace( orig_func, target=None, verbose=False):
   
    def decorator(new_func, target=target):

        def wrapper(*a, **kw):
            return new_func(*a, **kw)

        wrapper.isPatched = True

        if inspect.ismethod(orig_func):
            if target is None:
                target =  orig_func.im_class
            LLL.debug("replace method %s in %s with %s" %( orig_func, target, new_func))
            setattr(target, orig_func.__name__, wrapper)
            setattr(target, "_orig_%s" % orig_func.__name__, orig_func)
        elif inspect.isfunction(orig_func):
            if target is None:
                target = sys.modules[orig_func.__module__]
            LLL.debug("replace function %s in %s with %s" %( orig_func, target, new_func))
            setattr(target, orig_func.func_name, wrapper)
            setattr(target, "_orig_%s" % orig_func.__name__, orig_func)
        else:
            raise Exception("can not wrap %s " % orig_func)

        return wrapper # not needed as new_func is not modified at all

    return decorator


def add(target, verbose=False):

    def decorator(new_func, target=target):

        LLL.debug("add %s to %s" % (new_func, target))
        setattr(target, new_func.__name__, new_func)

    return decorator
