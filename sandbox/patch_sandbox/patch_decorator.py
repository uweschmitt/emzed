import functools, inspect

def patch( orig_func, target=None):
   
    def decorator(new_func, target=target):

        def wrapper(*a, **kw):
            return new_func(orig_func, *a, **kw)

        if inspect.ismethod(orig_func):
            if target is None:
                target =  orig_func.im_class
            setattr(target, orig_func.__name__, wrapper)
        elif inspect.isfunction(orig_func):
            if target is None:
                raise Exception("need target for pure functions")
            setattr(target, orig_func.func_name, wrapper)
        else:
            raise Exception("can not wrap %s " % orig_func)

        return wrapper # not needed as new_func is not modified at all

    return decorator
