#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/decoration.py
from __future__ import absolute_import, print_function
from itertools import ifilter
from ableton.v2.base import CompoundDisconnectable, Proxy

class LiveObjectDict(dict):

    def __init__(self, *a, **k):
        self.update(*a, **k)

    def __getitem__(self, key):
        return super(LiveObjectDict, self).__getitem__(self._transform_key(key))

    def __setitem__(self, key, value):
        return super(LiveObjectDict, self).__setitem__(self._transform_key(key), value)

    def __delitem__(self, key):
        return super(LiveObjectDict, self).__delitem__(self._transform_key(key))

    def __contains__(self, key):
        return super(LiveObjectDict, self).__contains__(self._transform_key(key))

    def get(self, key, *default):
        return super(LiveObjectDict, self).get(self._transform_key(key), *default)

    def _transform_key(self, key):
        raise hasattr(key, '_live_ptr') or AssertionError
        return key._live_ptr

    def update(self, *a, **k):
        trans = self._transform_key
        super(LiveObjectDict, self).update(*[ (trans(key), v) for key, v in a ], **dict(((trans(key), k[key]) for key in k)))

    def prune(self, keys):
        transformed_keys = map(self._transform_key, keys)
        deleted_objects = []
        for key in ifilter(lambda x: x not in transformed_keys, self.keys()):
            deleted_objects.append(super(LiveObjectDict, self).__getitem__(key))
            super(LiveObjectDict, self).__delitem__(key)

        return deleted_objects


class LiveObjectDecorator(CompoundDisconnectable, Proxy):

    def __init__(self, live_object = None, additional_properties = {}):
        raise live_object is not None or AssertionError
        super(LiveObjectDecorator, self).__init__(proxied_object=live_object)
        self._live_object = live_object
        for name, value in additional_properties.iteritems():
            setattr(self, name, value)

    def __eq__(self, other):
        return id(self) == id(other) or self._live_object == other

    def __ne__(self, other):
        return not self == other

    def __nonzero__(self):
        return self._live_object != None

    def __hash__(self):
        return hash(self._live_object)


class DecoratorFactory(CompoundDisconnectable):
    _decorator = LiveObjectDecorator

    def __init__(self, *a, **k):
        super(DecoratorFactory, self).__init__(*a, **k)
        self.decorated_objects = LiveObjectDict()

    def decorate(self, live_object, additional_properties = {}, **k):
        if self._should_be_decorated(live_object):
            if not self.decorated_objects.get(live_object, None):
                self.decorated_objects[live_object] = self.register_disconnectable(self._get_decorated_object(live_object, additional_properties, **k))
            live_object = self.decorated_objects[live_object]
        return live_object

    def _get_decorated_object(self, live_object, additional_properties, **k):
        return self._decorator(live_object=live_object, additional_properties=additional_properties, **k)

    def sync_decorated_objects(self, keys):
        deleted_objects = self.decorated_objects.prune(keys)
        for decorated in deleted_objects:
            self.unregister_disconnectable(decorated)
            decorated.disconnect()

    @classmethod
    def _should_be_decorated(cls, device):
        return True