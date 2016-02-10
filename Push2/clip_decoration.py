#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/clip_decoration.py
from __future__ import absolute_import, print_function
from ableton.v2.base import liveobj_valid, SlotManager, Subject
from pushbase.decoration import DecoratorFactory, LiveObjectDecorator
from pushbase.internal_parameter import InternalParameter
from .decoration import find_decorated_object
from .waveform_navigation import AudioClipWaveformNavigation

class ZoomParameter(AudioClipWaveformNavigation, InternalParameter):
    pass


class ClipDecoration(Subject, SlotManager, LiveObjectDecorator):
    __events__ = ('zoom',)

    def __init__(self, *a, **k):
        super(ClipDecoration, self).__init__(*a, **k)
        waveform_length = max(self._live_object.view.sample_length, 1)
        self._zoom_parameter = ZoomParameter(name='Zoom', parent=self._live_object, waveform_length=waveform_length, clip=self)
        self._zoom_parameter.focus_object(self._zoom_parameter.start_marker_focus)
        self.register_disconnectable(self._zoom_parameter)

    @property
    def zoom(self):
        return self._zoom_parameter

    @property
    def waveform_navigation(self):
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