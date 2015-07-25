#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/BrowserComponent.py
from __future__ import with_statement
from functools import partial
from itertools import izip, chain, imap
import string
import re
import consts
import Live
FilterType = Live.Browser.FilterType
DeviceType = Live.Device.DeviceType
from _Framework.Control import ButtonControl
from _Framework import Task
from _Framework.CompoundComponent import CompoundComponent
from _Framework.Util import first, find_if, index_if, clamp, in_range, BooleanContext, nop, const, lazy_attribute, memoize
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot, subject_slot_group, SlotManager, Subject
from ScrollableList import ActionListItem, ActionList, ListComponent, DefaultItemFormatter

class VirtualBrowserItem(object):
    """
    Quacks like a Live.Browser.BrowserItem
    """
    source = ''
    is_device = False
    is_loadable = False

    def __init__(self, name = '', children_query = nop, is_folder = False):
        self.name = name
        self.is_folder = is_folder
        self.children_query = children_query

    @lazy_attribute
    def children(self):
        return self.children_query()

    @property
    def is_selected(self):
        return find_if(lambda x: x.is_selected, self.children)

    def __str__(self):
        return self.name


class BrowserListItem(ActionListItem):
    """
    List item representing a browser element
    """

    def __str__(self):
        import os
        return os.path.splitext(self.content.name)[0] if self.content else ''

    def action(self):
        if self.container and self.container.browser:
            self.container.browser.load_item(self.content)

    @property
    def supports_action(self):
        return self.container and self.container.browser and self.content != None and self.content.is_loadable


class BrowserList(ActionList):
    """
    Component for representing lists of browser items
    """
    browser = None
    item_type = BrowserListItem

    def __init__(self, browser = None, *a, **k):
        super(BrowserList, self).__init__(*a, **k)
        self.browser = browser


class BrowserModel(Subject, SlotManager):
    """
    A browser model provides the data to a browser component as a
    sequence of BrowserLists.
    
    The BrowserComponent will use equality to discard equivalent
    models and prevent unnecessary updating, override it when
    neccesary.
    """
    __subject_events__ = ('content_lists', 'selection_updated')
    empty_list_messages = []

    def __init__(self, browser = None, *a, **k):
        super(BrowserModel, self).__init__(*a, **k)
        self._browser = browser

    def can_be_exchanged(self, model):
        return isinstance(model, BrowserModel)

    def exchange_model(self, model):
        """
        Tries to replace itself with the settings of a given
        model. Returns true if it succeeds or false if the current
        model can not represent the same set of values.
        """
        if self.can_be_exchanged(model):
            self._browser = model._browser
            return True
        return False

    @property
    def content_lists(self):
        """
        Returns a set of ActionLists that hold the hierarchy of
        content for the browser.
        """
        return NotImplementedError

    def update_content(self):
        """
        Called when the browser contents have changed.
        """
        raise NotImplementedError

    def update_selection(self):
        """
        Called when the browser selection might have changed.
        """
        raise NotImplementedError

    @property
    def browser(self):
        return self._browser

    def make_content_list(self):
        return BrowserList(browser=self._browser)


class EmptyBrowserModel(BrowserModel):
    """
    A browser model that never returns anything, to be used for
    hotswap targets that do not make sense in Push.
    """
    empty_list_messages = ['Nothing to browse']

    @property
    def content_lists(self):
        return tuple()

    def update_content(self):
        self.notify_content_lists()

    def update_selection(self):
        pass

    def can_be_exchanged(self, model):
        return isinstance(model, EmptyBrowserModel) and super(EmptyBrowserModel, self).can_be_exchanged(model)


class FullBrowserModel(BrowserModel):
    """
    A browser model that provides an abstract hierarchical query model
    for simpler implementation.  Note that this can result in endless
    nesting, which the BrowserComponent does not support so far.
    It always provides at least two columns.
    """
    empty_list_messages = ['<no tags>',
     '<no devices>',
     '<no presets>',
     '<no presets>']

    def __init__(self, *a, **k):
        super(FullBrowserModel, self).__init__(*a, **k)
        self._contents = []
        self._num_contents = 0
        self._push_content_list()
        self._inside_item_activated_notification = BooleanContext()

    def get_root_children(self):
        """
        Query for the initial items.
        """
        return self.browser.tags

    def get_children(self, item, level):
        """
        Query for children of node.
        """
        return item.children

    @property
    def content_lists(self):
        return map(first, self._contents[:self._num_contents])

    def can_be_exchanged(self, model):
        return isinstance(model, FullBrowserModel) and super(FullBrowserModel, self).can_be_exchanged(model)

    def update_content(self):
        root, _ = self._contents[0]
        root.assign_items(self.get_root_children())
        self.update_selection()

    def update_selection(self):
        last_seleced_list_index = None
        if self._browser.hotswap_target != None:
            list_index = 0
            while list_index < self._num_contents:
                content_list, _ = self._contents[list_index]
                items = content_list.items
                index = index_if(lambda x: x.content.is_selected, items)
                if in_range(index, 0, len(items)):
                    content_list.select_item_index_with_offset(index, 2)
                    last_seleced_list_index = list_index
                list_index += 1

        if last_seleced_list_index != None:
            self.notify_selection_updated(last_seleced_list_index)

    def _push_content_list(self):
        if self._num_contents < len(self._contents):
            self._num_contents += 1
            content = self._contents[self._num_contents - 1]
        else:
            raise self._num_contents == len(self._contents) or AssertionError
            content = self.make_content_list()
            level = len(self._contents)
            slot = self.register_slot(content, partial(self._on_item_activated, level), 'item_activated')
            self._contents.append((content, slot))
            self._num_contents = len(self._contents)
        return content

    def _pop_content_list(self):
        raise self._num_contents > 1 or AssertionError
        self._num_contents -= 1

    def _fit_content_lists(self, requested_lists):
        """
        Ensures that there are exactly 'request_lists' number of
        content lists. Returns whether a change was needed or not.
        """
        raise requested_lists > 0 or AssertionError
        if requested_lists != self._num_contents:
            while requested_lists < self._num_contents:
                self._pop_content_list()

            while requested_lists > self._num_contents:
                self._push_content_list()

    def _finalize_content_lists_change(self):
        """
        After a series of push/pop/fit operations, this makes sure
        that we only have as many content lists referenced as
        necessary.
        """
        while self._num_contents < len(self._contents):
            _, slot = self._contents.pop()
            self.disconnect_disconnectable(slot)

        raise self._num_contents == len(self._contents) or AssertionError

    def _on_item_activated(self, level):
        old_num_contents = self._num_contents
        with self._inside_item_activated_notification():
            contents, _ = self._contents[level]
            selected = contents.selected_item
            if selected != None:
                is_folder = selected.content.is_folder
                children = self.get_children(selected.content, level) if selected != None else []
                (children or is_folder or level < 1) and self._fit_content_lists(level + 2)
                child_contents, _ = self._contents[level + 1]
                child_contents.assign_items(children)
            else:
                self._fit_content_lists(level + 1)
        if not self._inside_item_activated_notification:
            self._finalize_content_lists_change()
            if old_num_contents != self._num_contents:
                self.notify_content_lists()


class BrowserQuery(object):
    """
    Base class for browser queries. Is capable of creating a subfolder for wrapping
    all results of the query.
    """

    def __init__(self, subfolder = None, *a, **k):
        self.subfolder = subfolder

    def __call__(self, browser):
        if self.subfolder:
            return [VirtualBrowserItem(name=self.subfolder, children_query=partial(self.query, browser), is_folder=True)]
        else:
            return self.query(browser)

    def query(self, browser):
        raise NotImplementedError


class PathBrowserQuery(BrowserQuery):
    """
    Includes the element for the given path.
    """

    def __init__(self, path = tuple(), *a, **k):
        super(PathBrowserQuery, self).__init__(*a, **k)
        raise path or AssertionError
        self.path = path

    def query(self, browser):
        return self._find_item(self.path, browser.tags, browser) or []

    def _find_item(self, path, items = None, browser = None):
        name = path[0]
        elem = find_if(lambda x: x.name == name, items)
        if elem:
            return [elem] if len(path) == 1 else self._find_item(path[1:], elem.children)


class TagBrowserQuery(BrowserQuery):
    """
    Query that merges the contents of the specified subtrees of
    the browser.  It will first merge the contents of all the paths
    specified in the 'include' list. A path is either the name of a
    tag or a list with the name of the tag/folders that describe the
    path. Then it drops the items that are in the 'exclude' list.
    """

    def __init__(self, include = tuple(), exclude = tuple(), *a, **k):
        super(TagBrowserQuery, self).__init__(*a, **k)
        self.include = include
        self.exclude = exclude

    def query(self, browser):
        return filter(lambda item: item.name not in self.exclude, sum(map(partial(self._extract_path, browser=browser), self.include), tuple()))

    def _extract_path(self, path, items = None, browser = None):
        if isinstance(path, (str, unicode)):
            path = [path]
        if items is None:
            items = browser.tags
        if path:
            name = path[0]
            elem = find_if(lambda x: x.name == name, items)
            if elem:
                items = self._extract_path(path[1:], elem.children)
        return tuple(items)


class SourceBrowserQuery(TagBrowserQuery):
    """
    Like TagBrowserQuery, but adds a top-level source selection.
    """

    def __init__(self, *a, **k):
        super(SourceBrowserQuery, self).__init__(*a, **k)

    def query(self, browser):
        root = super(SourceBrowserQuery, self).query(browser)
        groups = dict()
        for item in root:
            groups.setdefault(item.source, []).append(item)

        return map(lambda (k, g): VirtualBrowserItem(name=k if k is not None else '', children_query=const(g)), sorted(groups.items(), key=first))


class PlacesBrowserQuery(BrowserQuery):
    """
    Query that fetches all places of the browser
    """

    def __init__(self, *a, **k):
        super(PlacesBrowserQuery, self).__init__(*a, **k)

    def query(self, browser):
        return tuple(browser.packs) + tuple(browser.places)


class QueryingBrowserModel(FullBrowserModel):
    """
    Browser model that takes query objects to build up the model hierarchy
    """
    empty_list_messages = ['<no devices>',
     '<no presets>',
     '<no presets>',
     '<no presets>']

    def __init__(self, queries = [], *a, **k):
        super(QueryingBrowserModel, self).__init__(*a, **k)
        self.queries = queries

    def get_root_children(self):
        browser = self.browser
        return chain(*imap(lambda q: q(browser), self.queries))

    def can_be_exchanged(self, model):
        return isinstance(model, QueryingBrowserModel) and super(QueryingBrowserModel, self).can_be_exchanged(model)

    def exchange_model(self, model):
        if super(QueryingBrowserModel, self).exchange_model(model):
            self.queries = model.queries
            return True


PLACES_LABEL = 'Places'

def make_midi_effect_browser_model(browser):
    midi_effects = TagBrowserQuery(include=['MIDI Effects'])
    max = TagBrowserQuery(include=[['Max for Live', 'Max MIDI Effect']], subfolder='Max for Live')
    places = PlacesBrowserQuery(subfolder=PLACES_LABEL)
    return QueryingBrowserModel(browser=browser, queries=[midi_effects, max, places])


def make_audio_effect_browser_model(browser):
    audio_effects = TagBrowserQuery(include=['Audio Effects'])
    max = TagBrowserQuery(include=[['Max for Live', 'Max Audio Effect']], subfolder='Max for Live')
    places = PlacesBrowserQuery(subfolder=PLACES_LABEL)
    return QueryingBrowserModel(browser=browser, queries=[audio_effects, max, places])


def make_instruments_browser_model(browser):
    instrument_rack = PathBrowserQuery(path=['Instruments', 'Instrument Rack'])
    drums = SourceBrowserQuery(include=['Drums'], exclude=['Drum Hits'], subfolder='Drum Rack')
    instruments = TagBrowserQuery(include=['Instruments'], exclude=['Drum Rack', 'Instrument Rack'])
    drum_hits = TagBrowserQuery(include=[['Drums', 'Drum Hits']], subfolder='Drum Hits')
    max = TagBrowserQuery(include=[['Max for Live', 'Max Instrument']], subfolder='Max for Live')
    places = PlacesBrowserQuery(subfolder=PLACES_LABEL)
    return QueryingBrowserModel(browser=browser, queries=[instrument_rack,
     drums,
     instruments,
     max,
     drum_hits,
     places])


def make_drum_pad_browser_model(browser):
    drums = TagBrowserQuery(include=[['Drums', 'Drum Hits']])
    samples = SourceBrowserQuery(include=['Samples'], subfolder='Samples')
    instruments = TagBrowserQuery(include=['Instruments'])
    max = TagBrowserQuery(include=[['Max for Live', 'Max Instrument']], subfolder='Max for Live')
    places = PlacesBrowserQuery(subfolder=PLACES_LABEL)
    return QueryingBrowserModel(browser=browser, queries=[drums,
     samples,
     instruments,
     max,
     places])


def make_fallback_browser_model(browser):
    return EmptyBrowserModel(browser=browser)


def filter_type_for_hotswap_target(target):
    """
    Returns the appropriate browser filter type for a given hotswap target.
    """
    if isinstance(target, Live.Device.Device):
        if target.type == DeviceType.instrument:
            return FilterType.instrument_hotswap
        elif target.type == DeviceType.audio_effect:
            return FilterType.audio_effect_hotswap
        elif target.type == DeviceType.midi_effect:
            return FilterType.midi_effect_hotswap
        else:
            FilterType.disabled
    elif isinstance(target, Live.DrumPad.DrumPad):
        return FilterType.drum_pad_hotswap
    elif isinstance(target, Live.Chain.Chain):
        return filter_type_for_hotswap_target(target.canonical_parent) if target else FilterType.disabled
    return FilterType.disabled


def make_browser_model(browser, filter_type = None):
    """
    Factory that returns an appropriate browser model depending on the
    browser filter type and hotswap target.
    """
    factories = {FilterType.instrument_hotswap: make_instruments_browser_model,
     FilterType.drum_pad_hotswap: make_drum_pad_browser_model,
     FilterType.audio_effect_hotswap: make_audio_effect_browser_model,
     FilterType.midi_effect_hotswap: make_midi_effect_browser_model}
    if filter_type == None:
        filter_type = filter_type_for_browser(browser)
    return factories.get(filter_type, make_fallback_browser_model)(browser)


def filter_type_for_browser(browser):
    filter_type = filter_type_for_hotswap_target(browser.hotswap_target)
    if filter_type == FilterType.disabled:
        filter_type = browser.filter_type
    return filter_type


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
    __subject_events__ = ('load_item',)
    NUM_COLUMNS = 4
    COLUMN_SIZE = 4
    enter_button = ButtonControl(**consts.SIDE_BUTTON_COLORS)
    exit_button = ButtonControl(**consts.SIDE_BUTTON_COLORS)
    shift_button = ButtonControl()

    def __init__(self, browser = None, *a, **k):
        super(BrowserComponent, self).__init__(*a, **k)
        self._browser = browser or self.application().browser
        self._browser_model = make_fallback_browser_model(self._browser)
        num_data_sources = self.NUM_COLUMNS * self.COLUMN_SIZE
        self._data_sources = map(DisplayDataSource, ('',) * num_data_sources)
        self._last_loaded_item = None
        self._default_item_formatter = DefaultItemFormatter()
        self._list_components = self.register_components(*[ ListComponent() for _ in xrange(self.NUM_COLUMNS) ])
        for i, component in enumerate(self._list_components):
            component.do_trigger_action = lambda item: self._do_load_item(item)
            component.last_action_item = lambda : self._last_loaded_item
            component.item_formatter = partial(self._item_formatter, i)

        self._select_buttons = []
        self._state_buttons = []
        self._encoder_controls = []
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

    def reset_load_memory(self):
        self._update_load_memory(None)

    def _do_load_item(self, item):
        self.do_load_item(item)
        self._update_load_memory(item)
        self._skip_next_preselection = True

        def reset_skip_next_preselection():
            self._skip_next_preselection = False

        self._tasks.add(Task.run(reset_skip_next_preselection))

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

        return item_name[:-1] if len(item_name) >= shortening_limit and item_name[-1] == consts.CHAR_ELLIPSIS else item_name

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

    @subject_slot('hotswap_target')
    def _on_hotswap_target_changed(self):
        if not self._skip_next_preselection:
            self._set_scroll_offset(0)
        self._update_browser_model()

    @subject_slot('filter_type')
    def _on_filter_type_changed(self):
        self._update_browser_model()

    @subject_slot('full_refresh')
    def _on_browser_full_refresh(self):
        self._browser_model_dirty = True

    def _update_browser_model(self):
        if self.is_enabled():
            self._do_update_browser_model()

    def _create_browser_model_of_type(self, filter_type):
        self._last_filter_type = filter_type
        new_model = make_browser_model(self._browser, filter_type)
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

    @subject_slot_group('item_action')
    def _on_list_item_action(self, item, _):
        self.notify_load_item(item.content)

    @subject_slot('selection_updated')
    def _on_selection_updated(self, index):
        more_content_available = len(self._browser_model.content_lists) > self.NUM_COLUMNS + self._scroll_offset
        required_scroll_offset = index - (self.NUM_COLUMNS - 1)
        if more_content_available and required_scroll_offset > self._scroll_offset:
            self._set_scroll_offset(self._scroll_offset + 1)
            self._browser_model.update_selection()

    @subject_slot('content_lists')
    def _on_content_lists_changed(self):
        components = self._list_components
        contents = self._browser_model.content_lists[self._scroll_offset:]
        messages = self._browser_model.empty_list_messages
        scroll_depth = len(self._browser_model.content_lists) - len(self._list_components)
        self._max_scroll_offset = max(0, scroll_depth + 2)
        self._max_hierarchy = max(0, scroll_depth)
        for component, content, message in map(None, components, contents, messages):
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

    @subject_slot('value')
    def _on_select_matrix_value(self, value, *_):
        pass

    @subject_slot('value')
    def _on_state_matrix_value(self, value, *_):
        pass

    @subject_slot('value')
    def _on_encoder_matrix_value(self, value, *_):
        pass