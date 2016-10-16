#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/base/gcutil.py
from __future__ import absolute_import, print_function
from collections import defaultdict
import gc

def typename(obj):
    """
    Robust class-name utility-function
    """
    if hasattr(obj, '__class__'):
        return obj.__class__.__name__
    if hasattr(obj, '__name__'):
        return obj.__name__
    return '<unknown>'


def histogram(name_filter = None, objs = None):
    """
    Return a defaultdict of classname to count mappings.
    
    In the debugger, use e.g. pp dict(histogram()) to print this out.
    
    name_filter filters partially - all classes that contain name_filter
    will be counted.
    
    Also, an explicit set of objs can be given instead of using all
    known objects.
    """
    all_ = gc.get_objects() if objs is None else objs

    def _name_filter(name):
        return name_filter is None or name_filter in name

    hist = defaultdict(lambda : 0)
    for o in all_:
        n = typename(o)
        if _name_filter(n):
            hist[n] += 1

    return hist


def instances_by_name(name_filter):
    """
    Return the list of objects that exactly match the given
    name_filter.
    """
    return [ o for o in gc.get_objects() if name_filter == typename(o) ]


def refget(objs, level = 1):
    """
    Get the referrers to the sequence of objects passed in.
    
    As Python stores instance attributes within a dict, usually
    you need two generations of references to actually get to the
    holders of certain objects.
    
    You can control the number of generations to collect with
    the level-parameter.
    """
    for _ in xrange(level):
        refs = gc.get_referrers(*objs)
        try:
            refs.remove(objs)
        except ValueError:
            pass

        objs = refs

    return refs