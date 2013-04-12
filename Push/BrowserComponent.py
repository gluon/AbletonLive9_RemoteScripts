#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/BrowserComponent.py
from __future__ import with_statement
from functools import partial
from itertools import izip
import Live
FilterType = Live.Browser.FilterType
DeviceType = Live.Device.DeviceType
from _Framework.CompoundComponent import CompoundComponent
from _Framework.Util import first, find_if, index_if, clamp, in_range, BooleanContext
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot, subject_slot_group, SlotManager, Subject
from ScrollableList import ActionListItem, ActionList, ListComponent

class VirtualBrowserItem(object):
    """
    Quacks like a Live.Browser.BrowserItem
    """
    source = ''
    is_device = False
    is_loadable = False

    def __init__(self, name = '', children = tuple(), is_folder = False):
        self.name = name
        self.children = children
        self.is_folder = is_folder

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
        return self.content.name if self.content else ''

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
    __subject_events__ = ('content_lists',)
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
    hotswap targets that do not make sense in the L9C.
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
        target = self._browser.hotswap_target
        if self._browser.hotswap_target != None:
            if isinstance(target, Live.DrumPad.DrumPad) and (not target.chains or not target.chains[0].devices):
                for content_list in self.content_lists:
                    content_list.select_item_index_with_offset(0, 0)

            else:
                list_index = 0
                while list_index < self._num_contents:
                    content_list, _ = self._contents[list_index]
                    items = content_list.items
                    index = index_if(lambda x: x.content.is_selected, items)
                    if in_range(index, 0, len(items)):
                        content_list.select_item_index_with_offset(index, 2)
                    list_index += 1

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
        result = self.query(browser)
        if self.subfolder and len(result) > 0:
            return [VirtualBrowserItem(name=self.subfolder, children=result, is_folder=True)]
        else:
            return result

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

        return map(lambda (k, g): VirtualBrowserItem(name=k, children=tuple(g)), sorted(groups.items(), key=first))


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
        root = []
        for query in self.queries:
            root += query(self.browser)

        return root

    def can_be_exchanged(self, model):
        return isinstance(model, QueryingBrowserModel) and super(QueryingBrowserModel, self).can_be_exchanged(model)

    def exchange_model(self, model):
        if super(QueryingBrowserModel, self).exchange_model(model):
            self.queries = model.queries
            return True


def make_midi_effect_browser_model(browser):
    query = TagBrowserQuery(include=['MIDI Effects'])
    return QueryingBrowserModel(browser=browser, queries=[query])


def make_audio_effect_browser_model(browser):
    query = TagBrowserQuery(include=['Audio Effects'])
    return QueryingBrowserModel(browser=browser, queries=[query])


def make_instruments_browser_model(browser):
    instrument_rack = PathBrowserQuery(path=['Instruments', 'Instrument Rack'])
    drums = SourceBrowserQuery(include=['Drums'], exclude=['Drum Hits'], subfolder='Drum Rack')
    instruments = TagBrowserQuery(include=['Instruments'], exclude=['Drum Rack', 'Instrument Rack'])
    drum_hits = TagBrowserQuery(include=[['Drums', 'Drum Hits']], subfolder='Drum Hits')
    return QueryingBrowserModel(browser=browser, queries=[instrument_rack,
     drums,
     instruments,
     drum_hits])

# JULIEN
def make_plugins_browser_model(browser):
    query = TagBrowserQuery(include=['Plug-ins'])
    return QueryingBrowserModel(browser=browser, queries=[query])


def make_drum_pad_browser_model(browser):
    drums = TagBrowserQuery(include=[['Drums', 'Drum Hits']])
    samples = SourceBrowserQuery(include=['Samples'], subfolder='Samples')
    instruments = TagBrowserQuery(include=['Instruments'])
    return QueryingBrowserModel(browser=browser, queries=[drums, samples, instruments])


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
        elif target.type == DeviceType.audio_effect:
            return FilterType.audio_effect_hotswap
        elif target.type == DeviceType.midi_effect:
            return FilterType.midi_effect_hotswap
        else:
            FilterType.disabled
    elif isinstance(target, Live.DrumPad.DrumPad):
        return FilterType.drum_pad_hotswap
    return FilterType.disabled


def make_browser_model(browser, filter_type = None):
    """
    Factory that returns an appropriate browser model depending on the
    browser filter type and hotswap target.
    """
    factories = {FilterType.instrument_hotswap: make_instruments_browser_model,
     FilterType.drum_pad_hotswap: make_drum_pad_browser_model,
     FilterType.audio_effect_hotswap: make_audio_effect_browser_model,
     FilterType.midi_effect_hotswap: make_midi_effect_browser_model,
     FilterType.plugins_hotswap: make_plugins_browser_model}
    if filter_type == None:
        filter_type = filter_type_for_browser(browser)
    return factories.get(filter_type, make_fallback_browser_model)(browser)


def filter_type_for_browser(browser):
    filter_type = filter_type_for_hotswap_target(browser.hotswap_target)
    if filter_type == FilterType.disabled:
        filter_type = browser.filter_type
    return filter_type


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

    def __init__(self, *a, **k):
        super(BrowserComponent, self).__init__(*a, **k)
        self._browser = self.application().browser
        self._browser_model = make_fallback_browser_model(self._browser)
        num_data_sources = self.NUM_COLUMNS * self.COLUMN_SIZE
        self._data_sources = map(DisplayDataSource, ('',) * num_data_sources)
        self._last_loaded_item = None
        self._list_components = self.register_components(*[ ListComponent() for _ in xrange(self.NUM_COLUMNS) ])
        for component in self._list_components:
            component.do_trigger_action = lambda item: self._do_load_item(item)
            component.last_action_item = lambda : self._last_loaded_item

        self._select_buttons = []
        self._state_buttons = []
        self._encoder_controls = []
        self._on_list_item_action.replace_subjects(self._list_components)
        self._on_hotswap_target_changed.subject = self._browser
        self._on_filter_type_changed.subject = self._browser
        self._on_browser_full_refresh.subject = self._browser
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
            button.reset()

        self._on_select_matrix_value.subject = buttons or None
        self._select_buttons = buttons
        buttons = buttons or (None, None, None, None, None, None, None, None)
        for component, button in izip(self._list_components, buttons[1::2]):
            self._set_button_if_enabled(component, 'action_button', button)

        for component, button in izip(self._list_components, buttons[::2]):
            self._set_button_if_enabled(component, 'select_prev_button', button)

    def set_state_buttons(self, buttons):
        for button in buttons or []:
            button.reset()

        self._on_state_matrix_value.subject = buttons or None
        self._state_buttons = buttons
        buttons = buttons or (None, None, None, None, None, None, None, None)
        for component, button in izip(self._list_components, buttons[::2]):
            self._set_button_if_enabled(component, 'select_next_button', button)

        for button in buttons[1::2]:
            if button and self.is_enabled():
                button.set_light('DefaultButton.Disabled')

    def _set_button_if_enabled(self, component, name, button):
        setter = getattr(component, 'set_' + name)
        if component.is_enabled(explicit=True):
            setter(button)
        else:
            setter(None)
            if button and self.is_enabled():
                button.set_light('DefaultButton.Disabled')

    def set_encoder_controls(self, encoder_controls):
        if encoder_controls:
            num_active_lists = len(self._browser_model.content_lists)
            index = 0
            for component in self._list_components[:num_active_lists - 1]:
                component.set_encoder_controls(encoder_controls[index:index + 2])
                index += 2

            self._list_components[num_active_lists - 1].set_encoder_controls(encoder_controls[index:])
        else:
            for component in self._list_components:
                component.set_encoder_controls([])

        self._encoder_controls = encoder_controls

    def update(self):
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

    def _update_load_memory(self, item):
        self._last_loaded_item = item
        for component in self._list_components:
            component.update()

    def do_load_item(self, item):
        item.action()
        self.notify_load_item(item.content)

    @subject_slot('hotswap_target')
    def _on_hotswap_target_changed(self):
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

    def _do_update_browser_model(self):
        filter_type = filter_type_for_browser(self._browser)
        if filter_type != self._last_filter_type:
            self._last_filter_type = filter_type
            new_model = make_browser_model(self._browser, filter_type)
            if self._browser_model and self._browser_model.can_be_exchanged(new_model) and new_model.can_be_exchanged(self._browser_model):
                self._browser_model.exchange_model(new_model)
                new_model.disconnect()
            else:
                self.disconnect_disconnectable(self._browser_model)
                self._browser_model = self.register_slot_manager(new_model)
                self._on_content_lists_changed.subject = self._browser_model
            for contents in self._browser_model.content_lists:
                contents.selected_item_index = 0

            self._browser_model.update_content()
        elif self._browser_model_dirty:
            self._browser_model.update_content()
        elif not self._skip_next_preselection:
            self._browser_model.update_selection()
        self._skip_next_preselection = False
        self._browser_model_dirty = False

    @subject_slot_group('item_action')
    def _on_list_item_action(self, item, list):
        self.notify_load_item(item.content)

    @subject_slot('content_lists')
    def _on_content_lists_changed(self):
        components = self._list_components
        contents = self._browser_model.content_lists
        messages = self._browser_model.empty_list_messages
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
            sources = self._data_sources[num_head * self.COLUMN_SIZE:]
            set_data_sources_with_separator(last[0], sources, '')
            for component in last[1:]:
                component.set_enabled(False)

        self.set_select_buttons(self._select_buttons)
        self.set_state_buttons(self._state_buttons)
        self.set_encoder_controls(self._encoder_controls)

    @subject_slot('value')
    def _on_select_matrix_value(self, value, *_):
        pass

    @subject_slot('value')
    def _on_state_matrix_value(self, value, *_):
        pass

    @subject_slot('value')
    def _on_encoder_matrix_value(self, value, *_):
        pass