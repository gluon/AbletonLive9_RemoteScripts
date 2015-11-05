#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/ableton/v2/base/live_api_utils.py


def liveobj_changed(obj, other):
    """
    Check whether obj and other are not equal, properly handling lost weakrefs.
    
    Use this whenever you cache a Live API object in some variable, and want to check
    whether you need to update the cached object.
    """
    return obj != other or type(obj) != type(other)


def liveobj_valid(obj):
    """
    Check whether obj represents a valid Live API obj.
    
    This will return False both if obj represents a lost weakref or is None.
    It's important that Live API objects are not checked using "is None", since this
    would treat lost weakrefs as valid.
    """
    return obj != None