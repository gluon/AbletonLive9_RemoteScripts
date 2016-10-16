#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_MxDCore/__init__.py
from MxDCore import MxDCore as _MxDCore
import sys

def set_manager(manager):
    raise manager != None or AssertionError
    raise _MxDCore.instance == None or AssertionError
    _MxDCore.instance = _MxDCore()
    _MxDCore.instance.set_manager(manager)


def disconnect():
    _MxDCore.instance.disconnect()
    del _MxDCore.instance


def execute_command(device_id, object_id, command, arguments):
    raise _MxDCore.instance != None or AssertionError
    raise isinstance(arguments, (str, unicode)) or AssertionError
    if hasattr(_MxDCore.instance, command):
        try:
            _MxDCore.instance.update_device_context(device_id, object_id)
            function = getattr(_MxDCore.instance, command)
            function(device_id, object_id, arguments)
        except:
            if sys.exc_info()[0].__name__ == 'RuntimeError':
                assert_reason = str(sys.exc_info()[1])
            else:
                assert_reason = 'Invalid syntax'
            _MxDCore.instance._raise(device_id, object_id, assert_reason)

    else:
        _MxDCore.instance._raise(device_id, object_id, 'Unknown command: ' + command)