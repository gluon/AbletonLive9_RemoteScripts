# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/clip_control.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from ableton.v2.base import listens, liveobj_valid, listenable_property
from ableton.v2.control_surface import CompoundComponent
from ableton.v2.control_surface.control import EncoderControl, ToggleButtonControl
from pushbase.clip_control_component import convert_beat_length_to_bars_beats_sixteenths, convert_beat_time_to_bars_beats_sixteenths, LoopSettingsControllerComponent as LoopSettingsControllerComponentBase, AudioClipSettingsControllerComponent as AudioClipSettingsControllerComponentBase, ONE_YEAR_AT_120BPM_IN_BEATS, WARP_MODE_NAMES
from pushbase.internal_parameter import WrappingParameter
from pushbase.mapped_control import MappedControl
from .clip_decoration import ClipDecoratorFactory
from .decoration import find_decorated_object
from .real_time_channel import RealTimeDataComponent
PARAMETERS_LOOPED = ('Loop position', 'Loop length', 'Start offset')
PARAMETERS_NOT_LOOPED = ('Start', 'End')
PARAMETERS_AUDIO = ('Warp', 'Transpose', 'Detune', 'Gain')

class LoopSetting(WrappingParameter):
    min = -ONE_YEAR_AT_120BPM_IN_BEATS
    max = ONE_YEAR_AT_120BPM_IN_BEATS

    def __init__(self, use_length_conversion=False, *a, **k):
        super(LoopSetting, self).__init__(*a, **k)
        assert self.canonical_parent is not None
        self._conversion = convert_beat_length_to_bars_beats_sixteenths if use_length_conversion else convert_beat_time_to_bars_beats_sixteenths
        self._recording = False
        self.set_property_host(self._parent)
        self.__on_clip_changed.subject = self.canonical_parent
        self.__on_clip_changed()
        return

    @property
    def recording(self):
        return self._recording

    @recording.setter
    def recording(self, value):
        self._recording = value
        self.notify_value()

    @listens('clip')
    def __on_clip_changed(self):
        self.__on_signature_numerator_changed.subject = self.canonical_parent.clip
        self.__on_signature_denominator_changed.subject = self.canonical_parent.clip

    @listens('signature_numerator')
    def __on_signature_numerator_changed(self):
        self.notify_value()

    @listens('signature_denominator')
    def __on_signature_denominator_changed(self):
        self.notify_value()

    @property
    def display_value(self):
        if not liveobj_valid(self.canonical_parent.clip):
            return unicode('-')
        if self.recording:
            return unicode('...')
        return unicode(self._conversion((
         self.canonical_parent.clip.signature_numerator,
         self.canonical_parent.clip.signature_denominator), self._get_property_value()))


class LoopSettingsControllerComponent(LoopSettingsControllerComponentBase):
    __events__ = ('looping', 'loop_parameters', 'zoom')
    zoom_encoder = MappedControl()
    zoom_touch_encoder = EncoderControl()
    loop_button = ToggleButtonControl(toggled_color='Clip.Option', untoggled_color='Clip.OptionDisabled')

    def __init__(self, *a, **k):
        super(LoopSettingsControllerComponent, self).__init__(*a, **k)
        self._looping_settings = [
         LoopSetting(name=PARAMETERS_LOOPED[0], parent=self._loop_model, source_property='position'),
         LoopSetting(name=PARAMETERS_LOOPED[1], parent=self._loop_model, use_length_conversion=True, source_property='loop_length'),
         LoopSetting(name=PARAMETERS_LOOPED[2], parent=self._loop_model, source_property='start_marker')]
        self._non_looping_settings = [
         LoopSetting(name=PARAMETERS_NOT_LOOPED[0], parent=self._loop_model, source_property='loop_start'),
         LoopSetting(name=PARAMETERS_NOT_LOOPED[1], parent=self._loop_model, source_property='loop_end')]
        for setting in self._looping_settings + self._non_looping_settings:
            self.register_disconnectable(setting)

        self.__on_looping_changed.subject = self._loop_model
        self.__on_looping_changed()

    @loop_button.toggled
    def loop_button(self, toggled, button):
        self._loop_model.looping = toggled

    @property
    def looping(self):
        if self.clip:
            return self._loop_model.looping
        return False

    @property
    def loop_parameters(self):
        if not liveobj_valid(self.clip):
            return []
        parameters = self._looping_settings if self.looping else self._non_looping_settings
        if self.zoom:
            return [self.zoom] + parameters
        return parameters

    @property
    def zoom(self):
        if liveobj_valid(self.clip):
            return getattr(self.clip, 'zoom', None)
        else:
            return None

    @listenable_property
    def waveform_navigation(self):
        if liveobj_valid(self.clip):
            return getattr(self.clip, 'waveform_navigation', None)
        else:
            return None

    @listens('is_recording')
    def __on_is_recording_changed(self):
        self._update_recording_state()

    @listens('is_overdubbing')
    def __on_is_overdubbing_changed(self):
        self._update_recording_state()

    def _update_recording_state(self):
        clip = self._loop_model.clip
        if liveobj_valid(clip):
            recording = clip.is_recording and not clip.is_overdubbing
            self._looping_settings[1].recording = recording
            self._non_looping_settings[1].recording = recording

    @listens('looping')
    def __on_looping_changed(self):
        self._update_and_notify()

    def _update_loop_button(self):
        self.loop_button.enabled = liveobj_valid(self.clip)
        if liveobj_valid(self.clip):
            self.loop_button.is_toggled = self._loop_model.looping

    def _on_clip_changed(self):
        if self.waveform_navigation is not None:
            self.waveform_navigation.reset_focus_and_animation()
        self._update_and_notify()
        self.__on_is_recording_changed.subject = self._loop_model.clip
        self.__on_is_overdubbing_changed.subject = self._loop_model.clip
        self._update_recording_state()
        self._connect_encoder()
        self.notify_waveform_navigation()
        return

    def _on_clip_start_marker_touched(self):
        if self.waveform_navigation is not None:
            self.waveform_navigation.touch_object(self.waveform_navigation.start_marker_focus)
        return

    def _on_clip_position_touched(self):
        if self.waveform_navigation is not None:
            self.waveform_navigation.touch_object(self.waveform_navigation.loop_start_focus)
        return

    def _on_clip_end_touched(self):
        if self.waveform_navigation is not None:
            self.waveform_navigation.touch_object(self.waveform_navigation.loop_end_focus)
        return

    def _on_clip_start_marker_released(self):
        if self.waveform_navigation is not None:
            self.waveform_navigation.release_object(self.waveform_navigation.start_marker_focus)
        return

    def _on_clip_position_released(self):
        if self.waveform_navigation is not None:
            self.waveform_navigation.release_object(self.waveform_navigation.loop_start_focus)
        return

    def _on_clip_end_released(self):
        if self.waveform_navigation is not None:
            self.waveform_navigation.release_object(self.waveform_navigation.loop_end_focus)
        return

    @zoom_touch_encoder.touched
    def zoom_touch_encoder(self, encoder):
        if self.waveform_navigation is not None:
            self.waveform_navigation.touch_object(self.waveform_navigation.zoom_focus)
        return

    @zoom_touch_encoder.released
    def zoom_touch_encoder(self, encoder):
        if self.waveform_navigation is not None:
            self.waveform_navigation.release_object(self.waveform_navigation.zoom_focus)
        return

    def _update_and_notify(self):
        self._update_loop_button()
        self.notify_looping()
        self.notify_loop_parameters()
        self.notify_zoom()

    def _connect_encoder(self):
        self.zoom_encoder.mapped_parameter = self.zoom

    def set_zoom_encoder(self, encoder):
        self.zoom_encoder.set_control_element(encoder)
        self.zoom_touch_encoder.set_control_element(encoder)
        self._connect_encoder()


class GainSetting(WrappingParameter):

    def __init__(self, *a, **k):
        super(GainSetting, self).__init__(*a, **k)
        self.set_property_host(self._parent)

    @property
    def display_value(self):
        return unicode(self._property_host.clip.gain_display_string if self._property_host.clip else '')


class PitchSetting(WrappingParameter):

    def __init__(self, min_value, max_value, unit, *a, **k):
        super(PitchSetting, self).__init__(*a, **k)
        self._min = min_value
        self._max = max_value
        self._unit = unit
        self.set_property_host(self._parent)

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def display_value(self):
        value = int(round(float(self._get_property_value())))
        positive_indicator = '+' if value > 0 else ''
        return positive_indicator + str(value) + self._unit


class WarpSetting(WrappingParameter):

    def __init__(self, *a, **k):
        super(WarpSetting, self).__init__(*a, **k)
        self.set_property_host(self._parent)

    @property
    def max(self):
        return len(self._property_host.available_warp_modes) - 1

    @property
    def is_quantized(self):
        return True

    @property
    def value_items(self):
        return map(lambda x: unicode(WARP_MODE_NAMES[x]), self._property_host.available_warp_modes)

    def _get_property_value(self):
        return self._property_host.available_warp_modes.index(getattr(self._property_host, self._source_property))


class AudioClipSettingsControllerComponent(AudioClipSettingsControllerComponentBase, CompoundComponent):
    __events__ = ('audio_parameters', 'warping', 'gain')

    def __init__(self, *a, **k):
        super(AudioClipSettingsControllerComponent, self).__init__(*a, **k)
        self._audio_clip_parameters = [
         WarpSetting(name=PARAMETERS_AUDIO[0], parent=self._audio_clip_model, source_property='warp_mode'),
         PitchSetting(name=PARAMETERS_AUDIO[1], parent=self._audio_clip_model, source_property='pitch_coarse', min_value=-49.0, max_value=49.0, unit='st'),
         PitchSetting(name=PARAMETERS_AUDIO[2], parent=self._audio_clip_model, source_property='pitch_fine', min_value=-51.0, max_value=51.0, unit='ct'),
         GainSetting(name=PARAMETERS_AUDIO[3], parent=self._audio_clip_model, source_property='gain')]
        self._playhead_real_time_data = self.register_component(RealTimeDataComponent(channel_type='playhead'))
        self._waveform_real_time_data = self.register_component(RealTimeDataComponent(channel_type='waveform'))
        for parameter in self._audio_clip_parameters:
            self.register_disconnectable(parameter)

        self.__on_warping_changed.subject = self._audio_clip_model
        self.__on_gain_changed.subject = self._audio_clip_model
        self.__on_warping_changed()
        self.__on_gain_changed()

    def disconnect(self):
        super(AudioClipSettingsControllerComponent, self).disconnect()
        self._playhead_real_time_data.set_data(None)
        self._waveform_real_time_data.set_data(None)
        return

    @property
    def audio_parameters(self):
        if liveobj_valid(self.clip):
            return self._audio_clip_parameters
        return []

    @property
    def warping(self):
        if liveobj_valid(self.clip):
            return self._audio_clip_model.warping
        return False

    @property
    def gain(self):
        if liveobj_valid(self.clip):
            return self._audio_clip_model.gain
        return 0.0

    @property
    def waveform_real_time_channel_id(self):
        return self._waveform_real_time_data.channel_id

    @property
    def playhead_real_time_channel_id(self):
        return self._playhead_real_time_data.channel_id

    def _on_clip_changed(self):
        self._playhead_real_time_data.set_data(self.clip)
        self._waveform_real_time_data.set_data(self.clip)
        self.__on_file_path_changed.subject = self.clip
        self.notify_audio_parameters()
        self.notify_warping()
        self.notify_gain()

    def _on_transpose_encoder_value(self, value):
        self._audio_clip_model.set_clip_pitch_coarse(value, False)

    def _on_detune_encoder_value(self, value):
        self._audio_clip_model.set_clip_pitch_fine(value, False)

    @listens('warping')
    def __on_warping_changed(self):
        self.notify_warping()

    @listens('gain')
    def __on_gain_changed(self):
        self.notify_gain()

    @listens('file_path')
    def __on_file_path_changed(self):
        self._waveform_real_time_data.invalidate()


class ClipControlComponent(CompoundComponent):
    __events__ = ('clip', )

    def __init__(self, loop_controller=None, audio_clip_controller=None, mode_selector=None, decorator_factory=None, *a, **k):
        assert loop_controller is not None
        assert audio_clip_controller is not None
        assert mode_selector is not None
        super(ClipControlComponent, self).__init__(*a, **k)
        self._loop_controller = self.register_component(loop_controller)
        self._audio_clip_controller = self.register_component(audio_clip_controller)
        self._mode_selector = self.register_component(mode_selector)
        self._decorator_factory = decorator_factory or ClipDecoratorFactory()
        self.__on_selected_scene_changed.subject = self.song.view
        self.__on_selected_track_changed.subject = self.song.view
        self.__on_selected_clip_changed.subject = self.song.view
        self.__on_has_clip_changed.subject = self.song.view.highlighted_clip_slot
        self._update_controller()
        return

    @listens('selected_scene')
    def __on_selected_scene_changed(self):
        self._update_controller()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        self._update_controller()

    @listens('detail_clip')
    def __on_selected_clip_changed(self):
        clip = self.song.view.detail_clip
        if not liveobj_valid(clip) or clip.is_arrangement_clip:
            self._update_controller()

    def on_enabled_changed(self):
        super(ClipControlComponent, self).on_enabled_changed()
        self._update_controller()

    def _decorate_clip(self, clip):
        return find_decorated_object(clip, self._decorator_factory) or self._decorator_factory.decorate(clip)

    @listens('has_clip')
    def __on_has_clip_changed(self):
        self._update_controller()

    def _update_controller(self):
        if self.is_enabled():
            clip = self.song.view.detail_clip
            self._update_selected_mode(clip)
            self._loop_controller.clip = self._decorate_clip(clip) if self._mode_selector.selected_mode == 'audio' else clip
            self._audio_clip_controller.clip = clip if liveobj_valid(clip) and clip.is_audio_clip else None
            self.__on_has_clip_changed.subject = self.song.view.highlighted_clip_slot
            self.notify_clip()
        return

    def _update_selected_mode(self, clip):
        if liveobj_valid(clip):
            self._mode_selector.selected_mode = 'audio' if clip.is_audio_clip else 'midi'
        else:
            self._mode_selector.selected_mode = 'no_clip'

    @property
    def clip(self):
        return self._loop_controller.clip