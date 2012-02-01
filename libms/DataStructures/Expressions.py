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

_basic_num_types = [int, long, float]
_basic_types = [int, long, float, str, type(None) ]
_iterables = [list, np.ndarray]

def isNumericList(li):
    if not isinstance(li, list):
        return False
    innertypes = set(type(item) for item in li)
    innertypes.discard(type(None))
    return all(i in _basic_num_types for i in innertypes)

def saveeval(expr, ctx):
    try:
        return  expr._eval(ctx)
    except Exception, e:
        raise Exception("eval of %s failed: %s" % (expr, e))

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
        return AndExpression(self, other)

    # no rand / ror / rxor: makes sometimes trouble with precedence of
    # terms.....

    def __or__(self, other):
        return OrExpression(self, other)

    def __xor__(self, other):
        return XorExpression(self, other)

    def __invert__(self):
        return UnaryExpression(self, lambda a: not a, "not %s")

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

        return BinaryExpression(self, other, lambda a,b: a.startswith(b), "%s.startswith(%s)")

    def contains(self, other):
        """
        ``a.contains(b)`` tests if ``b in a``.
        """
        return BinaryExpression(self, other, lambda a,b: b in a, "%s.contains(%s)")


    def containsElement(self, element):
        """
        For a string valued expression ``a`` which represents a molecular formula
        the expressions ``a.containsElement(element)`` tests if the
        given ``element`` is contained in ``a``.

        Example:  ``tab.mf.containsElement("Na")``
        """
        return BinaryExpression(self, element,\
               lambda a,b: b in re.findall("([A-Z][a-z]?)\d*", a),\
               "%s.containsElement(%s)")

    def isIn(self, li):
        """
        ``a.isIn(li)`` tests if the value of ``a`` is contained in a list ``li``.

        Example: ``tab.id.isIn([1,2,3])``

        """
        return UnaryExpression(self, lambda a, b=li: a in b, "%%s.isIn(%s)"%li)

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
        This applies a function *fun* to an expression.

        Example::  ``tab.time.apply(sin)``
        """
        return FunctionExpression(fun, str(fun), self, False)

    @property
    def min(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its minimal value.

        Example: ``tab.rt.min``
        """
        return AggregateExpression(self, lambda v: min(v), "min(%s)")

    @property
    def max(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its maximal value.

        Example: ``tab.rt.max``
        """
        return AggregateExpression(self, lambda v: max(v), "max(%s)")

    @property
    def sum(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its sum.

        Example: ``tab.area.sum``

        """
        return AggregateExpression(self, lambda v: sum(v), "sum(%s)")

    @property
    def mean(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its mean.

        Example: ``tab.area.mean``
        """
        return AggregateExpression(self, lambda v: np.mean(v).tolist(),\
                                   "mean(%s)")

    @property
    def std(self):
        """
        This is an **aggretation expression** which evaluates an
        expression to its standard deviation.

        Example: ``tab.area.std``
        """
        return AggregateExpression(self, lambda v: np.std(v).tolist(),\
                                   "stddev(%s)")
    @property
    def len(self):
        """
        **This expression is depreciated**. Please use
        :py:meth:`~libms.DataStructures.Expressions.BaseExpression.count`
        instead.
        """
        return AggregateExpression(self, lambda v: len(v), "len(%s)",\
                                   ignoreNone=False)

    @property
    def count(self):
        """
        This is an **aggretation expression** which evaluates an
        column expression to the number of values in the column.

        Example:: ``tab.id.len``
        """
        return AggregateExpression(self, lambda v: len(v), "count(%s)",\
                                   ignoreNone=False)

    @property
    def countNone(self):
        """
        This is an **aggretation expression** which evaluates an
        Column expression to the number of None values in it.
        """
        return AggregateExpression(self,\
                                   lambda v: sum(1 for vi in v if vi is None),\
                                   "countNone(%s)", ignoreNone=False)
    @property
    def countNotNone(self):
        """
        This is an **aggretation expression** which evaluates an
        Column expression to the number of values != None in it.
        """
        return AggregateExpression(self,\
                               lambda v: sum(1 for vi in v if vi is not None),\
                               "countNotNone(%s)", ignoreNone=False)

    @property
    def hasNone(self):
        """
        This is an **aggretation expression** which evaluates an
        Column expression to *True* if and only if the column contains a *None* value.
        """
        return self.countNone > 0
        return AggregateExpression(self, lambda v: int(None in v) , "hasNone(%s)",\
                                   ignoreNone=False)

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
            diff = set(id(v) for v in values if v is not None)
            if len(diff) == 0:
                raise Exception("only None values in %s" % self)
            if len(diff) > 1:
                raise Exception("more than one None value in %s" % self)
            return [v for v in values if v is not None][0]
        return AggregateExpression(self, select, "uniqueNotNone(%s)",\
                                   ignoreNone=False)

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
        lhs, ixl = saveeval(self.left, ctx)
        rhs, ixr = saveeval(self.right, ctx)
        if not self.allowNone:
            if lhs == None or rhs==None:
                raise Exception("comparing to None with '%s' is not allowed"\
                                % self.symbol)
            # comparint to None in np.array does not work ! so
            if type(lhs) == list and None in lhs\
                or type(lhs)==np.ndarray and None in set(lhs):
                    raise Exception("comparing to None with '%s' is not allowed"\
                                    % self.symbol)
            if type(rhs) in [list, np.ndarray] and None in set(rhs):
                raise Exception("comparing to None with '%s' is not allowed"\
                                % self.symbol)

        if ixl != None and type(rhs) in _basic_num_types:
            return self.fastcomp(lhs, rhs, ixl), None
        if ixr != None and type(lhs) in _basic_num_types:
            return self.rfastcomp(lhs, rhs, ixr), None

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

        raise Exception("Can not handle %r or %r, resp %r or %r"\
                        % (lhs, rhs, t0, r0))

def Range(start, end, len):
    rv = np.zeros((len,), dtype=np.bool)
    rv[start:end] = True
    return rv

class LtExpression(CompExpression):

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

class GtExpression(CompExpression):

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

class LeExpression(CompExpression):

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

class GeExpression(CompExpression):

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

class NeExpression(CompExpression):

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

class EqExpression(CompExpression):

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


class BinaryExpression(BaseExpression):

    # TODO: refactor dependcies based on symbol, -> extra flags in
    # constructor.

    def __init__(self, left, right, efun, symbol):
        super(BinaryExpression, self).__init__(left, right)
        self.efun = efun
        self.symbol = symbol

    def _eval(self, ctx):
        lval, idxl = saveeval(self.left, ctx)
        rval, idxr = saveeval(self.right, ctx)

        if isNumericList(lval):
            lval = np.array(lval)
        if isNumericList(rval):
            rval = np.array(rval)

        # NOW lists with numeric contents are numpy arrays. all list
        # below contain  strings or other nonnum objects.
        # The array might contain None values.
        # For +-*/ we want to have that the result is None if at least
        # one of the operands is None.
        # to acchieve this wie first determine the Nones of the operands
        # set them to 1.0, perform the operation and insert Nones back
        # to their former places.

        if type(lval) in _basic_num_types and type(rval) == np.ndarray:
            # '== None' does not work, but None <= x for all values
            if self.symbol in "+-*/":
                indicesNone = rval <= None
                rval[indicesNone] = 1.0  # 1.0 works for all operations
            res = self.efun(lval, rval)
            # np.any is needed, as res[indicesNone] = None raises
            # exception even if there was no None in rval, that is
            # any(indicesNone) is false
            if self.symbol in "+-*/" and np.any(indicesNone):
                try:
                    res[indicesNone] = None
                except:
                    # trick: tolist converts all diff np types to
                    # corresponding python type:
                    raise Exception("None for columnType %s not allowed"\
                                    % type(res[0].tolist()))

            # order preserving operations keep index idxr
            # c + vec, c * vec and c>0, c/vec and c<0 kepp order of vec
            # c - vec destroys it:
            if self.symbol == "+" or (self.symbol=="*" and lval > 0)\
                                  or (self.symbol=="/" and lval < 0):
                return res, idxr
            # else: loose index
            return res, None

        if  type(lval) == np.ndarray and type(rval) in _basic_num_types:
            # numpy does not like [None, 1] + 1, which should be [None,
            # 2] in my opinion. so :
            # == None does not work, but None <= x for all values
            if self.symbol in "+-*/":
                indicesNone = lval <= None
                lval[indicesNone] = 1.0  # 1.0 works for all operations
            res = self.efun(lval, rval)
            # np.any is needed, as res[indicesNone] = None raises
            # exception even if there was no None in rval, that is
            # any(indicesNone) is false
            if self.symbol in "+-*/" and np.any(indicesNone):
                try:
                    res[indicesNone] = None
                except:
                    # trick: tolist converts all diff np types to
                    # corresponding python type:
                    raise Exception("None for columnType %s not allowed"\
                                    % type(res[0].tolist()))
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

            if self.symbol in "+-*/":
                # None handling trickery. SEE COMMETNS ABOVE !!!
                indicesNone = (lval <= None) | (rval <= None)
                lval[indicesNone] = 1.0
                rval[indicesNone] = 1.0

            res = self.efun(lval, rval)
            if self.symbol in "+-*/" and np.any(indicesNone):
                try:
                    res[indicesNone] = None
                except:
                    # trick: tolist converts all diff np types to
                    # corresponding python type:
                    raise Exception("None for columnType %s not allowed"\
                                    % type(res[0].tolist()))
            return res, None

        if type(lval) == list and type(rval) == list:
            if len(lval) != len(rval):
                raise Exception("sizes do not fit !")
            return [ self.efun(l,r) for (l,r) in zip(lval,rval) ], None

        # at least one is np.ndarray:
        if type(lval) in _iterables and type(rval) in _iterables:
            if len(lval) != len(rval):
                raise Exception("sizes do not fit !")
            return np.array([self.efun(l,r) for (l,r) in zip(lval,rval)]), None

        assert type(lval) in _basic_types and type(rval) in _basic_types
        if (lval is None or rval is None) and self.symbol in "+-*/":
            return None, None

        return self.efun(lval, rval), None


class UnaryExpression(BaseExpression):

    def __init__(self, left, efun, funname):
        if not isinstance(left, BaseExpression):
            left = Value(left)
        self.left = left
        self.efun = efun
        self.funname = funname

    def _eval(self, ctx):
        vals, _ = saveeval(self.left, ctx)
        if type(vals) in _iterables:
            return np.array([self.efun(v) for v in vals]), None
        return self.efun(vals), None

    def __str__(self):
        return self.funname % self.left

class AggregateExpression(BaseExpression):

    def __init__(self, left, efun, funname, ignoreNone=True):
        if not isinstance(left, BaseExpression):
            left = Value(left)
        self.left = left
        self.efun = efun
        self.funname = funname
        self.ignoreNone = ignoreNone

    def _eval(self, ctx):
        vals, _ = saveeval(self.left, ctx)
        if not type(vals) in _iterables:
            vals = [vals]
        if self.ignoreNone:
            vals  = [ v for v in vals if v is not None]
        if len(vals):
            return self.efun(vals), None
        return None, None

    def __str__(self):
        return self.funname % self.left


class LogicExpression(BaseExpression):

    def __init__(self, left, right):
        super(LogicExpression, self).__init__(left, right)
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
            return np.array([bitop(li, r) for li in l])
        elif type(l) == type(r) == np.ndarray:
            return bitop(l,r)
        elif type(l) in _iterables and type(r) in _iterables:
            return np.array([bitop(li, ri) for li,ri in zip(l,r)])
        raise Exception("bool op for %r and %r not defined" % (l, r))


class AndExpression(LogicExpression):

    symbol = "&"
    def _eval(self, ctx):
        lhs, _ = saveeval(self.left, ctx)
        if type(lhs) == bool and not lhs:
            return np.zeros((self.right._evalsize(ctx),), dtype=np.bool), None
        rhs, _ = saveeval(self.right, ctx)
        return self.richeval(lhs, rhs, lambda a,b: a & b), None

class OrExpression(LogicExpression):

    symbol = "|"
    def _eval(self, ctx):
        lhs, _ = saveeval(self.left, ctx)
        if type(lhs)==bool and lhs:
            return np.ones((self.right._evalsize(ctx),), dtype=np.bool), None
        rhs, _ = saveeval(self.right, ctx)
        return self.richeval(lhs, rhs, lambda a,b: a | b), None

class XorExpression(LogicExpression):

    symbol = "^"
    def _eval(self, ctx):
        lhs, _ = saveeval(self.left, ctx)
        rhs, _ = saveeval(self.right, ctx)
        return self.richeval(lhs, rhs, lambda a,b: (a & ~b) | (~a & b)), None


class Value(BaseExpression):

    def __init__(self, value):
        self.value = value
    def _eval(self, ctx):
        return self.value, None

    def __str__(self):
        return repr(self.value)

    def _evalsize(self, ctx):
        return 1

    def _neededColumns(self):
        return []



class FunctionExpression(BaseExpression):

    def __init__(self, efun, efunname, child, agg):
        if not isinstance(child, BaseExpression):
            child = Value(child)
        self.child = child
        self.efun = efun
        self.efunname = efunname
        self.agg = agg

    def _eval(self, ctx):
        val, index = saveeval(self.child, ctx)
        if type(val) in _basic_types:
            if val is None:
                return val, None
            return self.efun(val), None

        if str(self.efun).startswith("<ufunc"):
            if None not in val:
                return self.efun(val), None 
        res = [ self.efun(v) if v is not None else None for v in val]
        return res, None


    def __str__(self):
        return "%s(%s)" % (self.efunname, self.child)

    def _evalsize(self, ctx):
        if self.agg:
            return 1
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
            e1, _ = saveeval(self.e1, ctx)
            e2, _ = saveeval(self.e2, ctx)
            e3, _ = saveeval(self.e3, ctx)

            size = self._evalsize(ctx)
            if size == 1:
                return e2 if e1 else e3, None
            if not type(e1) in _iterables:
                e1 = [ e1 ] * size
            elif isinstance(e1, np.ndarray):
                # incl. conversion of array entries to python types here
                e1 = e1.tolist()

            if not type(e2) in _iterables:
                e2 = [ e2 ] * size
            elif isinstance(e2, np.ndarray):
                # incl. conversion of array entries to python types here
                e2 = e2.tolist()

            if not type(e3) in _iterables:
                e3 = [ e3 ] * size
            elif isinstance(e3, np.ndarray):
                # incl. conversion of array entries to python types here
                e3 = e3.tolist()

            # no numpy array here, this would not be much
            # faster and we would have to do lots of decisions
            # and extra handling here
            return [ e2i if e1i else e3i for (e1i, e2i, e3i)
                     in zip(e1, e2, e3) ], None


        def __str__(self):
            return "%s(%s)" % (self.efunname, self.child)

        def _evalsize(self, ctx):
            return max((self.e1._evalsize(ctx),
                        self.e2._evalsize(ctx),
                        self.e3._evalsize(ctx)))

        def _neededColumns(self):
            return self.e1._neededColumns() \
                   + self.e2._neededColumns() \
                   + self.e3._neededColumns()



def _wrapFun(name, agg=False):
    def wrapper(x):
        origfun = getattr(np, name)
        if isinstance(x,BaseExpression):
            return FunctionExpression(origfun, name,  x, agg)
        return origfun(x)
    wrapper.__doc__ = \
    """
    Applies %s to an expression. Example:: ``%s(tab.value)``
    """ %(name, name)
    return wrapper

log = _wrapFun("log")
exp = _wrapFun("exp")
sin = _wrapFun("sin")
cos = _wrapFun("cos")
sqrt = _wrapFun("sqrt")

max = _wrapFun("max", agg=True)
min = _wrapFun("min", agg=True)
mean = _wrapFun("mean", agg=True)
std = _wrapFun("std", agg=True)
sum = _wrapFun("sum", agg=True)
count = _wrapFun("len", agg=True)



class ColumnExpression(BaseExpression):

    """
    A ``ColumnExpression`` is the simplest form of an ``Expression``.
    It is generated from a ``Table`` ``t`` as ``t.x`` or by calling
    ``t.getColumn("x")``.

    """

    def __init__(self, table, colname, idx):
        self.table = table
        self.colname = colname
        self.idx = idx

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
        if ctx is None:
            return self.values, None
        cx = ctx.get(self.table)
        if cx is None:
            raise Exception("context not correct. "\
                            "did you use wrong table in expression ?")
        return cx[self.colname]


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
        if type(rv) in _basic_types:
            return 1
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

