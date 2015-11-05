#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/decoration.py
from __future__ import absolute_import
from itertools import ifilter
import Live
from ableton.v2.base import CompoundDisconnectable, find_if, liveobj_changed, liveobj_valid, Proxy

def find_decorated_object(proxied_object, decorator_factory):
    decorated_obj = None
    if liveobj_valid(proxied_object):
        decorated_obj = find_if(lambda obj: not liveobj_changed(obj.proxied_object, proxied_object), decorator_factory.decorated_objects.itervalues())
    return decorated_obj


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


class TrackDecoratorFactory(DecoratorFactory):

    def attach_nesting_level(self, decorated, nesting_level = 0, parent = None):
        parent_nesting = parent.nesting_level if parent else 0
        decorated.parent_track = parent
        decorated.nesting_level = nesting_level + parent_nesting
        return decorated

    def decorate_all_mixer_tracks(self, mixer_tracks):
        tracks = []
        parent = None
        for track in mixer_tracks:
            decorated_track = self._get_decorated_track(track, parent)
            tracks.append(decorated_track)
            if self._is_unfolded(track):
                parent = decorated_track

        self.sync_decorated_objects(tracks)
        return tracks

    def _get_decorated_track(self, track, parent):
        decorated = self.decorate(track)
        is_nested_mixable = getattr(track, 'is_grouped', False) or isinstance(track, Live.Chain.Chain)
        nesting_level, parent_to_use = (1, parent) if is_nested_mixable else (0, None)
        return self.attach_nesting_level(decorated, nesting_level, parent_to_use)

    def _is_unfolded(self, track):
        return getattr(track, 'is_foldable', False) and not getattr(track, 'fold_state', False) or getattr(track, 'can_show_chains', False) and getattr(track, 'is_showing_chains', False)