import numpy as np
import re

__doc__ = """

Working with tables relies on so called ``Expressions`` 


"""

def le(a, x):
    return np.searchsorted(a, x, 'right')-1

def ge(a, x):
    return np.searchsorted(a, x, 'left')

def lt(a, x):
    return np.searchsorted(a, x, 'left') - 1

def gt(a, x):
    return np.searchsorted(a, x, 'right')


"""
spaltentypen: int, long, float, bool, str, dict, tuple, set, list, object

numerisch: int, long, bool, float   -> werden IMMER in np.ma.core.MaskedArray verwaltet
alle andern: als list verwaltet.

"""

_basic_num_types = [int, long, float, bool]
_basic_types = [int, long, float, bool, str, type(None) ]
#_iterables = [list, np.ndarray]

def isNumericList(li):
    if not isinstance(li, list):
        return False
    innertypes = set(type(item) for item in li)
    innertypes.discard(type(None))
    return all(i in _basic_num_types for i in innertypes)

def saveeval(expr, ctx):
    #try:
        return  expr._eval(ctx)
    #except Exception, e:
    #    raise Exception("eval of %s failed: %s" % (expr, e))

def container(type_):
    if type_ in [ int, long, float, bool]:
        return np.ma.core.MaskedArray
    if hasattr(type_, "__mro__") and np.number in type_.__mro__:
        return np.ma.core.MaskedArray
    return list

def tolist(collection):
    if type(collection) == list:
        return collection
    return np.array(collection).tolist()

def cleanup(type_):
    # keeps pure python types as they are, converts
    # numpy values to their python equivalent:
    if type_ in [ int, long, float, bool, str, list, dict, tuple, set, object]:
        return type_
    if hasattr(type_, "__mro__"):
        mro = type_.__mro__
        if np.number in mro:
            if np.bool_ in mro:
                return bool
            if np.integer in mro:
                return int
            if np.floating in mro:
                return float
    return object
    raise Exception("do not know how to handle %s" % type_)

def common_type(t1, t2):
    if t1==t2:
        return t1

    if t1 in _basic_num_types and t2 in _basic_num_types:
        if float in t1 or float in t2:
            return float
        if long in t1 or long in t2:
            return long
        if int in t1 or int in t2:
            return int
        return bool

    raise Exception("can not coerce types %s and %s" % (t1, t2))


class BaseExpression(object):

    """
    BaseClass for Expressions. For two Expressions ``t1`` and ``t2``
    this class generates new Expressions as follows:

    * Comparison Operators:

     *  ``t1 <= t2``
     *  ``t1 < t2``
     *  ``t1 >= t2``
     *  ``t1 > t2``
     *  ``t1 == t2``
     *  ``t1 != t2``

    * Algebraic Operators:

      *  ``t1 + t2``
      *  ``t1 - t2``
      *  ``t1 * t2``
      *  ``t1 > t2``

    * Logic Operators:

      *  ``t1 & t2``
      *  ``t1 | t2``
      *  ``t1 ^  t2``
      *  ``~t1``

      .. note::

          Due to some Python internals, these operators have a low precedence,
          so you have to use parantheses like ``(t1 <= t2) & (t1 > t3)```

    """

    def __init__(self, left, right):
        if not isinstance(left, BaseExpression):
            left = Value(left)
        if not isinstance(right, BaseExpression):
            right = Value(right)
        self.left = left
        self.right = right

    def _evalsize(self, ctx):
        # size of result when _eval is called:
        sl = self.left._evalsize(ctx)
        sr = self.right._evalsize(ctx)
        if sl==1: # numpy and list coercing
            return sr
        if sr==1: # numpy and list coercing
            return sl
        if sr==sl:
            return sl
        raise Exception("sizes %d and %d do not fit" % (sl, sr))

    def __nonzero__(self):
        """ this one raises and exception if "and" or "or" are used to
            build expressions.
            "and" and "or" can not be used as there are no methods
            to overload these. Combining expressions this way allways
            results in a call to this method to determine their
            equivalent "boolean value".

        """
        raise Exception("can not convert %s to boolean value" % self)

    def __str__(self):
        return "(%s %s %s)" % (self.left, self.symbol, self.right)

    def __ge__(self, other):
        return GeExpression(self, other)

    def __gt__(self, other):
        return GtExpression(self, other)

    def __le__(self, other):
        return LeExpression(self, other)

    def __lt__(self, other):
        return LtExpression(self, other)

    def __eq__(self, other):
        return EqExpression(self, other)

    def __ne__(self, other):
        return NeExpression(self, other)

    def __add__(self, other):
        return BinaryExpression(self, other, lambda a,b: a+b, "+", None)

    def __radd__(self, other):
        return BinaryExpression(other, self, lambda a,b: a+b, "+", None)

    def __sub__(self, other):
        return BinaryExpression(self, other, lambda a,b: a-b, "-", None)

    def __rsub__(self, other):
        return BinaryExpression(other, self, lambda a,b: a-b, "-", None)

    def __mul__(self, other):
        return BinaryExpression(self, other, lambda a,b: a*b, "*", None)

    def __rmul__(self, other):
        return BinaryExpression(other, self, lambda a,b: a*b, "*", None)

    def __div__(self, other):
        return BinaryExpression(self, other, lambda a,b: a/b, "/", None)

    def __rdiv__(self, other):
        return BinaryExpression(self, other, lambda a,b: a/b, "/", None)

    def __and__(self, other):
        return AndExpression(self, other)

    # no rand / ror / rxor: makes sometimes trouble with precedence of
    # terms.....

    def __or__(self, other):
        return OrExpression(self, other)

    def __xor__(self, other):
        return XorExpression(self, other)

    def __invert__(self):
        return FunctionExpression(lambda a: not a, "not %s", self)

    def _neededColumns(self):
        lc = self.left._neededColumns()
        if hasattr(self, "right"):
            return lc + self.right._neededColumns()
        return lc

    def startswith(self, other):
        """
        For two string valued expressions ``a`` and ``b`` the expression
        ``a.startswith(b)``
        evaluates if the string ``a`` starts with the string
        ``b``. The latter might be a fixed string, as ``tab.mf.startswith("H2")``

        """

        return BinaryExpression(self, other, lambda a,b: a.startswith(b), "%s.startswith(%s)", bool)

    def contains(self, other):
        """
        ``a.contains(b)`` tests if ``b in a``.
        """
        return BinaryExpression(self, other, lambda a,b: b in a, "%s.contains(%s)", bool)


    def containsElement(self, element):
        """
        For a string valued expression ``a`` which represents a molecular formula
        the expressions ``a.containsElement(element)`` tests if the
        given ``element`` is contained in ``a``.

        Example:  ``tab.mf.containsElement("Na")``
        """
        return BinaryExpression(self, element,\
               lambda a,b: b in re.findall("([A-Z][a-z]?)\d*", a),\
               "%s.containsElement(%s)", bool)

    def isIn(self, li):
        """
        ``a.isIn(li)`` tests if the value of ``a`` is contained in a list ``li``.

        Example: ``tab.id.isIn([1,2,3])``

        """
        return FunctionExpression(lambda a, b=li: a in b, "%%s.isIn(%s)"%li, self)

    def inRange(self, minv, maxv):
        """
        ``a.inRange(low, up)`` tests if ``low <= a <= up``.

        Example: ``tab.rt.inRange(60, 120)``
        """

        return (self>=minv) & (self<=maxv)

    def approxEqual(self, what, tol):
        """

        ``a.approxEqual(b, tol)`` tests if ``|a-b| <= tol``.

        Example: ``tab.mz.approxEqual(meatbolites.mz, 0.001)``
        """
        return self.inRange(what-tol, what+tol)

    def thenElse(self, then, else_):
        """
        ``a.thenElse(b, c)`` avaluates to ``b`` if ``a`` is *True*, if not it
        evaluates to ``c``.
        """

        return IfThenElse(self, then, else_)

    def ifNotNoneElse(self, other):
        """
        ``a.ifNotNoneElse(b)`` evaluates to ``a`` if a is not *None*, else
        it evaluates to ``b``.

        Example: ``tab.rt.replaceColumn("rt", rt.ifNotNoneElse(tab.rt_default))``

        """
        return (self==None).thenElse(other, self)

    def pow(self, exp):
        """
        ``a.pow(b)`` evaluates to ``a**b``.

        Example: ``tab.rmse.pow(2)``
        """
        return self.apply(lambda v, exp=exp: v**exp)

    def apply(self, fun):
        """
        t.apply(*fun*) results in an expression which applies *fun* to the
        values in t if evaluated.

        Example::  ``tab.addColumn("amplitude", tab.time.apply(sin))``
        """
        return FunctionExpression(fun, str(fun), self)

    @property
    def min(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its minimal value.

        Example: ``tab.rt.min``
        """
        return AggregateExpression(self, lambda v: min(v), "min(%s)", None)

    @property
    def max(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its maximal value.

        Example: ``tab.rt.max``
        """
        return AggregateExpression(self, lambda v: max(v), "max(%s)", None)

    @property
    def sum(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its sum.

        Example: ``tab.area.sum``

        """
        return AggregateExpression(self, lambda v: sum(v), "sum(%s)", None)

    @property
    def mean(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its mean.

        Example: ``tab.area.mean``
        """
        return AggregateExpression(self, lambda v: np.mean(v).tolist(),\
                                   "mean(%s)", None)

    @property
    def std(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its standard deviation.

        Example: ``tab.area.std``
        """
        return AggregateExpression(self, lambda v: np.std(v).tolist(),\
                                   "stddev(%s)", None)
    @property
    def len(self):
        """
        **This expression is depreciated**. Please use
        :py:meth:`~libms.DataStructures.Expressions.BaseExpression.count`
        instead.
        """
        return AggregateExpression(self, lambda v: len(v), "len(%s)",\
                                   int, ignoreNone=False)

    @property
    def count(self):
        """
        This is an **aggretation expression** which evaluates an
        column expression to the number of values in the column.

        Example:: ``tab.id.len``
        """
        return AggregateExpression(self, lambda v: len(v), "count(%s)",\
                                   int, ignoreNone=False)

    @property
    def countNone(self):
        """
        This is an **aggretation expression** which evaluates an
        Column expression to the number of None values in it.
        """
        return AggregateExpression(self,\
                                   lambda v: sum(1 for vi in v if vi is None),\
                                   "countNone(%s)", int, ignoreNone=False)
    @property
    def countNotNone(self):
        """
        This is an **aggretation expression** which evaluates an
        Column expression to the number of values != None in it.
        """
        return AggregateExpression(self,\
                               lambda v: sum(1 for vi in v if vi is not None),\
                               "countNotNone(%s)", int, ignoreNone=False)

    @property
    def hasNone(self):
        """
        This is an **aggretation expression** which evaluates an
        Column expression to *True* if and only if the column contains a *None* value.
        """
        return self.countNone > 0
        return AggregateExpression(self, lambda v: int(None in v) , "hasNone(%s)",\
                                   bool, ignoreNone=False)

    @property
    def uniqueNotNone(self):
        """
        This is an **aggretation expression**. If applied to an expression ``t``
        ``t.uniqueNotNone`` evaluates to
        ``v`` if ``t`` only contains two values ``v`` and ``None``.
        Else it raises an Exception.

        Example: ``tab.peakmap.uniqueNotNone``
        """
        def select(values):
            diff = set(v for v in values if v is not None)
            if len(diff) == 0:
                raise Exception("only None values in %s" % self)
            if len(diff) > 1:
                raise Exception("more than one None value in %s" % self)
            return [v for v in values if v is not None][0]
        return AggregateExpression(self, select, "uniqueNotNone(%s)",\
                                   None, ignoreNone=False)

    def __call__(self):
        val, _ = self._eval(ctx=None)
        # works for lists, nubmers, objects: convers inner numpy dtypes
        # to python types if present, else does nothing !!!!
        return np.array(val).tolist()

    def toTable(self, colName, fmt=None, type_=None, title="", meta=None):
        """
        Generates a one column :py:class:`~libms.DataStructures.Table` from an expession.

        Example: ``tab = substances.name.toTable()``
        """
        from Table import Table
        return Table.toTable(colName, self(), fmt, type_, title, meta)



class CompExpression(BaseExpression):

    # comparing to None is allowed by default, but is overidden in some
    #  sublassess,
    # as eg  None <= x or None >=x give hard to predict results  and  is
    # very error prone:
    allowNone = True

    def _eval(self, ctx):
        lhs, ixl, tl = saveeval(self.left, ctx)
        rhs, ixr, tr = saveeval(self.right, ctx)

        assert len(lhs) <= 1 or len(rhs)<=1 or len(lhs) == len(rhs),\
            "sizes do not fit"

        if len(lhs) == 0 or len(rhs)==0:
            return np.zeros((0,), dtype=np.bool), None, bool

        if tl in _basic_num_types and tr in _basic_num_types:
            if ixl != None  and len(rhs) == 1:
                return self.fastcomp(lhs, rhs[0]), None, bool
            if ixr != None  and len(lhs) == 1:
                return self.rfastcomp(lhs, lhs[0]), None, bool
            return self.comparator(lhs, rhs), None, bool

        if len(lhs) == 1:
            l = lhs[0]
            if l is None and tr in _basic_num_types:
                if self.symbol == "==":
                    values = rhs.mask
                elif self.symbol == "!=":
                    values = ~rhs.mask
                else:
                    values = np.zeros((len(rhs),), dtype=bool)
            else:
                values = [ self.comparator(l,r) for r in  rhs]
        elif len(rhs) == 1:
            r = rhs[0]
            if r is None and tl in _basic_num_types:
                if self.symbol == "==":
                    values = lhs.mask
                elif self.symbol == "!=":
                    values = ~lhs.mask
                else:
                    values = np.zeros((len(lhs),), dtype=bool)
            else:
                values = [ self.comparator(l,r) for l in  lhs]
        else:
            values = [ self.comparator(l,r) for (l,r) in zip(lhs, rhs)]
        return np.ma.array(values), None, bool


def Range(start, end, len):
    rv = np.zeros((len,), dtype=np.bool)
    rv[start:end] = True
    return rv

class LtExpression(CompExpression):

    symbol = "<"
    comparator = lambda self, a, b: a < b
    allowNone = False

    def fastcomp(self, vec, refval):
        i0 = lt(vec, refval)
        return Range(0, i0+1, len(vec))

    def rfastcomp(self, refval, vec):
        # refval < vec
        i0 = gt(vec, refval)
        return Range(i0, len(vec), len(vec))

class GtExpression(CompExpression):

    symbol = ">"
    comparator = lambda self, a, b: a > b
    allowNone = False

    def fastcomp(self, vec, refval):
        # ix not used, we know that vec is sorted
        i0 = gt(vec, refval)
        return Range(i0, len(vec), len(vec))

    def rfastcomp(self, refval, vec):
        # refval > vec
        i0 = lt(vec, refval)
        return Range(0, i0+1, len(vec))

class LeExpression(CompExpression):

    symbol = "<="
    comparator = lambda self, a, b: a <= b
    allowNone = False

    def fastcomp(self, vec, refval):
        # ix not used, we know that vec is sorted
        i0 = le(vec, refval)
        return Range(0, i0+1, len(vec))

    def rfastcomp(self, refval, vec):
        # refval < vec
        i0 = ge(vec, refval)
        return Range(i0, len(vec), len(vec))

class GeExpression(CompExpression):

    symbol = ">="
    comparator = lambda self, a, b: a >= b
    allowNone = False

    def fastcomp(self, vec, refval):
        i0 = ge(vec, refval)
        return Range(i0, len(vec), len(vec))

    def rfastcomp(self, refval, vec):
        # refval < vec
        i0 = le(vec, refval)
        return Range(0, i0+1, len(vec))

class NeExpression(CompExpression):

    symbol = "!="
    comparator = lambda self, a, b: a != b
    def fastcomp(self, vec, refval):
        i0 = ge(vec, refval)
        i1 = le(vec, refval)
        return  ~Range(i0, i1+1, len(vec))

    def rfastcomp(self, refval, vec):
        # refval < vec
        i0 = le(vec, refval)
        i1 = ge(vec, refval)
        return ~Range(i1, i0+1, len(vec))

class EqExpression(CompExpression):

    symbol = "=="
    comparator = lambda self, a, b: a == b

    def fastcomp(self, vec, refval):
        i0 = ge(vec, refval)
        i1 = le(vec, refval)
        return Range(i0, i1+1, len(vec))

    def rfastcomp(self, refval, vec):
        # refval < vec
        i0 = le(vec, refval)
        i1 = ge(vec, refval)
        return Range(i1, i0+1, len(vec))


class BinaryExpression(BaseExpression):

    # TODO: refactor dependcies based on symbol, -> extra flags in
    # constructor.

    def __init__(self, left, right, efun, symbol, restype):
        super(BinaryExpression, self).__init__(left, right)
        self.efun = efun
        self.symbol = symbol
        self.restype = restype

    def _eval(self, ctx):
        lvals, idxl, tl = saveeval(self.left, ctx)
        rvals, idxr, tr = saveeval(self.right, ctx)

        ll = len(lvals)
        lr = len(rvals)
        if ll> 1 and lr>1 and ll != lr:
            raise Exception("can not cast sizes %d and %d" % (ll, lr))
        if tl in _basic_num_types and tr in _basic_num_types:
            res = self.efun(lvals, rvals)
            if self.restype is not None:
                res = res.astype(self.restype)
            return res, None, cleanup(res.dtype)

        ct = self.restype or common_type(tl,tr)

        assert ll==1 or lr==1 or ll==lr, "sizes do not fit"

        if ll==1:
            values = [ self.efun(lvals[0], r) for r in rvals ]
        elif lr==1:
            values = [ self.efun(l, rvals[0]) for l in lvals ]
        else:
            values = [ self.efun(l, r) for (l, r) in zip(lvals, rvals) ]

        return values, None , ct



class __UnaryExpression(BaseExpression):

    def __init__(self, left, efun, funname):
        if not isinstance(left, BaseExpression):
            left = Value(left)
        self.left = left
        self.efun = efun
        self.funname = funname

    def _eval(self, ctx):
        vals, _, type_ = saveeval(self.left, ctx)
        if type(vals) in _iterables:
            return np.ma.array([self.efun(v) for v in vals]), None
        return self.efun(vals), None

    def __str__(self):
        return self.funname % self.left

class AggregateExpression(BaseExpression):

    def __init__(self, left, efun, funname, restype, ignoreNone=True):
        if not isinstance(left, BaseExpression):
            left = Value(left)
        self.left = left
        self.efun = efun
        self.funname = funname
        self.restype = restype
        self.ignoreNone = ignoreNone

    def _eval(self, ctx):
        vals, _, _ = saveeval(self.left, ctx)
        if self.ignoreNone:
            vals  = [ v for v in vals if v is not None]
        if len(vals):
            result = [self.efun(vals)]
            result = container(type(result[0]))(result)
            type_ = cleanup(type(result[0]))
            return result, None, type_
        return [None], None, self.restype or type_

    def __str__(self):
        return self.funname % self.left


class LogicExpression(BaseExpression):

    def __init__(self, left, right):
        super(LogicExpression, self).__init__(left, right)
        if right.__class__ == Value and type(right.value) != bool:
            print "warning: parentesis for logic op set ?"

    def richeval(self, lvals, rvals, tl, tr,  boolop):

        if len(lvals) == 1:
            values = [ boolop(lvals[0], r) for r in rvals ]
        elif len(rvals) == 1:
            values = [ boolop(l, rvals[0]) for l in lvals ]
        else:
            assert len(lvals) == len(rvals)
            values = [ boolop(l, r) for (l,r) in zip(lvals, rvals) ]

        ct = common_type(tl, tr)
        if ct in _basic_types:
            values = np.ma.array([ ct(v) for v in values ])

        return values, None, ct


class AndExpression(LogicExpression):

    symbol = "&"
    def _eval(self, ctx):
        lhs, _, tlhs = saveeval(self.left, ctx)
        if len(lhs) == 1 and not lhs[0]:
            return np.zeros((self.right._evalsize(ctx),), dtype=np.bool), None, bool
        rhs, _, trhs = saveeval(self.right, ctx)
        if len(rhs) == 1 and not rhs[0]:
            return np.zeros((self.right._evalsize(ctx),), dtype=np.bool), None, bool
        if len(lhs) == 1: # lhs[0] is True
            return rhs, _, trhs
        if len(rhs) == 1: # rhs[0] is True
            return lhs, _, tlhs
        return self.richeval(lhs, rhs, tlhs, trhs, lambda a,b: a and b)

class OrExpression(LogicExpression):

    symbol = "|"
    def _eval(self, ctx):
        lhs, _, tlhs = saveeval(self.left, ctx)
        if len(lhs) == 1 and lhs[0]:
            return np.ones((self.right._evalsize(ctx),), dtype=np.bool), None, bool
        rhs, _, trhs = saveeval(self.right, ctx)
        if len(rhs) == 1 and rhs[0]:
            return np.ones((self.right._evalsize(ctx),), dtype=np.bool), None, bool
        if len(lhs) == 1: # lhs[0] is False
            return rhs, _, trhs
        if len(rhs) == 1: # rhs[0] is False
            return lhs, _, tlhs
        return self.richeval(lhs, rhs, tlhs, trhs, lambda a,b: a or b), None, bool

class XorExpression(LogicExpression):

    symbol = "^"
    def _eval(self, ctx):
        lhs, _, tlhs = saveeval(self.left, ctx)
        rhs, _, trhs = saveeval(self.right, ctx)
        if len(lhs) ==1 and not lhs[0]:
            return rhs, _, trhs
        if len(rhs) ==1 and not rhs[0]:
            return lhs, _, tlhs
        return self.richeval(lhs, rhs, tlhs, trhs, lambda a,b: (a and not b) | (not a and b)), None, bool


class Value(BaseExpression):

    def __init__(self, value):
        self.value = value

    def _eval(self, ctx):
        tt = cleanup(type(self.value))
        return container(tt)([self.value]), None, tt

    def __str__(self):
        return repr(self.value)

    def _evalsize(self, ctx):
        return 1

    def _neededColumns(self):
        return []



class FunctionExpression(BaseExpression):

    def __init__(self, efun, efunname, child):
        if not isinstance(child, BaseExpression):
            child = Value(child)
        self.child = child
        self.efun = efun
        self.efunname = efunname

    def _eval(self, ctx):
        values, index, type_ = saveeval(self.child, ctx)
        if type(values) == np.ndarray:
            if type(self.efun) == np.ufunc:
                return self.efun(values), None, float
        new_values = [self.efun(v) if v is not None else None for v in values]
        if type_ in _basic_types:
            new_values = np.array(new_values)
            return new_values, None, cleanup(new_values.dtype)
        types = set(type(v) for v in new_values)
        common = int
        for t in types:
            common = common_type(t, common)
        return new_values, None, common

    def __str__(self):
        return "%s(%s)" % (self.efunname, self.child)

    def _evalsize(self, ctx):
        return self.child._evalsize(ctx)

    def _neededColumns(self):
        return self.child._neededColumns()



class IfThenElse(BaseExpression):

    def __init__(self, e1, e2, e3):
        if not isinstance(e1, BaseExpression):
            e1 = Value(e1)
        if not isinstance(e2, BaseExpression):
            e2 = Value(e2)
        if not isinstance(e3, BaseExpression):
            e3 = Value(e3)
        self.e1 = e1
        self.e2 = e2
        self.e3 = e3

    def _eval(self, ctx):
        values1, _, t1 = saveeval(self.e1, ctx)
        assert t1 == bool

        eval2 = saveeval(self.e2, ctx)
        eval3 = saveeval(self.e3, ctx)

        eval_size = self._evalsize(ctx)
        if len(values1) == 1:
            return eval2 if values1[0] else eval3

        assert len(values1) == eval_size

        values2, ix2, t2 = eval2
        values3, ix3, t3 = eval3

        ct = common_type(t2, t3)
        if type(values2) == type(values3) == np.ndarray:
            return np.where(values1, values2, values3), _, ct

        return [ val2 if val1 else val3 for (val1, val2, val3) \
                in zip(values1, values2, values3) ], _, ct


    def __str__(self):
        return "%s(%s)" % (self.efunname, self.child)

    def _evalsize(self, ctx):
        s2 = self.e2._evalsize(ctx)
        s3 = self.e3._evalsize(ctx)
        if s2 == 1 or s3==1:
            return max(s2, s3)
        if s2 != s3:
            raise Exception("sizes %d and %d do not fit!"% (s2,s3))
        return s2

    def _neededColumns(self):
        return self.e1._neededColumns() \
               + self.e2._neededColumns() \
               + self.e3._neededColumns()






class ColumnExpression(BaseExpression):

    """
    A ``ColumnExpression`` is the simplest form of an ``Expression``.
    It is generated from a ``Table`` ``t`` as ``t.x`` or by calling
    ``t.getColumn("x")``.

    """

    def __init__(self, table, colname, idx, type_):
        self.table = table
        self.colname = colname
        self.idx = idx
        self.type_ = type_

    def _setupValues(self):
        # delayed lazy evaluation
        if not hasattr(self, "_values"):
            self._values = [ row[self.idx] for row in self.table.rows ]

    @property
    def values(self):
        self._setupValues()
        return self._values
        #raise AttributeError("%s has no attribute %s" % (self, name))

    def __getstate__(self):
        dd = self.__dict__.copy()
        if "_values" in dd:
            del dd["_values"]
        return dd

    def __setstate__(self, dd):
        self.__dict__ = dd

    def __iter__(self):
        self._setupValues()
        return iter(self.values)

    def _eval(self, ctx):
        # self.values is allways a list ! for speedinig up things
        # we convert numerical types to np.ma.array during evaluation
        # of expressions
        if ctx is None:
            if self.type_ in _basic_num_types:
                mask = [ v is None for v in self.values ]
                values = map(lambda v: v or 0, self.values)
                return np.ma.array(values, mask = mask, dtype = self.type_), None, self.type_
                #return np.array(self.values), None, self.type_
            return self.values, None, self.type_
        cx = ctx.get(self.table)
        if cx is None:
            raise Exception("context not correct. "\
                            "did you use wrong table in expression ?")
        values, idx, type_ = cx.get(self.colname)
        if type_ in _basic_num_types:
            values = np.array(values)
            mask = [ v is None for v in self.values ]
            values = map(lambda v: v or 0, self.values)
            values = np.ma.array(values, mask = mask, dtype = self.type_)
        return values, idx, type_

    def __str__(self):
        if not hasattr(self, "colname"):
            raise Exception("colname missing")
        if not hasattr(self, "table"):
            raise Exception("table missing")
        if not hasattr(self.table, "_name"):
            raise Exception("table._name missing")
        return "%s.%s" % (self.table._name, self.colname)

    def _evalsize(self, ctx):
        if ctx is None:
            return len(self.values)
        cx = ctx[self.table]
        rv, _ = cx[self.colname]
        return len(rv)

    def _neededColumns(self):
        return [ (self.table, self.colname), ]

    def modify(self, operation):
        """
        Allows **inplace** modification of a Table column.

        Example: ``tab.time.modify(sin)`` replaces the content of in column
        ``time`` by its ``sin`` value.
        """

        self.table.replaceColumn(self.colname, map(operation, self.values))
        if hasattr(self, "_values"):
            del self._values

    def __iadd__(self, value):
        """
        Allows **inplace** modification of a Table column.

        Example: ``tab.id += 1``
        """
        self.modify(lambda v, value=value: v+value)
        return self

    def __isub__(self, value):
        """
        Allows **inplace** modification of a Table column.

        Example: ``tab.id -= 1``
        """
        self.modify(lambda v, value=value: v-value)
        return self

    def __imul__(self, value):
        """
        Allows **inplace** modification of a Table column.

        Example: ``tab.area *= 2``
        """
        self.modify(lambda v, value=value: v*value)
        return self

    def __idiv__(self, value):
        """
        Allows **inplace** modification of a Table column.

        Example: ``tab.area /= 3.141``
        """
        self.modify(lambda v, value=value: v/value)
        return self

