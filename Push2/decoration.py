#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/decoration.py
from __future__ import absolute_import, print_function
import Live
from ableton.v2.base import find_if, liveobj_changed, liveobj_valid
from pushbase.decoration import DecoratorFactory

def find_decorated_object(proxied_object, decorator_factory):
    decorated_obj = None
    if liveobj_valid(proxied_object):
        decorated_obj = find_if(lambda obj: not liveobj_changed(obj.proxied_object, proxied_object), decorator_factory.decorated_objects.itervalues())
    return decorated_obj


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