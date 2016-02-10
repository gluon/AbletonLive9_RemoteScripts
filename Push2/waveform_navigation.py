#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/waveform_navigation.py
from __future__ import absolute_import, print_function
import math
from collections import namedtuple, OrderedDict
from functools import partial
from itertools import imap
from ableton.v2.base import SlotManager, Subject, const, clamp, depends, find_if, index_if, lazy_attribute, listenable_property, listens, listens_group, liveobj_changed, task
from ableton.v2.control_surface.control import EncoderControl
FocusMarker = namedtuple('FocusMarker', ['name', 'position'])

def ease_out(t, degree):
    return 1 - (1 - t) ** degree


def inverse_ease_out(t, degree):
    if t < 1.0:
        return 1.0 - (1.0 - t) ** (1.0 / degree)
    return 1.0


def interpolate(from_value, to_value, t, ease_out_degree):
    """
    Interpolate between from_value and to_value given the value t [0..1]
    ease_out_degree alters the interpolation curve to ease out more, the higher
    the value, where 1 is no easing.
    """
    t = ease_out(t, ease_out_degree)
    return (1.0 - t) * from_value + t * to_value


def interpolate_inverse(from_value, to_value, current_value, ease_out_degree):
    """
    The inverse function of interpolate solved to t
    """
    t = 0.0 if from_value - to_value == 0 else -float(current_value - from_value) / float(from_value - to_value)
    return inverse_ease_out(t, ease_out_degree)


def calc_easing_degree_for_proportion(proportion):
    """
    Calculates a reasonable easing degree for a given proportion.
    """
    return -math.log10(proportion) + 1


def compare_region_length(r1, r2):
    """
    Returns a negative, zero or positive number, depending on whether r1 is considered
    smaller than, equal to, or larger than r2
    """
    r1 = r1()
    r2 = r2()
    s1 = r1[1] - r1[0]
    s2 = r2[1] - r2[0]
    return int(s2 - s1)


class WaveformNavigation(SlotManager, Subject):
    """ Class for managing a visible area of a waveform """
    visible_start = listenable_property.managed(0)
    visible_end = listenable_property.managed(0)
    animate_visible_region = listenable_property.managed(False)
    show_focus = listenable_property.managed(False)
    ZOOM_SENSITIVITY = 1.5
    MIN_VISIBLE_LENGTH = 1000
    WAVEFORM_WIDTH_IN_PX = 933
    MARGIN_IN_PX = 121
    RELATIVE_FOCUS_MARGIN = float(MARGIN_IN_PX) / WAVEFORM_WIDTH_IN_PX

    def __init__(self, waveform_length = None, *a, **k):
        raise waveform_length is not None or AssertionError
        raise waveform_length > 0 or AssertionError
        super(WaveformNavigation, self).__init__(*a, **k)
        self._length = waveform_length
        self._focused_object = None
        self._focus_marker = FocusMarker('', 0)
        self._touched_objects = set()
        self._has_tasks = False
        self._target_region_getter = self.get_start_end_region
        self._source_region_getter = lambda : (0, self._length)
        self._request_select_region = False
        self.set_visible_region(0, self._length)

    def disconnect(self):
        super(WaveformNavigation, self).disconnect()
        if self._has_tasks:
            self._tasks.kill()
            self._tasks.clear()

    def get_object_identifier(self, obj):
        raise NotImplementedError

    def get_zoom_object(self):
        raise NotImplementedError

    def get_start_object_identifier(self):
        raise NotImplementedError

    def get_end_object_identifier(self):
        raise NotImplementedError

    def get_start_end_region(self):
        return self._make_region_from_region_identifiers(self.get_start_object_identifier(), self.get_end_object_identifier())

    @lazy_attribute
    def focusable_object_connections(self):
        return {}

    @property
    def visible_length(self):
        """ Returns the length of the visible area """
        return self.visible_end - self.visible_start

    @property
    def visible_proportion(self):
        """ Returns the proportion between the visible length and the sample length """
        return self.visible_length / float(self._length)

    def set_visible_region(self, start, end, animate = False):
        self.animate_visible_region = animate
        self.visible_start = clamp(start, 0, self._length)
        self.visible_end = clamp(end, 0, self._length)

    def zoom(self, value):
        """ Zooms in or out of the waveform start
            value should be between -1.0 and 1.0, where 1.0 will zoom in as much as
            possible and -1.0 will zoom out completely.
        """
        animate = self._request_select_region
        if self._request_select_region:
            self._select_region(value > 0)
        source = self._source_region_getter()
        target = self._target_region_getter()
        source_length = float(source[1] - source[0])
        target_length = float(target[1] - target[0])
        easing_degree = calc_easing_degree_for_proportion(target_length / source_length)
        if source[0] != target[0]:
            t = interpolate_inverse(source[0], target[0], self.visible_start, easing_degree)
        else:
            t = interpolate_inverse(source[1], target[1], self.visible_end, easing_degree)
        t = clamp(t + value * self.ZOOM_SENSITIVITY, 0.0, 1.0)
        self.set_visible_region(interpolate(source[0], target[0], t, easing_degree), interpolate(source[1], target[1], t, easing_degree), animate=animate)
        self.show_focus = True
        self.try_hide_focus_delayed()

    def focus_object(self, obj):
        if obj != self.get_zoom_object():
            identifier = self.get_object_identifier(obj)
            if identifier in self.focusable_object_connections:
                connection = self.focusable_object_connections[identifier]
                animate = liveobj_changed(self._focused_object, obj)
                self._focused_object = obj
                self._focus_connection(connection, animate=animate)
                return True
        return False

    def _focus_connection(self, connection, animate = False):
        """ Focuses the connection in the waveform and brings it into the visible range.
            The visible length is preserved. The position is aligned to the left or right
            of the visible range, with a certain margin defined by RELATIVE_FOCUS_MARGIN.
            If the connections boundary is already in the visible range, the visible
            position is not changing.
            :connection: the object connection to focus
            :align_right: focuses the position on the left or right side of the
            :animate: should be set to True if, if it should animate to the new position
        """
        position = connection.getter()
        visible_length = self.visible_length
        visible_margin = visible_length * self.RELATIVE_FOCUS_MARGIN
        length = self._length
        if connection.align_right:
            start = min(connection.boundary_getter() - visible_margin, self.visible_start) if connection else 0
            right = max(position + visible_margin, start + visible_length)
            self.set_visible_region(clamp(right - visible_length, 0, length - visible_length), clamp(right, visible_length, length), animate)
        else:
            end = max(connection.boundary_getter() + visible_margin, self.visible_end) if connection else length
            left = min(position - visible_margin, end - visible_length)
            self.set_visible_region(clamp(left, 0, length - visible_length), clamp(left + visible_length, visible_length, length), animate)
        self._focus_marker = FocusMarker(connection.focus_name, position)
        self.notify_focus_marker()
        self._request_select_region = True

    @listenable_property
    def focus_marker(self):
        return self._focus_marker

    def touch_object(self, obj):
        is_zoom_object = obj == self.get_zoom_object()
        if is_zoom_object:
            if self._visible_region_reaches(self._target_region_getter()) or self._visible_region_reaches(self._source_region_getter()):
                self._request_select_region = True
        if self.focus_object(obj) or is_zoom_object:
            self._touched_objects.add(obj)
            self.show_focus = True

    def release_object(self, obj):
        if obj in self._touched_objects:
            self._touched_objects.remove(obj)
            self.try_hide_focus()

    def change_object(self, obj):
        if self.focus_object(obj) or obj == self.get_zoom_object():
            self.show_focus = True
            self.try_hide_focus_delayed()

    def try_hide_focus(self):
        """ Hides the focus, if the focused object is not longer touched """
        if self._should_hide_focus():
            self.show_focus = False

    def try_hide_focus_delayed(self):
        """ Hides the focus after some time, if the focused object is not
            longer touched
        """
        if self._hide_focus_task and self._should_hide_focus():
            self._hide_focus_task.restart()

    def _should_hide_focus(self):
        return self.get_zoom_object() not in self._touched_objects and self._focused_object not in self._touched_objects

    def reset_focus_and_animation(self):
        self.show_focus = False
        self.animate_visible_region = False
        self._touched_objects = set()

    @lazy_attribute
    @depends(parent_task_group=const(None))
    def _tasks(self, parent_task_group = None):
        if parent_task_group is not None:
            tasks = parent_task_group.add(task.TaskGroup())
            self._has_tasks = True
            return tasks

    @lazy_attribute
    def _hide_focus_task(self):
        tasks = self._tasks
        if tasks is not None:
            return tasks.add(task.sequence(task.wait(EncoderControl.TOUCH_TIME), task.run(self.try_hide_focus)))

    def _add_margin_to_region(self, start, end):
        margin = self.RELATIVE_FOCUS_MARGIN
        start1 = (margin * start + end * margin - start) / (2 * margin - 1)
        end1 = (end - margin * start1) / (1 - margin)
        start1 = clamp(start1, 0, self._length)
        end1 = clamp(end1, 0, self._length)
        return (start1, end1)

    def _get_position_for_identifier(self, identifier):
        return self.focusable_object_connections[identifier].getter()

    def _make_region_from_region_identifiers(self, start_identifier, end_identifier):
        return self._add_margin_to_region(self._get_position_for_identifier(start_identifier), self._get_position_for_identifier(end_identifier))

    def _make_region_from_position_identifier(self, identifier):
        connection = self.focusable_object_connections[identifier]
        align_right = connection.align_right
        position = connection.getter()
        length = self.MIN_VISIBLE_LENGTH
        margin = self.RELATIVE_FOCUS_MARGIN * length
        if align_right:
            right = min(position + margin, self._length)
            left = max(right - length, 0)
        else:
            left = max(position - margin, 0)
            right = min(left + length, self._length)
        return (left, right)

    def _make_region_for_focused_object(self):
        if self._focused_object is not None:
            return self._make_region_from_position_identifier(self.get_object_identifier(self._focused_object))
        return (0, 0)

    def _region_inside(self, inner_region, outer_region):
        outer_region = (int(outer_region[0]), int(outer_region[1]))
        inner_region = (int(inner_region[0]), int(inner_region[1]))
        return inner_region[0] >= outer_region[0] and inner_region[1] <= outer_region[1] and outer_region != inner_region

    def _visible_region_reaches(self, region):
        region = (int(region[0]), int(region[1]))
        visible_region = (int(self.visible_start), int(self.visible_end))
        return region == visible_region

    def _visible_region_inside(self, region):
        return self._region_inside((self.visible_start, self.visible_end), region)

    def _get_region_getters_for_focused_identifier(self):
        focused_identifier = self.get_object_identifier(self._focused_object)
        return self.focusable_object_connections[focused_identifier].region_getters

    def _get_unique_region_getters(self):
        """
        Eliminates duplicates of the current regions and returns the remaining getters
        sorted by the length of the regions.
        """
        getters = OrderedDict()
        for region_getter in self._get_region_getters_for_focused_identifier():
            getters[region_getter()] = region_getter

        return sorted(getters.values(), cmp=compare_region_length)

    def _select_region_around_visible_region(self):
        region_getters = self._get_unique_region_getters()
        source_getter = find_if(lambda g: self._visible_region_inside(g()), region_getters[1::-1])
        if source_getter is not None:
            self._source_region_getter = source_getter
            self._target_region_getter = region_getters[region_getters.index(source_getter) + 1]

    def _select_reached_region(self, zoom_in):
        region_getters = self._get_unique_region_getters()
        i = index_if(self._visible_region_reaches, imap(apply, region_getters))
        if i != len(region_getters):
            if zoom_in:
                if i < len(region_getters) - 1:
                    self._source_region_getter = region_getters[i]
                    self._target_region_getter = region_getters[i + 1]
            elif i > 0:
                self._source_region_getter = region_getters[i - 1]
                self._target_region_getter = region_getters[i]
            return True
        return False

    def _select_region(self, zoom_in):
        if not self._select_reached_region(zoom_in):
            self._select_region_around_visible_region()
        self._request_select_region = False


ObjectConnection = namedtuple('ObjectConnection', ['getter',
 'align_right',
 'focus_name',
 'region_getters',
 'boundary_getter'])

class SimplerWaveformNavigation(WaveformNavigation):
    """ Extends the WaveformNavigation class by the concept of focusing parameters
        and slices.
    """
    selected_slice_focus = object()

    def __init__(self, simpler = None, *a, **k):
        super(SimplerWaveformNavigation, self).__init__(*a, **k)
        self._simpler = simpler
        focusable_parameters = [ self._simpler.get_parameter_by_name(n) for n in self.focusable_object_connections ]
        self.__on_selected_slice_changed.subject = simpler.view
        self.__on_parameter_value_changed.replace_subjects(focusable_parameters)

    @lazy_attribute
    def focusable_object_connections(self):
        return {'Start': ObjectConnection(lambda : self._simpler.sample.start_marker, False, 'start_marker', (lambda : (0, self._length), self.get_start_end_region, self._make_region_for_focused_object), partial(self._get_position_for_identifier, 'End')),
         'End': ObjectConnection(lambda : self._simpler.sample.end_marker, True, 'end_marker', (lambda : (0, self._length), self.get_start_end_region, self._make_region_for_focused_object), partial(self._get_position_for_identifier, 'Start')),
         'S Start': ObjectConnection(lambda : self._simpler.view.sample_start, False, 'position', (lambda : (0, self._length),
                     self.get_start_end_region,
                     self.get_sample_start_end_region,
                     self._make_region_for_focused_object), partial(self._get_position_for_identifier, 'S Length')),
         'S Length': ObjectConnection(lambda : self._simpler.view.sample_end, True, 'position', (lambda : (0, self._length),
                      self.get_start_end_region,
                      self.get_sample_start_end_region,
                      self._make_region_for_focused_object), partial(self._get_position_for_identifier, 'S Start')),
         'S Loop Length': ObjectConnection(lambda : self._simpler.view.sample_loop_start, False, 'position', (lambda : (0, self._length),
                           self.get_start_end_region,
                           self.get_sample_start_end_region,
                           self.get_sample_loop_start_end_region,
                           self._make_region_for_focused_object), partial(self._get_position_for_identifier, 'S Length')),
         self.selected_slice_focus: ObjectConnection(lambda : self._simpler.view.selected_slice, False, '', (lambda : (0, self._length),
                                     self.get_start_end_region,
                                     self.get_slice_region,
                                     self._make_region_for_focused_object), self.get_next_slice_position)}

    def get_object_identifier(self, obj):
        if hasattr(obj, 'name'):
            return obj.name
        return self.selected_slice_focus

    def get_zoom_object(self):
        return self._simpler.zoom

    def get_start_object_identifier(self):
        return 'Start'

    def get_end_object_identifier(self):
        return 'End'

    def get_sample_start_end_region(self):
        return self._make_region_from_region_identifiers('S Start', 'S Length')

    def get_sample_loop_start_end_region(self):
        return self._make_region_from_region_identifiers('S Loop Length', 'S Length')

    def get_next_slice_position(self):
        selected_slice = self._get_selected_slice_index()
        if selected_slice < 0 or selected_slice + 1 >= len(self._simpler.sample.slices):
            return self._get_position_for_identifier(self.get_end_object_identifier())
        return self._simpler.sample.slices[selected_slice + 1]

    def get_slice_region(self):
        return self._add_margin_to_region(self._get_position_for_identifier(self.selected_slice_focus), self.get_next_slice_position())

    @listens_group('value')
    def __on_parameter_value_changed(self, parameter):
        self.change_object(parameter)

    @listens('selected_slice')
    def __on_selected_slice_changed(self):
        slice_index = self._get_selected_slice_index()
        if slice_index != -1:
            self.focus_object(slice_index)

    def _get_selected_slice_index(self):
        try:
            return self._simpler.sample.slices.index(self._simpler.view.selected_slice)
        except ValueError:
            pass

        return -1


class AudioClipWaveformNavigation(WaveformNavigation):
    """ WaveformNavigation that adds the concept of focus for audio clips to the. """
    zoom_focus = object()
    start_marker_focus = object()
    loop_start_focus = object()
    loop_end_focus = object()

    def __init__(self, clip = None, *a, **k):
        super(AudioClipWaveformNavigation, self).__init__(*a, **k)
        self._clip = clip
        self.__on_is_recording_changed.subject = clip

    @lazy_attribute
    def focusable_object_connections(self):
        return {self.start_marker_focus: ObjectConnection(lambda : self._clip.view.sample_start_marker, False, 'start_marker', (lambda : (0, self._length), self.get_start_end_region, self._make_region_for_focused_object), partial(self._get_position_for_identifier, self.loop_end_focus)),
         self.loop_start_focus: ObjectConnection(lambda : self._clip.view.sample_loop_start, False, 'position', (lambda : (0, self._length), self.get_start_end_region, self._make_region_for_focused_object), partial(self._get_position_for_identifier, self.loop_end_focus)),
         self.loop_end_focus: ObjectConnection(lambda : self._clip.view.sample_loop_end, True, 'end_marker', (lambda : (0, self._length), self.get_start_end_region, self._make_region_for_focused_object), self._get_start_position)}

    def get_object_identifier(self, obj):
        return obj

    def get_zoom_object(self):
        return self.zoom_focus

    def get_start_object_identifier(self):
        return self.loop_start_focus

    def get_end_object_identifier(self):
        return self.loop_end_focus

    def _get_start_position(self):
        start_marker_position = self._get_position_for_identifier(self.start_marker_focus)
        loop_start_position = self._get_position_for_identifier(self.loop_start_focus)
        return min(start_marker_position, loop_start_position)

    def get_start_end_region(self):
        return self._add_margin_to_region(self._get_start_position(), self._get_position_for_identifier(self.loop_end_focus))

    @listens('is_recording')
    def __on_is_recording_changed(self):
        self._length = self._clip.view.sample_length
        self.set_visible_region(0, self._length)