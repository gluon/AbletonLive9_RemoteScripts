#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push/browser_component.py
from __future__ import absolute_import, print_function
from functools import partial
from itertools import izip, izip_longest
import string
import re
import Live
from ableton.v2.base import find_if, clamp, nop, memoize, listens, listens_group, task
from ableton.v2.control_surface import CompoundComponent
from ableton.v2.control_surface.control import ButtonControl, ToggleButtonControl
from ableton.v2.control_surface.elements import DisplayDataSource
from pushbase import consts
from pushbase.scrollable_list import ListComponent, DefaultItemFormatter
from .browser_model import filter_type_for_browser, EmptyBrowserModel
FilterType = Live.Browser.FilterType
DeviceType = Live.Device.DeviceType

def make_stem_cleaner(stem):
    """ Returns a function that can be used to remove the stem from a sentence """
    if stem[-1] == 's':
        stem = stem[:-1]
    if len(stem) > 2:
        return _memoized_stem_cleaner(stem)
    return nop


@memoize
def _memoized_stem_cleaner(stem):
    ellipsis = consts.CHAR_ELLIPSIS
    stem = re.escape(stem)
    rule1 = re.compile(u'([a-z])' + stem + u's?([ A-Z])')
    rule2 = re.compile(u'[' + ellipsis + ' \\-]' + stem + u's?([\\-' + ellipsis + u' A-Z])')
    rule3 = re.compile(u'' + stem + u's?$')

    def cleaner(short_name):
        short_name = ' ' + short_name
        short_name = rule1.sub(u'\\1' + ellipsis + u'\\2', short_name)
        short_name = rule2.sub(ellipsis + u'\\1', short_name)
        short_name = rule3.sub(ellipsis, short_name)
        return short_name.strip(' ')

    return cleaner


def split_stem(sentence):
    """ Splits camel cased sentence into words """
    sentence = re.sub('([a-z])([A-Z])', u'\\1 \\2', sentence)
    return sentence.split()


_stripper_double_spaces = re.compile(u' [\\- ]*')
_stripper_double_ellipsis = re.compile(consts.CHAR_ELLIPSIS + u'+')
_stripper_space_ellipsis = re.compile(u'[\\- ]?' + consts.CHAR_ELLIPSIS + u'[\\- ]?')

def full_strip(string):
    """ Strip string for double spaces and dashes """
    string = _stripper_double_spaces.sub(' ', string)
    string = _stripper_double_ellipsis.sub(consts.CHAR_ELLIPSIS, string)
    string = _stripper_space_ellipsis.sub(consts.CHAR_ELLIPSIS, string)
    return string.strip(' ')


class BrowserComponent(CompoundComponent):
    """
    Component for controlling the Live library browser.  It has 4
    browsing columns that are controlled by encoders and state
    buttons.  The contents of these lists are provided by a browser
    model -- see BrowserModel and derivatives.
    """
    __events__ = ('load_item',)
    NUM_COLUMNS = 4
    COLUMN_SIZE = 4
    enter_button = ButtonControl(**consts.SIDE_BUTTON_COLORS)
    exit_button = ButtonControl(**consts.SIDE_BUTTON_COLORS)
    shift_button = ButtonControl()
    prehear_button = ToggleButtonControl(toggled_color='Browser.Prehear', untoggled_color='Browser.PrehearOff')

    def __init__(self, browser = None, make_browser_model = None, preferences = dict(), *a, **k):
        super(BrowserComponent, self).__init__(*a, **k)
        raise make_browser_model is not None or AssertionError
        self._browser = browser or self.application().browser
        self._browser_model = EmptyBrowserModel(browser=self._browser)
        self._make_browser_model = make_browser_model
        num_data_sources = self.NUM_COLUMNS * self.COLUMN_SIZE
        self._data_sources = map(DisplayDataSource, ('',) * num_data_sources)
        self._last_loaded_item = None
        self._default_item_formatter = DefaultItemFormatter()
        self._list_components = self.register_components(*[ ListComponent() for _ in xrange(self.NUM_COLUMNS) ])
        for i, component in enumerate(self._list_components):
            component.do_trigger_action = lambda item: self._do_load_item(item)
            component.last_action_item = lambda : self._last_loaded_item
            component.item_formatter = partial(self._item_formatter, i)

        self._preferences = preferences
        self._select_buttons = []
        self._state_buttons = []
        self._encoder_controls = []
        self._on_selected_item.replace_subjects(self._list_components)
        self._on_list_item_action.replace_subjects(self._list_components)
        self._on_hotswap_target_changed.subject = self._browser
        self._on_filter_type_changed.subject = self._browser
        self._on_browser_full_refresh.subject = self._browser
        self._scroll_offset = 0
        self._max_scroll_offset = 0
        self._max_hierarchy = 0
        self._last_filter_type = None
        self._skip_next_preselection = False
        self._browser_model_dirty = True
        self._on_content_lists_changed()
        self.prehear_button.is_toggled = preferences.setdefault('browser_prehear', True)
        self._last_selected_item = None

    def disconnect(self):
        self._last_selected_item = None
        super(BrowserComponent, self).disconnect()

    def set_display_line1(self, display):
        self.set_display_line_with_index(display, 0)

    def set_display_line2(self, display):
        self.set_display_line_with_index(display, 1)

    def set_display_line3(self, display):
        self.set_display_line_with_index(display, 2)

    def set_display_line4(self, display):
        self.set_display_line_with_index(display, 3)

    def set_display_line_with_index(self, display, index):
        if display:
            sources = self._data_sources[index::self.COLUMN_SIZE]
            display.set_data_sources(sources)

    def set_select_buttons(self, buttons):
        for button in buttons or []:
            if button:
                button.reset()

        self._on_select_matrix_value.subject = buttons or None
        self._select_buttons = buttons
        buttons = buttons or (None, None, None, None, None, None, None, None)
        for component, button in izip(self._list_components, buttons[1::2]):
            self._set_button_if_enabled(component, 'action_button', button)

        for component, button in izip(self._list_components, buttons[::2]):
            if self.shift_button.is_pressed:
                self._set_button_if_enabled(component, 'prev_page_button', button)
                self._set_button_if_enabled(component, 'select_prev_button', None)
            else:
                self._set_button_if_enabled(component, 'prev_page_button', None)
                self._set_button_if_enabled(component, 'select_prev_button', button)

    def set_state_buttons(self, buttons):
        for button in buttons or []:
            if button:
                button.reset()

        self._on_state_matrix_value.subject = buttons or None
        self._state_buttons = buttons
        buttons = buttons or (None, None, None, None, None, None, None, None)
        for component, button in izip(self._list_components, buttons[::2]):
            if self.shift_button.is_pressed:
                self._set_button_if_enabled(component, 'next_page_button', button)
                self._set_button_if_enabled(component, 'select_next_button', None)
            else:
                self._set_button_if_enabled(component, 'next_page_button', None)
                self._set_button_if_enabled(component, 'select_next_button', button)

        for button in buttons[1::2]:
            if button and self.is_enabled():
                button.set_light('DefaultButton.Disabled')

    @shift_button.value
    def shift_button(self, value, control):
        self.set_select_buttons(self._select_buttons)
        self.set_state_buttons(self._state_buttons)

    def _set_button_if_enabled(self, component, name, button):
        control = getattr(component, name)
        if component.is_enabled(explicit=True):
            control.set_control_element(button)
        else:
            control.set_control_element(None)
            if button and self.is_enabled():
                button.set_light('DefaultButton.Disabled')

    def set_encoder_controls(self, encoder_controls):
        if encoder_controls:
            num_active_lists = len(self._browser_model.content_lists) - self._scroll_offset
            num_assignable_lists = min(num_active_lists, len(encoder_controls) / 2)
            index = 0
            for component in self._list_components[:num_assignable_lists - 1]:
                component.encoders.set_control_element(encoder_controls[index:index + 2])
                index += 2

            self._list_components[num_assignable_lists - 1].encoders.set_control_element(encoder_controls[index:])
        else:
            for component in self._list_components:
                component.encoders.set_control_element([])

        self._encoder_controls = encoder_controls

    def update(self):
        super(BrowserComponent, self).update()
        if self.is_enabled():
            self.set_state_buttons(self._state_buttons)
            self.set_select_buttons(self._select_buttons)
            self._update_browser_model()
        else:
            self._browser.stop_preview()

    def reset_load_memory(self):
        self._update_load_memory(None)

    def _do_load_item(self, item):
        self.do_load_item(item)
        self._update_load_memory(item)
        self._skip_next_preselection = True

        def reset_skip_next_preselection():
            self._skip_next_preselection = False

        self._tasks.add(task.run(reset_skip_next_preselection))

    def _update_load_memory(self, item):
        self._last_loaded_item = item
        for component in self._list_components:
            component.update()

    def do_load_item(self, item):
        item.action()
        self.notify_load_item(item.content)

    def back_to_top(self):
        self._set_scroll_offset(0)

    def _set_scroll_offset(self, offset):
        self._scroll_offset = offset
        self._on_content_lists_changed()
        scrollable_list = self._list_components[-1].scrollable_list
        if scrollable_list:
            scrollable_list.request_notify_item_activated()

    def _update_navigation_button_state(self):
        self.exit_button.enabled = self._scroll_offset > 0
        self.enter_button.enabled = self._scroll_offset < self._max_scroll_offset

    def _shorten_item_name(self, shortening_limit, list_index, item_name):
        """
        Creates the name of an item shortened by removing words from the parents name
        """

        def is_short_enough(item_name):
            return len(item_name) <= 9

        content_lists = self._browser_model.content_lists
        parent_lists = reversed(content_lists[max(0, list_index - 3):list_index])
        for content_list in parent_lists:
            if is_short_enough(item_name):
                break
            parent_name = unicode(content_list.selected_item)
            stems = split_stem(parent_name)
            for stem in stems:
                short_name = make_stem_cleaner(stem)(item_name)
                short_name = full_strip(short_name)
                item_name = short_name if len(short_name) > 4 else item_name
                if is_short_enough(item_name):
                    break

        if len(item_name) >= shortening_limit and item_name[-1] == consts.CHAR_ELLIPSIS:
            return item_name[:-1]
        return item_name

    def _item_formatter(self, depth, index, item, action_in_progress):
        display_string = ''
        separator_length = len(self._data_sources[self.COLUMN_SIZE * depth].separator)
        shortening_limit = 16 - separator_length
        if item:
            item_name = 'Loading...' if action_in_progress else self._shorten_item_name(shortening_limit, depth + self._scroll_offset, unicode(item))
            display_string = consts.CHAR_SELECT if item and item.is_selected else ' '
            display_string += item_name
            if depth == len(self._list_components) - 1 and item.is_selected and self._scroll_offset < self._max_hierarchy:
                display_string = string.ljust(display_string, consts.DISPLAY_LENGTH / 4 - 1)
                shortening_limit += 1
                display_string = display_string[:shortening_limit] + consts.CHAR_ARROW_RIGHT
            if depth == 0 and self._scroll_offset > 0:
                prefix = consts.CHAR_ARROW_LEFT if index == 0 else ' '
                display_string = prefix + display_string
        return display_string[:shortening_limit + 1]

    @enter_button.pressed
    def enter_button(self, control):
        self._set_scroll_offset(min(self._max_scroll_offset, self._scroll_offset + 1))

    @exit_button.pressed
    def exit_button(self, control):
        self._set_scroll_offset(max(0, self._scroll_offset - 1))

    @prehear_button.toggled
    def prehear_button(self, toggled, button):
        if not toggled:
            self._browser.stop_preview()
        elif self._last_selected_item is not None:
            self._last_selected_item.preview()
        self._preferences['browser_prehear'] = toggled

    @listens('hotswap_target')
    def _on_hotswap_target_changed(self):
        if not self._skip_next_preselection:
            self._set_scroll_offset(0)
        self._update_browser_model()

    @listens('filter_type')
    def _on_filter_type_changed(self):
        self._update_browser_model()

    @listens('full_refresh')
    def _on_browser_full_refresh(self):
        self._browser_model_dirty = True

    def _update_browser_model(self):
        if self.is_enabled():
            self._do_update_browser_model()

    def _create_browser_model_of_type(self, filter_type):
        self._last_filter_type = filter_type
        new_model = self._make_browser_model(self._browser, filter_type)
        if self._browser_model and self._browser_model.can_be_exchanged(new_model) and new_model.can_be_exchanged(self._browser_model):
            self._browser_model.exchange_model(new_model)
            new_model.disconnect()
        else:
            self.disconnect_disconnectable(self._browser_model)
            self._browser_model = self.register_slot_manager(new_model)
            self._on_content_lists_changed.subject = self._browser_model
            self._on_selection_updated.subject = self._browser_model
        self._browser_model.update_content()

    def _do_update_browser_model(self):
        filter_type = filter_type_for_browser(self._browser)
        if filter_type != self._last_filter_type:
            self._create_browser_model_of_type(filter_type)
        elif self._browser_model_dirty:
            self._browser_model.update_content()
        elif not self._skip_next_preselection:
            self._browser_model.update_selection()
        self._skip_next_preselection = False
        self._browser_model_dirty = False

    @listens_group('item_action')
    def _on_list_item_action(self, item, _):
        self.notify_load_item(item.content)

    @listens_group('selected_item')
    def _on_selected_item(self, item, _):
        if item is not None and self.prehear_button.is_toggled:
            item.preview()
        self._last_selected_item = item

    @listens('selection_updated')
    def _on_selection_updated(self, index):
        more_content_available = len(self._browser_model.content_lists) > self.NUM_COLUMNS + self._scroll_offset
        required_scroll_offset = index - (self.NUM_COLUMNS - 1)
        if more_content_available and required_scroll_offset > self._scroll_offset:
            self._set_scroll_offset(self._scroll_offset + 1)
            self._browser_model.update_selection()

    @listens('content_lists')
    def _on_content_lists_changed(self):
        self._last_selected_item = None
        components = self._list_components
        contents = self._browser_model.content_lists[self._scroll_offset:]
        messages = self._browser_model.empty_list_messages
        scroll_depth = len(self._browser_model.content_lists) - len(self._list_components)
        self._max_scroll_offset = max(0, scroll_depth + 2)
        self._max_hierarchy = max(0, scroll_depth)
        for component, content, message in izip_longest(components, contents, messages):
            if component != None:
                component.scrollable_list = content
                component.empty_list_message = message

        active_lists = len(contents)
        num_head = clamp(active_lists - 1, 0, self.NUM_COLUMNS - 1)
        head = components[:num_head]
        last = components[num_head:]

        def set_data_sources_with_separator(component, sources, separator):
            for source in sources:
                source.separator = separator

            component.set_data_sources(sources)
            component.set_enabled(True)

        for idx, component in enumerate(head):
            offset = idx * self.COLUMN_SIZE
            sources = self._data_sources[offset:offset + self.COLUMN_SIZE]
            set_data_sources_with_separator(component, sources, '|')

        if last:
            offset = num_head * self.COLUMN_SIZE
            scrollable_list = last[0].scrollable_list
            if scrollable_list and find_if(lambda item: item.content.is_folder, scrollable_list.items):
                sources = self._data_sources[offset:offset + self.COLUMN_SIZE]
                map(DisplayDataSource.clear, self._data_sources[offset + self.COLUMN_SIZE:])
            else:
                sources = self._data_sources[offset:]
            set_data_sources_with_separator(last[0], sources, '')
            for component in last[1:]:
                component.set_enabled(False)

        self.set_select_buttons(self._select_buttons)
        self.set_state_buttons(self._state_buttons)
        self.set_encoder_controls(self._encoder_controls)
        self._update_navigation_button_state()

    @listens('value')
    def _on_select_matrix_value(self, value, *_):
        pass

    @listens('value')
    def _on_state_matrix_value(self, value, *_):
        pass

    @listens('value')
    def _on_encoder_matrix_value(self, value, *_):
        pass