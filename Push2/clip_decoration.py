#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/clip_decoration.py
from ableton.v2.base import liveobj_valid, SlotManager, Subject
from .decoration import DecoratorFactory, find_decorated_object, LiveObjectDecorator
from .internal_parameter import InternalParameter

class ClipDecoration(Subject, SlotManager, LiveObjectDecorator):
    __events__ = ('zoom',)

    def __init__(self, *a, **k):
        super(ClipDecoration, self).__init__(*a, **k)
        self._zoom_parameter = InternalParameter(name='Zoom', parent=self._live_object)

    @property
    def zoom(self):
        return self._zoom_parameter


class ClipDecoratorFactory(DecoratorFactory):
    _decorator = ClipDecoration

    @classmethod
    def _should_be_decorated(cls, clip):
        return liveobj_valid(clip)


class ClipDecoratedPropertiesCopier(object):

    def __init__(self, target_clip = None, destination_clip = None, decorator_factory = None):
        self._target_clip = target_clip
        self._destination_clip = destination_clip
        self._decorator_factory = decorator_factory

    def post_duplication_action(self):
        decorated_clip = find_decorated_object(self._target_clip, self._decorator_factory)
        if decorated_clip:
            self._copy_zoom_parameter(decorated_clip)

    def _copy_zoom_parameter(self, copied_decorated_clip):
        if not self._destination_clip:
            return
        new_clip_decorated = self._decorator_factory.decorate(self._destination_clip)
        new_clip_decorated.zoom.linear_value = copied_decorated_clip.zoom.linear_value