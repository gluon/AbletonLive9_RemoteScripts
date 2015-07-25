#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/_Tools/types.py
"""Define names for all type symbols known in the standard interpreter.

Types that are part of optional modules (e.g. array) are not listed.
"""
import sys
NoneType = type(None)
TypeType = type
ObjectType = object
IntType = int
LongType = long
FloatType = float
BooleanType = bool
try:
    ComplexType = complex
except NameError:
    pass

StringType = str
try:
    UnicodeType = unicode
    StringTypes = (StringType, UnicodeType)
except NameError:
    StringTypes = (StringType,)

BufferType = buffer
TupleType = tuple
ListType = list
DictType = DictionaryType = dict

def _f():
    pass


FunctionType = type(_f)
LambdaType = type(lambda : None)
try:
    CodeType = type(_f.func_code)
except RuntimeError:
    pass

def _g():
    yield 1


GeneratorType = type(_g())

class _C:

    def _m(self):
        pass


ClassType = type(_C)
UnboundMethodType = type(_C._m)
_x = _C()
InstanceType = type(_x)
MethodType = type(_x._m)
BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)
ModuleType = type(sys)
FileType = file
XRangeType = xrange
try:
    raise TypeError
except TypeError:
    try:
        tb = sys.exc_info()[2]
        TracebackType = type(tb)
        FrameType = type(tb.tb_frame)
    except AttributeError:
        pass

    tb = None
    del tb

SliceType = slice
EllipsisType = type(Ellipsis)
DictProxyType = type(TypeType.__dict__)
NotImplementedType = type(NotImplemented)
try:
    import _types
except ImportError:
    pass
else:
    GetSetDescriptorType = type(_types.Helper.getter)
    MemberDescriptorType = type(_types.Helper.member)
    del _types

del sys
del _f
del _g
del _C
del _x