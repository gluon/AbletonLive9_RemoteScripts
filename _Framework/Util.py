#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/Util.py
"""
Various utilities.
"""
from contextlib import contextmanager
from functools import wraps
from itertools import chain

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))


def linear(minv, maxv, val):
    return minv + (maxv - minv) * val


def nop(*a, **k):
    if a:
        return a[0]


def negate(value):
    return not value


def const(value):
    return lambda *a, **k: value


def in_range(value, lower_bound, upper_open_bound):
    return value >= lower_bound and value < upper_open_bound


def sign(value):
    return 1.0 if value >= 0.0 else -1.0


class memoize(object):
    """
    Decorator to use automatic memoization on a given function, such
    that results are chached and, if called a second time, the
    function will return the cached value. Example::
    
        @memoize
        def fibonacci(n):
            print "Computing fibonacci of:", n
            if n == 0:
                return 0
            if n == 1:
                return 1
            return fibonacci(n-1) + fibonacci(n-2)
    
        fibonacci(5)
    
    If we removed the @memoize decorator, it would print O(2^n) lines
    instead showing a exponential degeneration due to the binary
    recursion.  However, already computed values will not recurse,
    thus this program will print on the console:
    
        Computing fibonacci of: 5
        Computing fibonacci of: 4
        Computing fibonacci of: 3
        Computing fibonacci of: 2
        Computing fibonacci of: 1
    
    Note that every computed value is cached in global state, so this
    can be inapropiate when the function domain is very big.
    """

    def __init__(self, function):
        self.function = function
        self.memoized = {}

    def __call__(self, *args):
        try:
            ret = self.memoized[args]
        except KeyError:
            ret = self.memoized[args] = self.function(*args)

        return ret


@memoize
def mixin(one, two, *args):
    """
    Dynamically creates a class that inherits from all the classes
    passed as parameters. Example::
    
        class A(object):
            pass
        class B(object):
            pass
    
        a_and_b_instance = mixin(A, B)()
    
    Also, this statement holds for every A and B::
    
        assert mixin(A, B) == mixin(A, B)
    """

    class Mixin(one, two):

        def __init__(self, *args, **kws):
            super(Mixin, self).__init__(*args, **kws)

    if args:
        return mixin(Mixin, *args)
    return Mixin


def monkeypatch(target, name = None, override = False, doc = None):
    """
    Decorator that injects the decorated function into the 'target'
    class. If no name is given the decorated function name will be
    used for the injected method name. If the class already has a
    method with a given name it raises an error unless 'override' is
    set to True.
    
    Example::
        class MyClass(object):
            pass
    
        @monkeypatch(MyClass)
        def patched_method(self):
            print "Lalala"
    
        MyClass().patched_method()
    
    Output::
        Lalala
    """

    def patcher(func):
        patchname = func.__name__ if name is None else name
        if not override and hasattr(target, patchname):
            raise TypeError('Class %s already has method %s' % (target.__name__, patchname))
        setattr(target, patchname, func)
        func.__name__ = patchname
        if doc is not None:
            func.__doc__ = doc
        return func

    return patcher


def monkeypatch_extend(target, name = None):
    """
    Decorator that injects the decorated function as an extension of a
    method of the 'target' class. If no 'name' is passed, the
    decorated function name will be the name of the method.
    
    Example::
       class MyClass(object):
           def some_method(self):
               print "Original"
    
        @monkeypatch_extend(MyClass)
        def some_method(self):
            print "Patch"
    
        MyClass().some_method()
    
    Output::
        Original
        Patch
    
    Known issues: if you are extending a method of class Deriv,
    when the method is only defined in its super-class Base (i.e. not
    overriden by Deriv but is inherited from Base), can break the
    ability of the method to properly cooperate (i.e. propagate calls
    to super in a diamond-shaped hierarchy [1]).  If
    monkeypatch_extend in a metaclass, this can be worked around by
    injecting a cooperative definition of the method in Deriv's
    dictionary. An example of this can be seen in SubjectSlot.SubjectMeta
    
    [1] A definition of cooperative method http://sinusoid.es/jpblib/coop.html
    """

    def patcher(func):
        newfunc = func
        patchname = func.__name__ if name is None else name
        if hasattr(target, patchname):
            oldfunc = getattr(target, patchname)
            if not callable(oldfunc):
                raise TypeError('Can not extend non callable attribute')

            @wraps(oldfunc)
            def extended(*a, **k):
                ret = oldfunc(*a, **k)
                func(*a, **k)
                return ret

            newfunc = extended
        else:
            raise False or AssertionError, 'Must have something to extend'
        setattr(target, patchname, newfunc)
        return func

    return patcher


def instance_decorator(decorator):
    """
    Meta-decorator to define decorators that decorate a method in a
    concrete instance. The decorator method will be passed the
    object instance as first argument and the unbound decorated method
    as second argument. The decorator method will be called lazily the
    first time the method is accessed.
    
    For an example see @signal_slot in SubjectSlot module.
    """

    class Decorator(object):

        def __init__(self, func = nop, *args, **kws):
            self.__name__ = func.__name__
            self.__doc__ = func.__doc__
            self._func = func
            self._args = args
            self._kws = kws

        def __get__(self, obj, cls = None):
            if obj is None:
                return
            decorated = decorator(obj, self._func, *self._args, **self._kws)
            obj.__dict__[self.__name__] = decorated
            return decorated

    return Decorator


def forward_property(member):
    """
    Property that forwards access to a nested object. You can use it
    as a decorator, where the function will be used only to extract
    the name of the property. It is useful when exposing some property
    of a subobject...
    
    Example::
        class NestedClass(object):
            parameter = 0
    
        class SomeClass(object):
            def __init__(self, *a, **k):
                super(SomeClass, self).__init__(*a, **k)
                self._nested_object = NestedClass()
    
            @forward_property('_nested_object')
            def parameter(): pass
    
        print SomeClass().parameter
    
    Output::
        0
    """

    class Descriptor(object):

        def __init__(self, func_or_name):
            self._property_name = func_or_name.__name__ if callable(func_or_name) else func_or_name

        def __get__(self, obj, cls = None):
            return getattr(getattr(obj, member), self._property_name)

        def __set__(self, obj, value):
            return setattr(getattr(obj, member), self._property_name, value)

    return Descriptor


class lazy_attribute(object):
    """
    Decorator that will turn a method in a lazy attribute. The first
    time the attribute is accessed its value will be computed using
    the decorated method and then cached.
    
    Example::
        class MyClass(object):
    
            @lazy_attribute
            def my_attribute(self):
                print "Computing"
                return 0
    
        obj = MyClass()
        print obj.my_attribute
        print obj.my_attribute
    
    Output::
        Computing
        0
        0
    """

    def __init__(self, func, name = None):
        self._func = func
        self.__name__ = func.__name__ if name is None else name
        self.__doc__ = func.__doc__

    def __get__(self, obj, cls = None):
        if obj is None:
            return self
        result = obj.__dict__[self.__name__] = self._func(obj)
        return result


def remove_if(predicate, lst):
    """
    Returns a new list with elements of the iterable 'lst' excepting
    those satisfying 'predicate'.
    """
    return [ elem for elem in lst if not predicate(elem) ]


def flatten(list):
    """
    Flattens a list of lists into a new list. It does not do that
    recursively, only one level.
    """
    return chain(*list)


def group(lst, n):
    """
    Returns a list of lists with elements from 'lst' grouped in blocks
    of 'n' elements.
    """
    return map(None, *[ lst[i::n] for i in range(n) ])


def find_if(predicate, seq):
    """
    Returns the first element in sequence 'seq' satisfying 'predicate'
    or 'None' if no such element exists.
    """
    for x in seq:
        if predicate(x):
            return x


def index_if(predicate, seq):
    """
    Returns the index of the first element in sequence 'seq'
    satisfying predicate. If no such element exists returns the length
    of the sequence.
    """
    idx = 0
    for x in seq:
        if predicate(x):
            return idx
        idx += 1

    return idx


def union(a, b):
    """
    Returns a new dictionary with all the entries in dictionaries 'a'
    and 'b'. In case of conflict the entry from 'b' is taken.
    """
    a = dict(a)
    a.update(b)
    return a


def product(iter_a, iter_b):
    """
    Generator that generates all possible tuples combining elements
    from sequence 'iter_a' and 'iter_b'.
    """
    for a in iter_a:
        for b in iter_b:
            yield (a, b)


def next(iter):
    """
    Equivalent to iter.next()
    """
    return iter.next()


def is_iterable(value):
    """
    Returns True if 'value' is iterable and False otherwise.
    """
    try:
        it = iter(value)
        return bool(it)
    except TypeError:
        return False


def recursive_map(fn, element, sequence_type = None):
    """
    Maps a tree-like data structure built by composing sequences of
    type iterable_type. if no iterable_type is given, it is assumed to
    be the type of the root element.
    
    Example::
        print recurse_map(lambda t: t + (0,),
                          [[(0,), (1,)], [(3,), (4,)]])
    
    Output::
        [[(0,0), (1,0)], [(3,0), (4,0)]]
    """
    if sequence_type is None:
        return recursive_map(fn, element, type(element))
    elif isinstance(element, sequence_type):
        return map(lambda x: recursive_map(fn, x, sequence_type), element)
    else:
        return fn(element)


def first(seq):
    return seq[0]


def second(seq):
    return seq[1]


def third(seq):
    return seq[2]


def compose(*funcs):
    """
    Returns the composition of all passed functions, similar to the
    mathematical dot.
    
    Example::
        f = lambda x: x + 2
        g = lambda x: x * 2
        h = compose(f, g)
        print h(3)
    
    Output::
       8 # (3 * 2) + 2
    """
    return lambda x: reduce(lambda x, f: f(x), funcs[::-1], x)


def _partial(fn, *a, **k):
    """
    See functools.partial
    """
    return lambda *aa, **kk: fn(*(a + aa), **union(k, kk))


def is_contextmanager(value):
    return callable(getattr(value, '__enter__')) and callable(getattr(value, '__exit__'))


def infinite_context_manager(generator):
    """
    contextlib.contextmanager have the consumes the generator, so most
    of the time they can only be used one.  This variant will always
    re-instantiate the generator, such that the context manager can be
    reused.
    """
    make_context_manager = contextmanager(generator)

    class InfiniteContextManager(object):

        def __enter__(self):
            self._delegate = make_context_manager()
            self._delegate.__enter__()

        def __exit__(self, type, err, trace):
            self._delegate.__exit__(type, err, trace)
            del self._delegate

    return InfiniteContextManager


class BooleanContext(object):
    """
    This class represents an boolean variable with RAII setting within
    a scope.  It is useful to break recursions in an exception-safe
    way.  The boolean context can be used in nested fashion, as long
    as you request a new context manager for every 'with' statement
    using the call operator. Example::
    
      in_notification = BooleanContext()
    
      assert not in_notification
      with in_notification():
          assert in_notification
          with in_notification():
              assert in_notification
          assert in_notification
      assert not in_notification
    
    The 'default_value' parameter indicates the initial value. It will
    be negated when you enter the context.
    """
    default_value = False

    def __init__(self, default_value = None, *a, **k):
        super(BooleanContext, self).__init__(*a, **k)
        if default_value is not None:
            self.default_value = default_value
        self._current_value = self.default_value

    def __nonzero__(self):
        return bool(self._current_value)

    def __bool__(self):
        return bool(self._current_value)

    def __call__(self):
        """
        Makes a context manager for the boolean context
        """
        return self.Manager(self)

    @property
    def value(self):
        return self._current_value

    class Manager(object):

        def __init__(self, managed = None, *a, **k):
            super(BooleanContext.Manager, self).__init__(*a, **k)
            self._managed = managed

        def __enter__(self):
            managed = self._managed
            self._old_value = managed._current_value
            managed._current_value = not managed.default_value
            return self

        def __exit__(self, *a, **k):
            self._managed._current_value = self._old_value


class NamedTupleMeta(type):

    def __new__(cls, name, bases, dct):
        defaults = filter(lambda (k, _): k[:2] != '__', dct.iteritems())
        for k, _ in defaults:
            del dct[k]

        cls = super(NamedTupleMeta, cls).__new__(cls, name, bases, dct)
        cls._NamedTuple__defaults = union(getattr(cls, '_NamedTuple__defaults', {}), dict(defaults))
        return cls


class NamedTuple(object):
    """
    Immutable object that acts like a dictionary whose members can
    also be set via attribute access.  Derivatives can give and
    override default values in the class definition, for example::
    
      class MyNamedTuple(NamedTuple):
          some_value = 3
    
      assert MyNamedTuple == NamedTuple(some_value = 3)
    """
    __metaclass__ = NamedTupleMeta
    __defaults = {}

    def __init__(self, *a, **k):
        super(NamedTuple, self).__init__(*a)
        self.__dict__['_NamedTuple__contents'] = union(self.__defaults, k)

    def __getattr__(self, name):
        return self.__contents[name]

    def __setattr__(self, name, value):
        raise AttributeError, 'Named tuple is constant'

    def __delattr__(self, name):
        raise AttributeError, 'Named tuple is constant'

    def __getitem__(self, name):
        return self.__contents[name]

    def __eq__(self, other):
        return isinstance(other, NamedTuple) and self.__contents == other.__contents

    def __getstate__(self):
        return self.__contents

    def __setstate__(self, state):
        self.__dict__['_NamedTuple__contents'] = state


def trace_value(value, msg = 'Value: '):
    """
    Prints value and returns value. Useful when debugging the results
    of sub-expressions.
    """
    print msg, value
    return value


def count_calls(fn = nop):
    return wraps(fn)(CallCounter(fn))


class Bindable(object):
    """
    Utility base class for general bindable function objects.
    Specializations should define the bind()
    """
    _bound_instances = None

    def __get__(self, obj, cls = None):
        import weakref
        if self._bound_instances is None:
            self._bound_instances = weakref.WeakKeyDictionary()
        bound_dict = self._bound_instances.setdefault(obj, weakref.WeakKeyDictionary())
        try:
            bound = bound_dict[self]
        except KeyError:
            bound = self.bind(weakref.proxy(obj))
            bound_dict[self] = bound

        return bound

    def bind(self, bind_to_object):
        raise NotImplementedError


class CallCounter(Bindable):
    """
    Function object that counts the number of times it is called.
    """

    def __init__(self, fn = nop, current_self = None, *a, **k):
        super(CallCounter, self).__init__(*a, **k)
        self.fn = fn
        self.count = 0
        self.current_self = current_self

    def bind(self, obj):
        return CallCounter(fn=self.fn, current_self=obj)

    def __call__(self, *a, **k):
        self.count += 1
        if self.current_self is not None:
            return self.fn(self.current_self, *a, **k)
        else:
            return self.fn(*a, **k)