# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/clip_decoration.py
# Compiled at: 2016-05-20 03:43:52
from __future__ import absolute_import, print_function
from ableton.v2.base import liveobj_valid, listenable_property, listens, EventObject
from pushbase.decoration import DecoratorFactory, LiveObjectDecorator
from pushbase.internal_parameter import InternalParameter
from .decoration import find_decorated_object
from .waveform_navigation import AudioClipWaveformNavigation

class ClipPositions(EventObject):
    __events__ = ('is_recording', 'warp_markers', 'before_update_all', 'after_update_all')
    start = listenable_property.managed(0.0)
    end = listenable_property.managed(0.0)
    start_marker = listenable_property.managed(0.0)
    end_marker = listenable_property.managed(0.0)
    loop_start = listenable_property.managed(0.0)
    loop_end = listenable_property.managed(0.0)
    loop_length = listenable_property.managed(0.0)
    use_beat_time = listenable_property.managed(False)

    def __init__(self, clip=None, *a, **k):
        assert clip is not None
        assert clip.is_audio_clip
        super(ClipPositions, self).__init__(*a, **k)
        self._clip = clip
        self._looping = self._clip.looping
        self.__on_is_recording_changed.subject = clip
        self.__on_warping_changed.subject = clip
        self.__on_warp_markers_changed.subject = clip
        self.__on_looping_changed.subject = clip
        self.__on_start_marker_changed.subject = clip
        self.__on_end_marker_changed.subject = clip
        self.__on_loop_start_changed.subject = clip
        self.__on_loop_end_changed.subject = clip
        self.update_all()
        return

    def _convert_to_desired_unit(self, beat_time_or_seconds):
        """
        This converts the given beat time or seconds unit to the desired unit.
        - If the input unit is beat time, we are warped and don't need to do
          anything.
        - If the input time is seconds, we want to have sample time and need to
          convert.
        """
        if not self._clip.warping:
            beat_time_or_seconds = self._clip.seconds_to_sample_time(beat_time_or_seconds)
        return beat_time_or_seconds

    @listens('start_marker')
    def __on_start_marker_changed(self):
        if not self._process_looping_update():
            self.start_marker = self._convert_to_desired_unit(self._clip.start_marker)

    @listens('end_marker')
    def __on_end_marker_changed(self):
        if not self._process_looping_update():
            self.end_marker = self._convert_to_desired_unit(self._clip.end_marker)

    @listens('loop_start')
    def __on_loop_start_changed(self):
        if not self._process_looping_update():
            self.loop_start = self._convert_to_desired_unit(self._clip.loop_start)
        self._update_loop_length()

    @listens('loop_end')
    def __on_loop_end_changed(self):
        if not self._process_looping_update():
            self.loop_end = self._convert_to_desired_unit(self._clip.loop_end)
        self._update_loop_length()

    @listens('is_recording')
    def __on_is_recording_changed(self):
        self._update_start_end()
        self.notify_is_recording()

    @listens('warp_markers')
    def __on_warp_markers_changed(self):
        self.update_all()
        self.notify_warp_markers()

    @listens('looping')
    def __on_looping_changed(self):
        self.update_all()

    @listens('warping')
    def __on_warping_changed(self):
        self.update_all()

    def _process_looping_update(self):
        """
        Changing the looping setting is considered a transaction and will update
        all parameters.
        This method should be called, before updating any position parameter.
        Returns True, in case a looping change has been processed.
        """
        looping = self._clip.looping
        if looping != self._looping:
            self._looping = looping
            self.update_all()
            return True
        return False

    def _update_loop_length(self):
        self.loop_length = self._convert_to_desired_unit(self._clip.loop_end) - self._convert_to_desired_unit(self._clip.loop_start)

    def _update_start_end(self):
        if self._clip.warping:
            self.start = self._clip.sample_to_beat_time(0)
            self.end = self._clip.sample_to_beat_time(self._clip.sample_length)
        else:
            self.start = 0
            self.end = self._clip.sample_length

    def update_all(self):
        self.notify_before_update_all()
        self._update_start_end()
        self.__on_start_marker_changed()
        self.__on_end_marker_changed()
        self.__on_loop_start_changed()
        self.__on_loop_end_changed()
        self.use_beat_time = self._clip.warping
        self.notify_after_update_all()


class ZoomParameter(AudioClipWaveformNavigation, InternalParameter):
    pass


class ClipDecoration(EventObject, LiveObjectDecorator):
    __events__ = ('zoom', )

    def __init__(self, *a, **k):
        super(ClipDecoration, self).__init__(*a, **k)
        self._positions = self.register_disconnectable(ClipPositions(self))
        self._zoom_parameter = ZoomParameter(name='Zoom', parent=self._live_object, clip=self)
        self._zoom_parameter.focus_object(self._zoom_parameter.start_marker_focus)
        self.register_disconnectable(self._zoom_parameter)

    @property
    def positions(self):
        return self._positions

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

    def __init__(self, source_clip=None, destination_clip=None, decorator_factory=None):
        self._source_clip = source_clip
        self._destination_clip = destination_clip
        self._decorator_factory = decorator_factory

    def post_duplication_action(self):
        decorated_clip = find_decorated_object(self._source_clip, self._decorator_factory)
        if decorated_clip:
            self._copy_zoom_parameter(decorated_clip)

    def _copy_zoom_parameter(self, copied_decorated_clip):
        if not self._destination_clip:
            return
        new_clip_decorated = self._decorator_factory.decorate(self._destination_clip)
        new_clip_decorated.zoom.copy_state(copied_decorated_clip.zoom)