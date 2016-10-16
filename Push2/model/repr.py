#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/model/repr.py
from __future__ import absolute_import, print_function
import re
from functools import partial
from ableton.v2.base import Slot, SlotError, SlotManager, Subject, find_if, listenable_property, listens, liveobj_valid
DEVICE_TYPES_WITH_PRESET_NAME = ['InstrumentGroupDevice',
 'DrumGroupDevice',
 'AudioEffectGroupDevice',
 'MidiEffectGroupDevice',
 'ProxyInstrumentDevice',
 'ProxyAudioEffectDevice',
 'MxDeviceInstrument',
 'MxDeviceAudioEffect',
 'MxDeviceMidiEffect']
display_pattern = re.compile('\\d|\xb0|/|\\%|\\.|\\:|\\-|\\+|inf')
unit_pattern = re.compile('inf\\s*[A-z]+$|\\d\\s*[A-z]+$')
string_pattern = re.compile('[A-z]+$')

def _get_parameter_by_name(device, name):
    parameters = device.parameters if liveobj_valid(device) else []
    return find_if(lambda x: x.name == name, parameters)


def _try_to_round_number(parameter_string):
    value_as_number = None
    try:
        value_as_number = int(parameter_string)
    except ValueError:
        pass

    if value_as_number is None:
        try:
            value_as_number = round(float(parameter_string), 2)
        except ValueError:
            pass

    return value_as_number


def get_parameter_display_value(parameter):
    parameter_string = unicode(parameter)
    found_string = ''.join(display_pattern.findall(parameter_string))
    if found_string in ('inf', '-inf'):
        parameter_display = found_string
    else:
        value = _try_to_round_number(found_string)
        parameter_display = unicode(value) if value is not None else parameter_string
        if found_string.startswith('+'):
            parameter_display = '+' + parameter_display
    return parameter_display


def get_parameter_unit(parameter):
    parameter_string = unicode(parameter)
    value = unit_pattern.findall(parameter_string)
    if value:
        return ''.join(string_pattern.findall(value[0]))
    return ''


def strip_formatted_string(str):
    """
    Remove multiple whitespaces (including new lines) and whitespaces at the beginning
    and end of the given string.
    """
    return re.sub('\\s\\s+', ' ', str).strip()


class ModelAdapter(Subject, SlotManager):

    def __init__(self, adaptee = None, *a, **k):
        raise liveobj_valid(adaptee) or AssertionError
        super(ModelAdapter, self).__init__(*a, **k)
        self._adaptee = adaptee

    def is_valid(self):
        return liveobj_valid(self._adaptee)

    def __getattr__(self, name):
        if name in self.__dict__:
            return object.__getattribute__(self, name)
        return getattr(self._adaptee, name)

    @property
    def _live_ptr(self):
        if hasattr(self._adaptee, '_live_ptr'):
            return self._adaptee._live_ptr
        return id(self._adaptee)

    def _alias_observable_property(self, prop_name, alias_name, getter = None):
        default_getter = lambda self_: getattr(self_._adaptee, prop_name)
        aliased_prop = property(getter or default_getter)
        setattr(self.__class__, alias_name, aliased_prop)
        notifier = getattr(self, 'notify_' + alias_name)
        self.register_slot(Slot(self._adaptee, notifier, prop_name))


class ClipAdapter(ModelAdapter):

    def __init__(self, *a, **k):
        super(ClipAdapter, self).__init__(*a, **k)
        self.register_slot(self._adaptee, self.notify_name, 'name')

    @listenable_property
    def name(self):
        name = self._adaptee.name
        if len(name.strip()) == 0:
            name = 'MIDI clip' if self._adaptee.is_midi_clip else 'Audio clip'
        return name


class DeviceParameterAdapter(ModelAdapter):
    __events__ = ('hasAutomation',)

    def __init__(self, *a, **k):
        super(DeviceParameterAdapter, self).__init__(*a, **k)
        self._alias_observable_property('automation_state', 'hasAutomation', getter=lambda self_: self_._has_automation())
        self.register_slot(self._adaptee, self.notify_displayValue, 'value')
        self.register_slot(self._adaptee, self.notify_unit, 'value')
        self.register_slot(self._adaptee, self.notify_automationActive, 'automation_state')
        self.register_slot(self._adaptee, self.notify_isActive, 'state')
        try:
            self.register_slot(self._adaptee, self.notify_valueItems, 'value_items')
        except SlotError:
            pass

    @listenable_property
    def valueItems(self):
        if self._adaptee.is_quantized:
            return self._adaptee.value_items
        return []

    @listenable_property
    def displayValue(self):
        return get_parameter_display_value(self._adaptee)

    @listenable_property
    def unit(self):
        return get_parameter_unit(self._adaptee)

    def _has_automation(self):
        no_automation = 0
        return self._adaptee.automation_state != no_automation

    @listenable_property
    def automationActive(self):
        active_automation = 1
        return self._adaptee.automation_state == active_automation

    @listenable_property
    def isActive(self):
        enabled_state = 0
        return self._adaptee.state == enabled_state


class EditModeOptionAdapter(ModelAdapter):
    __events__ = ('activeIndex', 'firstChoice')

    def __init__(self, *a, **k):
        super(EditModeOptionAdapter, self).__init__(*a, **k)
        if hasattr(self._adaptee, 'active_index'):
            self._alias_observable_property('active_index', 'activeIndex', getter=lambda self_: getattr(self_._adaptee, 'active_index', 0))
        if hasattr(self._adaptee, 'default_label'):
            self._alias_observable_property('default_label', 'firstChoice')

    @property
    def activeIndex(self):
        return 0

    @property
    def firstChoice(self):
        return getattr(self._adaptee, 'default_label', self._adaptee.name)

    @property
    def secondChoice(self):
        return getattr(self._adaptee, 'second_label', '')


class SimplerDeviceAdapter(ModelAdapter):

    def __init__(self, *a, **k):
        super(SimplerDeviceAdapter, self).__init__(*a, **k)
        self.register_slot(self._adaptee.view, self.notify_selected_slice, 'selected_slice')
        get_parameter = partial(_get_parameter_by_name, self._adaptee)
        self.sample_start = get_parameter('S Start')
        self.sample_length = get_parameter('S Length')
        self.loop_length = get_parameter('S Loop Length')
        self.loop_on = get_parameter('S Loop On')
        self.zoom = get_parameter('Zoom')
        self.__on_sample_changed.subject = self._adaptee
        self.__on_sample_changed()

    def _is_slicing(self):
        return self._adaptee.playback_mode == 2

    def _get_slice_times(self):
        slice_times = []
        if self._is_slicing() and liveobj_valid(self._adaptee.sample):
            try:
                slice_times = self._adaptee.sample.slices
            except RuntimeError:
                pass

        return slice_times

    @listens('sample')
    def __on_sample_changed(self):
        self.register_slot(self._adaptee.sample, self.notify_start_marker, 'start_marker')
        self.register_slot(self._adaptee.sample, self.notify_end_marker, 'end_marker')
        self.register_slot(self._adaptee.sample, self.notify_slices, 'slices')
        self.register_slot(self._adaptee.sample, self.notify_slicing_sensitivity, 'slicing_sensitivity')
        self.register_slot(self._adaptee.sample, self.notify_gain, 'gain')

    @listenable_property
    def slices(self):

        def unique_id(id_, existing = set()):
            while id_ in existing:
                id_ += 0.01

            existing.add(id_)
            return id_

        class SlicePoint(object):

            def __init__(self, __id__, time):
                self.__id__ = __id__
                self.time = time

        return [ SlicePoint(unique_id(time), time) for time in self._get_slice_times() ]

    @listenable_property
    def selected_slice(self):
        return find_if(lambda s: s.time == self.view.selected_slice, self.slices)

    @listenable_property
    def start_marker(self):
        if liveobj_valid(self._adaptee) and liveobj_valid(self._adaptee.sample):
            return self._adaptee.sample.start_marker
        return 0

    @listenable_property
    def end_marker(self):
        if liveobj_valid(self._adaptee) and liveobj_valid(self._adaptee.sample):
            return self._adaptee.sample.end_marker
        return 0

    @listenable_property
    def slicing_sensitivity(self):
        if liveobj_valid(self._adaptee) and liveobj_valid(self._adaptee.sample):
            return self._adaptee.sample.slicing_sensitivity
        return 0.0

    @listenable_property
    def gain(self):
        if liveobj_valid(self._adaptee) and liveobj_valid(self._adaptee.sample):
            return self._adaptee.sample.gain
        return 0.0


class VisibleAdapter(ModelAdapter):

    def __init__(self, adaptee = None, *a, **k):
        super(VisibleAdapter, self).__init__(adaptee=adaptee, *a, **k)
        self.__on_enabled_changed.subject = adaptee

    @listenable_property
    def visible(self):
        return self._adaptee.is_enabled()

    @listens('enabled')
    def __on_enabled_changed(self, enabled):
        self.notify_visible()


class TrackControlAdapter(VisibleAdapter):
    __events__ = ('scrollOffset',)

    def __init__(self, *a, **k):
        super(TrackControlAdapter, self).__init__(*a, **k)
        self._alias_observable_property('scroll_offset', 'scrollOffset')


class OptionsListAdapter(VisibleAdapter):
    __events__ = ('selectedItem',)

    def __init__(self, *a, **k):
        super(OptionsListAdapter, self).__init__(*a, **k)
        self._alias_observable_property('selected_item', 'selectedItem')


class ItemListAdapter(VisibleAdapter):
    __events__ = ('selectedItem',)

    def __init__(self, *a, **k):
        super(ItemListAdapter, self).__init__(*a, **k)
        self.__on_selected_item_changed.subject = self._adaptee.item_provider

    @listens('selected_item')
    def __on_selected_item_changed(self):
        self.notify_selectedItem()

    @property
    def selectedItem(self):
        return self._adaptee.item_provider.selected_item


class ItemSlotAdapter(ModelAdapter):

    @property
    def icon(self):
        return getattr(self._adaptee, 'icon', '')


class DeviceAdapter(ModelAdapter):
    __events__ = ('is_active',)

    def __init__(self, *a, **k):
        from ..device_navigation import is_drum_pad
        super(DeviceAdapter, self).__init__(*a, **k)
        item = self._unwrapped_item()
        if hasattr(item, 'is_active'):
            self.__on_is_active_changed.subject = item
        elif is_drum_pad(item):
            self.__on_is_active_changed.subject = item.canonical_parent
            self.__on_mute_changed.subject = item

    def _unwrapped_item(self):
        return getattr(self._adaptee, 'item', self._adaptee)

    @property
    def name(self):
        item = self._unwrapped_item()
        if hasattr(item, 'class_name') and item.class_name in DEVICE_TYPES_WITH_PRESET_NAME:
            return item.name
        else:
            return getattr(item, 'class_display_name', item.name)

    @property
    def class_name(self):
        import Live
        item = self._unwrapped_item()
        if isinstance(item, Live.DrumPad.DrumPad):
            return 'DrumPad'
        else:
            return getattr(item, 'class_name', '')

    @property
    def nestingLevel(self):
        try:
            return self._adaptee.nesting_level
        except AttributeError:
            return 0

    @property
    def is_active(self):
        from ..device_navigation import is_active_element
        try:
            return is_active_element(self._unwrapped_item())
        except AttributeError:
            return True

    @listens('is_active')
    def __on_is_active_changed(self):
        self.notify_is_active()

    @listens('mute')
    def __on_mute_changed(self):
        self.notify_is_active()

    @property
    def icon(self):
        return getattr(self._adaptee, 'icon', '')


class TrackAdapter(ModelAdapter):
    __events__ = ('activated',)

    def __init__(self, *a, **k):
        super(TrackAdapter, self).__init__(*a, **k)
        if hasattr(self._adaptee, 'mute'):
            self.__on_mute_changed.subject = self._adaptee
            self.__on_solo_changed.subject = self._adaptee
            self.__on_muted_via_solo_changed.subject = self._adaptee
        try:
            self.register_slot(self._adaptee, self.notify_colorIndex, 'color_index')
        except SlotError:
            pass

        try:
            self.register_slot(self._adaptee.parent_track, self.notify_parentColorIndex, 'color_index')
        except AttributeError:
            pass

        try:
            self.register_slot(self._adaptee, self.notify_isFrozen, 'is_frozen')
        except SlotError:
            pass

        try:
            self.register_slot(self._adaptee, self.notify_arm, 'arm')
        except SlotError:
            pass

    @property
    def isFoldable(self):
        return getattr(self._adaptee, 'is_foldable', False)

    @property
    def canShowChains(self):
        return getattr(self._adaptee, 'can_show_chains', False)

    @property
    def containsDrumRack(self):
        from pushbase.device_chain_utils import find_instrument_meeting_requirement
        return find_instrument_meeting_requirement(lambda i: i.can_have_drum_pads, self._adaptee) is not None

    @property
    def nestingLevel(self):
        try:
            return self._adaptee.nesting_level
        except AttributeError:
            return 0

    @property
    def activated(self):
        try:
            return not (self._adaptee.muted_via_solo or self._adaptee.mute and not self._adaptee.solo)
        except RuntimeError:
            return True

    @listenable_property
    def isFrozen(self):
        try:
            return self._adaptee.is_frozen
        except AttributeError:
            return False

    @listenable_property
    def arm(self):
        try:
            if self._adaptee.can_be_armed:
                return self._adaptee.arm
            return False
        except AttributeError:
            return False

    @listens('mute')
    def __on_mute_changed(self):
        self.notify_activated()

    @listens('solo')
    def __on_solo_changed(self):
        self.notify_activated()

    @listens('muted_via_solo')
    def __on_muted_via_solo_changed(self):
        self.notify_activated()

    @staticmethod
    def _convert_color_index(color_index):
        from ..colors import UNCOLORED_INDEX
        if color_index is None:
            return UNCOLORED_INDEX
        return color_index

    @listenable_property
    def colorIndex(self):
        try:
            return self._convert_color_index(self._adaptee.color_index)
        except AttributeError:
            return self.parentColorIndex

    @listenable_property
    def parentColorIndex(self):
        try:
            return self._convert_color_index(self._adaptee.parent_track.color_index)
        except AttributeError:
            return -1

    @property
    def isMaster(self):
        try:
            return self._adaptee == self._adaptee.canonical_parent.master_track
        except AttributeError:
            return False

    @property
    def isAudio(self):
        try:
            return not self._adaptee.has_midi_input
        except AttributeError:
            return False


class TrackListAdapter(VisibleAdapter):
    __events__ = ('selectedTrack',)

    def __init__(self, *a, **k):
        super(TrackListAdapter, self).__init__(*a, **k)
        self._alias_observable_property('selected_track', 'selectedTrack')


class BrowserItemAdapter(ModelAdapter):

    @property
    def icon(self):
        return getattr(self._adaptee, 'icon', '')


class BrowserListWrapper(SlotManager):
    """
    Custom object wrapper that takes care of binding a browser list and serializing it.
    This is necessary to greatly improve performance and avoid unnecessary wrapping of
    each browser item.
    """

    def __init__(self, browser_list, notifier = None, *a, **k):
        super(BrowserListWrapper, self).__init__(*a, **k)
        self._browser_list = browser_list
        self._notifier = notifier
        slot = Slot(browser_list, self.notify, 'items')
        slot.connect()
        self.register_slot(slot)

    @staticmethod
    def _serialize_browser_item(item):
        return {'id': item.uri,
         'name': item.name,
         'is_loadable': item.is_loadable,
         'icon': getattr(item, 'icon', '')}

    def to_json(self):
        return map(self._serialize_browser_item, self._browser_list.items)

    def notify(self):
        self._notifier.structural_change()

    def disconnect(self):
        super(BrowserListWrapper, self).disconnect()
        self._browser_list = None


class LiveDialogAdapter(VisibleAdapter):

    @property
    def text(self):
        text = self._adaptee.text
        if text is not None:
            return strip_formatted_string(text)
        return ''