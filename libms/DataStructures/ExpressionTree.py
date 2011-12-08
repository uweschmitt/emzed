import numpy as np
import re

def le(a, x):
    return np.searchsorted(a, x, 'right')-1

def ge(a, x):
    return np.searchsorted(a, x, 'left')

def lt(a, x):
    return np.searchsorted(a, x, 'left') - 1

def gt(a, x):
    return np.searchsorted(a, x, 'right')

_basic_num_types = [int, long, float]
_basic_types = [int, long, float, str, type(None) ]
_iterables = [list, np.ndarray]

def isNumericList(li):
    if not isinstance(li, list):
        return False
    innertypes = set(type(item) for item in li)
    innertypes.discard(None)
    return all(i in _basic_num_types for i in innertypes)

class Node(object):

    def __init__(self, left, right):
        if not isinstance(left, Node):
            left = Value(left)
        if not isinstance(right, Node):
            right = Value(right)
        self.left = left
        self.right = right

    def evalsize(self, ctx):
        # size of result when eval is called:
        sl = self.left.evalsize(ctx)
        sr = self.right.evalsize(ctx)
        if sl==1: # numpy and list coercing
            return sr
        if sr==1: # numpy and list coercing
            return sl
        if sr==sl:
            return sl
        raise Exception("sizes %d and %d do not fit" % (sl, sr))

    def __str__(self):
        return "(%s %s %s)" % (self.left, self.symbol, self.right)

    def __ge__(self, other):
        return GeNode(self, other)

    def __gt__(self, other):
        return GtNode(self, other)

    def __le__(self, other):
        return LeNode(self, other)

    def __lt__(self, other):
        return LtNode(self, other)

    def __eq__(self, other):
        return EqNode(self, other)

    def __ne__(self, other):
        return NeNode(self, other)

    def __add__(self, other):
        return BinaryExpression(self, other, lambda a,b: a+b, "+")

    def __radd__(self, other):
        return BinaryExpression(other, self, lambda a,b: a+b, "+")

    def __sub__(self, other):
        return BinaryExpression(self, other, lambda a,b: a-b, "-")

    def __rsub__(self, other):
        return BinaryExpression(other, self, lambda a,b: a-b, "-")

    def __mul__(self, other):
        return BinaryExpression(self, other, lambda a,b: a*b, "*")

    def __rmul__(self, other):
        return BinaryExpression(other, self, lambda a,b: a*b, "*")

    def __div__(self, other):
        return BinaryExpression(self, other, lambda a,b: a/b, "/")

    def __rdiv__(self, other):
        return BinaryExpression(self, other, lambda a,b: a/b, "/")

    def __and__(self, other):
        return AndNode(self, other)

    # no rand / ror / rxor: makes sometimes trouble with precedence of
    # terms.....

    def __or__(self, other):
        return OrNode(self, other)

    def __xor__(self, other):
        return XorNode(self, other)

    def __invert__(self):
        return InvertNode(self)

    def neededColumns(self):
        lc = self.left.neededColumns()
        if hasattr(self, "right"):
            return lc + self.right.neededColumns()
        return lc

    # some helper functions
    def startswith(self, other):
        return BinaryExpression(self, other, lambda a,b: a.startswith(b), "%s.startswith(%s)")

    def contains(self, other):
        return BinaryExpression(self, other, lambda a,b: b in a, "%s.contains(%s)")

    def containsElement(self, element):
        return BinaryExpression(self, element,\
               lambda a,b: b in re.findall("[A-Z][a-z]?\d*", a),\
               "%s.containsElement(%s)")

    def isIn(self, li):
        return UnaryExpression(self, lambda a, b=li: a in b, "%%s.isIn(%s)"%li)

    def inRange(self, minv, maxv):
        return (self>=minv) & (self<=maxv)

    def approxEqual(self, what, tol):
        return self.inRange(what-tol, what+tol)

    def thenElse(self, then, else_):
        return IfThenElse(self, then, else_)


class CompNode(Node):

    # comparing to None is allowed, is overidden in sublassess,
    # as eg  None <= x or None >=x give hard to predict results
    # and is very error prone
    allowNone = True 

    def eval(self, ctx):
        lhs, ixl = self.left.eval(ctx)
        rhs, ixr = self.right.eval(ctx)

        if ixl != None and type(rhs) in _basic_num_types:
            return self.fastcomp(lhs, rhs, ixl), None
        if ixr != None and type(lhs) in _basic_num_types:
            return self.rfastcomp(lhs, rhs, ixr), None

        if not self.allowNone:
            if lhs == None or rhs==None:
                raise Exception("comparing to None is not allowed")
            if type(lhs) in [list, np.ndarray] and None in set(lhs):
                raise Exception("comparing to None is not allowed")
            if type(rhs) in [list, np.ndarray] and None in set(rhs):
                raise Exception("comparing to None is not allowed")

        if isNumericList(lhs):
            lhs = np.array(lhs)
        if isNumericList(rhs):
            rhs = np.array(rhs)

        if type(lhs) in _basic_num_types and type(rhs)==np.ndarray:
            return self.comparator(lhs, rhs), None

        if type(lhs) ==np.ndarray and type(rhs) in _basic_num_types:
            return self.comparator(lhs, rhs), None

        if type(lhs) ==np.ndarray and type(rhs) ==np.ndarray:
            assert len(lhs) == len(rhs), "maybe you have a np.float value in "\
                                         "your table instead of a float"
            return self.comparator(lhs, rhs), None

        if type(lhs) in _basic_types and type(rhs) in _iterables:
            return np.array([ self.comparator(lhs, r) for r in  rhs]), None
        if  type(lhs) in _iterables and type(rhs) in _basic_types:
            return np.array([ self.comparator(l, rhs) for l in  lhs]), None

        if type(lhs) in _basic_types and type(rhs) in _basic_types:
            return self.comparator(lhs, rhs), None

        t0 = ""
        try:
            t0 = type(lhs[0])
        except:
            pass

        r0 = ""
        try:
            r0 = type(rhs[0])
        except:
            pass

        raise "Can not handle %r or %r, resp %s or %s" % (lhs, rhs, t0, r0)

def Range(start, end, len):
    rv = np.zeros((len,), dtype=np.bool)
    rv[start:end] = True
    return rv

class LtNode(CompNode):

    symbol = "<"
    comparator = lambda self, a, b: a < b
    allowNone = False

    def fastcomp(self, vec, refval, ix):
        i0 = lt(vec, refval)
        return Range(0, i0+1, len(vec))

    def rfastcomp(self, refval, vec, ix):
        # refval < vec
        i0 = gt(vec, refval)
        return Range(i0, len(vec), len(vec))

class GtNode(CompNode):

    symbol = ">"
    comparator = lambda self, a, b: a > b
    allowNone = False

    def fastcomp(self, vec, refval, ix):
        # ix not used, we know that vec is sorted
        i0 = gt(vec, refval)
        return Range(i0, len(vec), len(vec))

    def rfastcomp(self, refval, vec, ix):
        # refval > vec
        i0 = lt(vec, refval)
        return Range(0, i0+1, len(vec))

class LeNode(CompNode):

    symbol = "<="
    comparator = lambda self, a, b: a <= b
    allowNone = False

    def fastcomp(self, vec, refval, ix):
        # ix not used, we know that vec is sorted
        i0 = le(vec, refval)
        return Range(0, i0+1, len(vec))

    def rfastcomp(self, refval, vec, ix):
        # refval < vec
        i0 = ge(vec, refval)
        return Range(i0, len(vec), len(vec))

class GeNode(CompNode):

    symbol = ">="
    comparator = lambda self, a, b: a >= b
    allowNone = False

    def fastcomp(self, vec, refval, ix):
        i0 = ge(vec, refval)
        return Range(i0, len(vec), len(vec))

    def rfastcomp(self, refval, vec, ix):
        # refval < vec
        i0 = le(vec, refval)
        return Range(0, i0+1, len(vec))

class NeNode(CompNode):

    symbol = "!="
    comparator = lambda self, a, b: a != b
    def fastcomp(self, vec, refval, ix):
        i0 = ge(vec, refval)
        i1 = le(vec, refval)
        return  ~Range(i0, i1+1, len(vec))

    def rfastcomp(self, refval, vec, ix):
        # refval < vec
        i0 = le(vec, refval)
        i1 = ge(vec, refval)
        return ~Range(i1, i0+1, len(vec))

class EqNode(CompNode):

    symbol = "=="
    comparator = lambda self, a, b: a == b

    def fastcomp(self, vec, refval, ix):
        i0 = ge(vec, refval)
        i1 = le(vec, refval)
        return Range(i0, i1+1, len(vec))

    def rfastcomp(self, refval, vec, ix):
        # refval < vec
        i0 = le(vec, refval)
        i1 = ge(vec, refval)
        return Range(i1, i0+1, len(vec))


class BinaryExpression(Node):

    def __init__(self, left, right, efun, symbol):
        super(BinaryExpression, self).__init__(left, right)
        self.efun = efun
        self.symbol = symbol

    def eval(self, ctx):
        lval, idxl = self.left.eval(ctx)
        rval, idxr = self.right.eval(ctx)

        if isNumericList(lval):
                lval = np.array(lval)
        if isNumericList(rval):
            rval = np.array(rval)

        if type(lval) in _basic_num_types and type(rval) == np.ndarray:
            res = self.efun(lval, rval)
            # order preserving operations keep index idxr
            # c + vec, c * vec and c>0, c/vec and c<0 kepp order of vec
            # c - vec destroys it:
            if self.symbol == "+" or (self.symbol=="*" and lval > 0)\
                                  or (self.symbol=="/" and lval < 0):
                return res, idxr
            # else: loose index
            return res, None

        if  type(lval) == np.ndarray and type(rval) in _basic_num_types:
            res = self.efun(lval, rval)
            # order preserving operations keep index idxr
            # vec +/- c, vec */ c and c>0 keep order of vec
            if self.symbol in "+-" or (self.symbol in "*/" and rval > 0):
                return res, idxl
            # else: loose index
            return res, None

        if type(lval) == str and type(rval) == list:
            res = [self.efun(lval, r) for r in rval ]
            return res, None

        if type(rval) == str and type(lval) == list:
            res = [self.efun(l, rval) for l in lval ]
            return res, None

        # arrays are fast:
        if type(lval) == type(rval) == np.ndarray:
            if len(lval) != len(rval):
                raise Exception("sizes do not fit !")
            res = self.efun(lval, rval)
            return self.efun(lval, rval), None

        # all other variation (eg str, ...): 
        if type(lval) == list and type(rval) == list:
            if len(lval) != len(rval):
                raise Exception("sizes do not fit !")
            return [ self.efun(l,r) for (l,r) in zip(lval,rval) ], None

        # at least one is np.ndarray:
        if type(lval) in _iterables and type(rval) in _iterables:
            if len(lval) != len(rval):
                raise Exception("sizes do not fit !")
            return np.array([ self.efun(l,r) for (l,r) in zip(lval,rval) ]), None

        print lval, rval
        assert type(lval) in _basic_types and type(rval) in _basic_types
        return [self.efun(lval, rval)], None


class InvertNode(Node):

    def __init__(self, child):
        self.child = child

    def eval(self, ctx):
        val, _ = self.child.eval(ctx)
        if type(val) in _basic_types:
            return not val, None
        elif type(val) in _iterables:
            return np.array([ not v for v in val ]), None
        raise Exception("invert eval with%s not possible" % val)

    def __str__(self):
        return "~%s" % str(self.child)

    def neededColumns(self):
        return self.child.neededColumns()


class LogicNode(Node):

    def __init__(self, left, right):
        super(LogicNode, self).__init__(left, right)
        if right.__class__ == Value and type(right.value) != bool:
            print "warning: parentesis for logic op set ?"

    def richeval(self, l, r, bitop):
        if type(l) == bool and type(r) == bool:
            return bitop(l, r)
        elif type(l) == bool and type(r) == np.ndarray:
            return bitop(l, r)
        elif type(l) == np.ndarray and type(r) == bool:
            return bitop(l,r)
        elif type(l) == bool and type(r) == list:
            return np.array([bitop(l, ri) for ri in r])
        elif type(l) == list and type(r) == bool:
            return np.array([bitop(l, ri) for ri in r])
        elif type(l) == type(r) == np.ndarray:
            return bitop(l,r)
        elif type(l) in _iterables and type(r) in _iterables:
            return np.array([bitop(li, ri) for li,ri in zip(l,r)])
        raise Exception("bool op for %r and %r not defined" % (l, r))

class AndNode(LogicNode):

    symbol = "&"
    def eval(self, ctx):
        lhs, _ = self.left.eval(ctx)
        if type(lhs) == bool and not lhs:
            return np.zeros((self.right.evalsize(ctx),), dtype=np.bool), None
        rhs, _ = self.right.eval(ctx)
        return self.richeval(lhs, rhs, lambda a,b: a & b), None

class OrNode(LogicNode):

    symbol = "|"
    def eval(self, ctx):
        lhs, _ = self.left.eval(ctx)
        if type(lhs)==bool and lhs:
            return np.ones((self.right.evalsize(ctx),), dtype=np.bool), None
        rhs, _ = self.right.eval(ctx)
        return self.richeval(lhs, rhs, lambda a,b: a | b), None

class XorNode(LogicNode):

    symbol = "^"
    def eval(self, ctx):
        lhs, _ = self.left.eval(ctx)
        rhs, _ = self.right.eval(ctx)
        return self.richeval(lhs, rhs, lambda a,b: (a & ~b) | (~a & b)), None


class Value(Node):

    def __init__(self, value):
        self.value = value
    def eval(self, ctx):
        return self.value, None

    def __str__(self):
        return repr(self.value)

    def evalsize(self, ctx):
        return 1

    def neededColumns(self):
        return []


class UnaryExpression(Node):

    def __init__(self, left, efun, funname):
        self.left = left
        self.efun = efun
        self.funname = funname

    def eval(self, ctx):
        vals, index = self.left.eval(ctx)
        if type(vals) in _iterables:
            return np.array([self.efun(v) for v in vals]), None
        return self.efun(vals), None

    def __str__(self):
        return self.funname % self.left


class FunctionExpression(Node):

    def __init__(self, efun, efunname, child):
        self.child = child
        self.efun = efun
        self.efunname = efunname

    def eval(self, ctx):
        vals, index = self.child.eval(ctx)
        return self.efun(vals), None

    def __str__(self):
        return "%s(%s)" % (self.efunname, self.child)

    def evalsize(self, ctx):
        return self.child.evalsize(ctx)

    def neededColumns(self):
        return self.child.neededColumns()



class IfThenElse(Node):

        def __init__(self, e1, e2, e3):
            self.e1 = e1
            self.e2 = e2
            self.e3 = e3

        def eval(self, ctx):
            e1, _ = self.e1.eval(ctx)
            e2, _ = self.e2.eval(ctx)
            e3, _ = self.e3.eval(ctx)

            size = self.evalsize(ctx)
            if size == 1:
                return e2 if e1 else e3, None
            if not type(e1) in _iterables:
                e1 = [ e1 ] * size
            if not type(e2) in _iterables:
                e2 = [ e2 ] * size
            if not type(e3) in _iterables:
                e3 = [ e3 ] * size

            return [ e2i if e1i else e3i for (e1i, e2i, e3i)
                     in zip(e1, e2, e3) ], None


        def __str__(self):
            return "%s(%s)" % (self.efunname, self.child)

        def evalsize(self, ctx):
            return max((self.e1.evalsize(ctx),
                        self.e2.evalsize(ctx),
                        self.e3.evalsize(ctx)))

        def neededColumns(self):
            return self.e1.neededColumns() \
                   + self.e2.neededColumns() \
                   + self.e3.neededColumns()



def wrapFun(name):
    def wrapper(x):
        origfun = getattr(np, name)
        if isinstance(x,Node):
            return FunctionExpression(origfun, name,  x)
        return origfun(x)
    return wrapper

log = wrapFun("log")
exp = wrapFun("exp")
sin = wrapFun("sin")
cos = wrapFun("cos")
sqrt = wrapFun("sqrt")


class Column(Node):

    def __init__(self, table, colname, values):
        self.table = table
        self.colname = colname
        self.values = values

    def __iter__(self):
        return iter(self.values)

    def getValues(self):
        return self.values

    def eval(self, ctx):
        cx = ctx[self.table]
        return cx[self.colname]

    def __str__(self):
        return "%s.%s" % (self.table._name, self.colname)

    def evalsize(self, ctx):
        cx = ctx[self.table]
        rv, _ = cx[self.colname]
        if type(rv) in _basic_types:
            return 1
        return len(rv)

    def neededColumns(self):
        return [ (self.table, self.colname), ]



