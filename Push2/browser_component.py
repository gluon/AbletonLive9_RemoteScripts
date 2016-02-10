#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/browser_component.py
from __future__ import absolute_import, print_function
from contextlib import contextmanager
from itertools import imap
from math import ceil
import Live
from ableton.v2.base import BooleanContext, depends, index_if, lazy_attribute, listenable_property, listens, liveobj_changed, liveobj_valid, nop, task
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.control import control_list, ButtonControl, StepEncoderControl, ToggleButtonControl
from pushbase.browser_util import filter_type_for_hotswap_target, get_selection_for_new_device
from pushbase.message_box_component import Messenger
from .colors import translate_color_index
from .browser_list import BrowserList
from .browser_item import BrowserItem, ProxyBrowserItem

class WrappedLoadableBrowserItem(BrowserItem):

    def __init__(self, *a, **k):
        super(WrappedLoadableBrowserItem, self).__init__(*a, **k)
        self._browser = Live.Application.get_application().browser

    @property
    def is_selected(self):
        if self._contained_item is None:
            return self._is_selected
        else:
            relation = self._browser.relation_to_hotswap_target(self._contained_item)
            return relation == Live.Browser.Relation.equal


class FolderBrowserItem(BrowserItem):

    def __init__(self, wrapped_loadable = None, *a, **k):
        raise wrapped_loadable is not None or AssertionError
        super(FolderBrowserItem, self).__init__(*a, **k)
        self._wrapped_loadable = wrapped_loadable

    @property
    def is_selected(self):
        if self._contained_item is None:
            return self._is_selected
        return self._contained_item.is_selected

    @lazy_attribute
    def children(self):
        return [self._wrapped_loadable] + list(self.contained_item.children)


class PluginPresetBrowserItem(BrowserItem):

    def __init__(self, preset_name = None, preset_index = None, vst_device = None, *a, **k):
        raise preset_name is not None or AssertionError
        raise preset_index is not None or AssertionError
        raise vst_device is not None or AssertionError
        super(PluginPresetBrowserItem, self).__init__(name=(preset_name if preset_name else '<Empty Slot %i>' % (preset_index + 1)), is_loadable=True, *a, **k)
        self.preset_index = preset_index
        self._vst_device = vst_device

    @property
    def is_selected(self):
        return self._vst_device.selected_preset_index == self.preset_index

    @property
    def uri(self):
        return 'pluginpreset%i' % self.preset_index


class PluginBrowserItem(BrowserItem):

    def __init__(self, vst_device = None, *a, **k):
        super(PluginBrowserItem, self).__init__(is_loadable=False, is_selected=True, *a, **k)
        raise vst_device is not None or AssertionError
        self._vst_device = vst_device

    @property
    def children(self):
        return [ PluginPresetBrowserItem(preset_name=preset, preset_index=i, vst_device=self._vst_device) for i, preset in enumerate(self._vst_device.presets) ]


class CannotFocusListError(Exception):
    pass


class BrowserComponent(Component, Messenger):
    __events__ = ('loaded', 'close')
    NUM_ITEMS_PER_COLUMN = 6
    NUM_VISIBLE_BROWSER_LISTS = 7
    NUM_COLUMNS_IN_EXPANDED_LIST = 3
    EXPAND_LIST_TIME = 1.5
    REVEAL_PREVIEW_LIST_TIME = 0.2
    navigation_colors = dict(color='Browser.Navigation', disabled_color='Browser.NavigationDisabled')
    up_button = ButtonControl(repeat=True)
    down_button = ButtonControl(repeat=True)
    right_button = ButtonControl(repeat=True, **navigation_colors)
    left_button = ButtonControl(repeat=True, **navigation_colors)
    back_button = ButtonControl(**navigation_colors)
    open_button = ButtonControl(**navigation_colors)
    load_button = ButtonControl(**navigation_colors)
    close_button = ButtonControl()
    prehear_button = ToggleButtonControl(toggled_color='Browser.Option', untoggled_color='Browser.OptionDisabled')
    scroll_encoders = control_list(StepEncoderControl, num_steps=10, control_count=NUM_VISIBLE_BROWSER_LISTS)
    scroll_focused_encoder = StepEncoderControl(num_steps=10)
    scrolling = listenable_property.managed(False)
    horizontal_navigation = listenable_property.managed(False)
    list_offset = listenable_property.managed(0)
    can_enter = listenable_property.managed(False)
    can_exit = listenable_property.managed(False)
    context_color_index = listenable_property.managed(-1)
    context_text = listenable_property.managed('')
    load_text = listenable_property.managed('')

    @depends(commit_model_changes=None, selection=None)
    def __init__(self, preferences = dict(), commit_model_changes = None, selection = None, main_modes_ref = None, *a, **k):
        raise commit_model_changes is not None or AssertionError
        super(BrowserComponent, self).__init__(*a, **k)
        self._lists = []
        self._browser = Live.Application.get_application().browser
        self._current_hotswap_target = self._browser.hotswap_target
        self._updating_root_items = BooleanContext()
        self._focused_list_index = 0
        self._commit_model_changes = commit_model_changes
        self._preferences = preferences
        self._expanded = False
        self._unexpand_with_scroll_encoder = False
        self._delay_preview_list = BooleanContext()
        self._selection = selection
        self._load_next = False
        self._main_modes_ref = main_modes_ref if main_modes_ref is not None else nop
        self._content_filter_type = None
        self._content_hotswap_target = None
        self._preview_list_task = self._tasks.add(task.sequence(task.wait(self.REVEAL_PREVIEW_LIST_TIME), task.run(self._replace_preview_list_by_task))).kill()
        self._update_root_items()
        self._update_navigation_buttons()
        self._update_load_text()
        self._update_context()
        self.prehear_button.is_toggled = preferences.setdefault('browser_prehear', True)
        self._on_selected_track_color_index_changed.subject = self.song.view
        self._on_selected_track_name_changed.subject = self.song.view
        self._on_detail_clip_name_changed.subject = self.song.view
        self._on_hotswap_target_changed.subject = self._browser
        self.register_slot(self, self.notify_focused_item, 'focused_list_index')

        def auto_unexpand():
            self.expanded = False
            self._update_list_offset()

        self._unexpand_task = self._tasks.add(task.sequence(task.wait(self.EXPAND_LIST_TIME), task.run(auto_unexpand))).kill()

    @up_button.pressed
    def up_button(self, button):
        with self._delay_preview_list():
            self.focused_list.select_index_with_offset(-1)
        self._update_auto_expand()
        self._update_scrolling()
        self._update_horizontal_navigation()

    @up_button.released
    def up_button(self, button):
        self._finish_preview_list_task()
        self._update_scrolling()

    @down_button.pressed
    def down_button(self, button):
        with self._delay_preview_list():
            self.focused_list.select_index_with_offset(1)
        self._update_auto_expand()
        self._update_scrolling()
        self._update_horizontal_navigation()

    @down_button.released
    def down_button(self, button):
        self._finish_preview_list_task()
        self._update_scrolling()

    @right_button.pressed
    def right_button(self, button):
        if self._expanded and self._can_auto_expand() and self._focused_list_index > 0:
            self.focused_list.select_index_with_offset(self.NUM_ITEMS_PER_COLUMN)
            self._update_scrolling()
            self.horizontal_navigation = True
        elif not self._enter_selected_item():
            self._update_auto_expand()

    @right_button.released
    def right_button(self, button):
        self._update_scrolling()

    @left_button.pressed
    def left_button(self, button):
        if self._expanded and self._focused_list_index > 0 and self.focused_list.selected_index >= self.NUM_ITEMS_PER_COLUMN:
            self.focused_list.select_index_with_offset(-self.NUM_ITEMS_PER_COLUMN)
            self._update_scrolling()
            self.horizontal_navigation = True
        else:
            self._exit_selected_item()

    @left_button.released
    def left_button(self, button):
        self._update_scrolling()

    @open_button.pressed
    def open_button(self, button):
        self._enter_selected_item()

    @back_button.pressed
    def back_button(self, button):
        self._exit_selected_item()

    @scroll_encoders.touched
    def scroll_encoders(self, encoder):
        list_index = self._get_list_index_for_encoder(encoder)
        if list_index is not None:
            try:
                if self._focus_list_with_index(list_index, crop=False):
                    self._unexpand_with_scroll_encoder = True
                    self._prehear_selected_item()
                if self.focused_list.selected_item.is_loadable and encoder.index == self.scroll_encoders.control_count - 1:
                    self._update_list_offset()
                self._on_encoder_touched()
            except CannotFocusListError:
                pass

    @scroll_encoders.released
    def scroll_encoders(self, encoders):
        self._on_encoder_released()

    @scroll_encoders.value
    def scroll_encoders(self, value, encoder):
        list_index = self._get_list_index_for_encoder(encoder)
        if list_index is not None:
            try:
                if self._focus_list_with_index(list_index):
                    self._unexpand_with_scroll_encoder = True
                self._on_encoder_value(value)
            except CannotFocusListError:
                pass

    @scroll_focused_encoder.value
    def scroll_focused_encoder(self, value, encoder):
        self._on_encoder_value(value)

    @scroll_focused_encoder.touched
    def scroll_focused_encoder(self, encoder):
        self._on_encoder_touched()

    @scroll_focused_encoder.released
    def scroll_focused_encoder(self, encoder):
        self._on_encoder_released()

    def _on_encoder_value(self, value):
        with self._delay_preview_list():
            self.focused_list.select_index_with_offset(value)
        first_visible_list_focused = self.focused_list_index == self.list_offset
        if self.expanded and first_visible_list_focused:
            self.expanded = False
            self._unexpand_with_scroll_encoder = True
        elif not first_visible_list_focused and not self.expanded and self._can_auto_expand():
            self._update_auto_expand()
            self._unexpand_with_scroll_encoder = True
        self._update_scrolling()
        self._update_horizontal_navigation()

    def _on_encoder_touched(self):
        self._unexpand_task.kill()
        self._update_scrolling()
        self._update_horizontal_navigation()

    def _on_encoder_released(self):
        any_encoder_touched = any(imap(lambda e: e.is_touched, self.scroll_encoders)) or self.scroll_focused_encoder.is_touched
        if not any_encoder_touched and self._unexpand_with_scroll_encoder:
            self._unexpand_task.restart()
        self._update_scrolling()

    def _get_list_index_for_encoder(self, encoder):
        if self.expanded:
            if encoder.index == 0:
                return self.list_offset
            return self.list_offset + 1
        index = self.list_offset + encoder.index
        if self.focused_list_index + 1 == index and self.focused_list.selected_item.is_loadable:
            index = self.focused_list_index
        if 0 <= index < len(self._lists):
            return index
        else:
            return None

    @load_button.pressed
    def load_button(self, button):
        self._load_selected_item()

    @prehear_button.toggled
    def prehear_button(self, toggled, button):
        if toggled:
            self._prehear_selected_item()
        else:
            self._browser.stop_preview()
        self._preferences['browser_prehear'] = toggled
        self.notify_prehear_enabled()

    @close_button.pressed
    def close_button(self, button):
        self.notify_close()

    @listenable_property
    def lists(self):
        return self._lists

    @listenable_property
    def focused_list_index(self):
        return self._focused_list_index

    @listenable_property
    def prehear_enabled(self):
        return self.prehear_button.is_toggled

    @property
    def focused_list(self):
        return self._lists[self._focused_list_index]

    @listenable_property
    def focused_item(self):
        return self.focused_list.selected_item

    @listenable_property
    def expanded(self):
        return self._expanded

    def disconnect(self):
        super(BrowserComponent, self).disconnect()
        self._lists = []
        self._commit_model_changes = None

    @expanded.setter
    def expanded(self, expanded):
        if self._expanded != expanded:
            self._expanded = expanded
            self._unexpand_with_scroll_encoder = False
            self._update_navigation_buttons()
            if len(self._lists) > self._focused_list_index + 1:
                self._lists[self._focused_list_index + 1].limit = self.num_preview_items
            self.notify_expanded()

    @listens('selected_track.color_index')
    def _on_selected_track_color_index_changed(self):
        if self.is_enabled():
            self._update_context()
            self._update_navigation_buttons()

    @listens('selected_track.name')
    def _on_selected_track_name_changed(self):
        if self.is_enabled():
            self._update_context()

    @listens('detail_clip.name')
    def _on_detail_clip_name_changed(self):
        if self.is_enabled():
            self._update_context()

    @listens('hotswap_target')
    def _on_hotswap_target_changed(self):
        if self.is_enabled():
            if not self._switched_to_empty_pad():
                self._update_root_items()
                self._update_context()
                self._update_list_offset()
        self._current_hotswap_target = self._browser.hotswap_target

    @property
    def browse_for_audio_clip(self):
        main_modes = self._main_modes_ref()
        if main_modes is None:
            return False
        has_midi_support = self.song.view.selected_track.has_midi_input
        return not has_midi_support and 'clip' in main_modes.active_modes

    def _switched_to_empty_pad(self):
        hotswap_target = self._browser.hotswap_target
        is_browsing_drumpad = isinstance(hotswap_target, Live.DrumPad.DrumPad)
        was_browsing_pad = isinstance(self._current_hotswap_target, Live.DrumPad.DrumPad)
        return is_browsing_drumpad and was_browsing_pad and len(hotswap_target.chains) == 0

    def _focus_list_with_index(self, index, crop = True):
        """
        Focus the list with the given index.
        Raises CannotFocusListError if the operation fails.
        Returns True if a new list was focused and False if it was already focused.
        """
        if self._focused_list_index != index:
            if self._finish_preview_list_task():
                raise index >= len(self._lists) and CannotFocusListError()
        if not 0 <= index < len(self._lists):
            raise AssertionError
            self._on_focused_selection_changed.subject = None
            if self._focused_list_index > index and crop:
                for l in self._lists[self._focused_list_index:]:
                    l.selected_index = -1

            self._focused_list_index = index
            self.focused_list.limit = -1
            if self.focused_list.selected_index == -1:
                self.focused_list.selected_index = 0
            self.notify_focused_list_index()
            self._on_focused_selection_changed.subject = self.focused_list
            if crop:
                self._crop_browser_lists(self._focused_list_index + 2)
            if self._focused_list_index == len(self._lists) - 1:
                self._replace_preview_list()
            self._reset_load_next()
            self._update_navigation_buttons()
            return True
        return False

    @listens('selected_index')
    def _on_focused_selection_changed(self):
        if self._delay_preview_list and not self.focused_item.is_loadable:
            self._preview_list_task.restart()
        else:
            self._replace_preview_list()
        self._update_navigation_buttons()
        self._prehear_selected_item()
        self._reset_load_next()
        self.notify_focused_item()

    def _get_actual_item(self, item):
        contained_item = getattr(item, 'contained_item', None)
        if contained_item is not None:
            return contained_item
        return item

    def _load_selected_item(self):
        focused_list = self.focused_list
        if self._load_next:
            focused_list.selected_index += 1
        self._load_next = focused_list.selected_index < len(focused_list.items) - 1 and liveobj_valid(self._browser.hotswap_target)
        self._update_load_text()
        item = self._get_actual_item(focused_list.selected_item)
        notification_ref = self.show_notification(self._make_notification_text(item))
        self._commit_model_changes()
        self._load_item(item)
        self.notify_loaded()
        notification = notification_ref()
        if notification is not None:
            notification.reschedule_after_slow_operation()

    def _make_notification_text(self, browser_item):
        return 'Loading %s' % browser_item.name

    def _load_item(self, item):
        if liveobj_valid(self._browser.hotswap_target):
            if isinstance(item, PluginPresetBrowserItem):
                self._browser.hotswap_target.selected_preset_index = item.preset_index
            else:
                self._browser.load_item(item)
                self._content_hotswap_target = self._browser.hotswap_target
        else:
            with self._insert_right_of_selected():
                self._browser.load_item(item)

    def _reset_load_next(self):
        self._load_next = False
        self._update_load_text()

    @contextmanager
    def _insert_right_of_selected(self):
        DeviceInsertMode = Live.Track.DeviceInsertMode
        device_to_select = get_selection_for_new_device(self._selection)
        if device_to_select:
            self._selection.selected_object = device_to_select
        selected_track_view = self.song.view.selected_track.view
        selected_track_view.device_insert_mode = DeviceInsertMode.selected_right
        yield
        selected_track_view.device_insert_mode = DeviceInsertMode.default

    def _prehear_selected_item(self):
        if self.prehear_button.is_toggled and not self._updating_root_items:
            self._browser.stop_preview()
            item = self._get_actual_item(self.focused_list.selected_item)
            if item and item.is_loadable and isinstance(item, Live.Browser.BrowserItem):
                self._browser.preview_item(item)

    def _stop_prehear(self):
        if self.prehear_button.is_toggled and not self._updating_root_items:
            self._browser.stop_preview()

    def _update_load_text(self):
        self.load_text = 'Load Next' if self._load_next else 'Load'

    def _update_navigation_buttons(self):
        focused_list = self.focused_list
        self.up_button.enabled = focused_list.selected_index > 0
        self.down_button.enabled = focused_list.selected_index < len(focused_list.items) - 1
        selected_item_loadable = self.focused_list.selected_item.is_loadable
        assume_can_enter = self._preview_list_task.is_running and not selected_item_loadable
        can_exit = self._focused_list_index > 0
        can_enter = self._focused_list_index < len(self._lists) - 1 or assume_can_enter
        self.back_button.enabled = can_exit
        self.open_button.enabled = can_enter
        self.load_button.enabled = selected_item_loadable
        context_button_color = translate_color_index(self.context_color_index) if self.context_color_index > -1 else 'Browser.Navigation'
        self.load_button.color = context_button_color
        self.close_button.color = context_button_color
        if not self._expanded:
            self.left_button.enabled = self.back_button.enabled
            self.right_button.enabled = can_enter or self._can_auto_expand()
        else:
            num_columns = int(ceil(float(len(self.focused_list.items)) / self.NUM_ITEMS_PER_COLUMN))
            last_column_start_index = (num_columns - 1) * self.NUM_ITEMS_PER_COLUMN
            self.left_button.enabled = self._focused_list_index > 0
            self.right_button.enabled = can_enter or self.focused_list.selected_index < last_column_start_index
        self.can_enter = can_enter
        self.can_exit = can_exit

    def _update_scrolling(self):
        self.scrolling = self.up_button.is_pressed or self.down_button.is_pressed or self.scroll_focused_encoder.is_touched or any(imap(lambda e: e.is_touched, self.scroll_encoders)) or self.right_button.is_pressed and self._expanded or self.left_button.is_pressed and self._expanded

    def _update_horizontal_navigation(self):
        self.horizontal_navigation = self.right_button.is_pressed or self.left_button.is_pressed

    def _update_context(self):
        selected_track = self.song.view.selected_track
        clip = self.song.view.detail_clip
        if self.browse_for_audio_clip and clip:
            self.context_text = clip.name
        elif liveobj_valid(self._browser.hotswap_target):
            self.context_text = self._browser.hotswap_target.name
        else:
            self.context_text = selected_track.name
        selected_track_color_index = selected_track.color_index
        self.context_color_index = selected_track_color_index if selected_track_color_index is not None else -1

    def _enter_selected_item(self):
        item_entered = False
        self._finish_preview_list_task()
        new_index = self._focused_list_index + 1
        if 0 <= new_index < len(self._lists):
            self._focus_list_with_index(new_index)
            self._unexpand_task.kill()
            self._update_list_offset()
            self._update_auto_expand()
            self._prehear_selected_item()
            item_entered = True
        return item_entered

    def _exit_selected_item(self):
        item_exited = False
        try:
            self._focus_list_with_index(self._focused_list_index - 1)
            self._update_list_offset()
            self._update_auto_expand()
            self._stop_prehear()
            item_exited = True
        except CannotFocusListError:
            pass

        return item_exited

    def _can_auto_expand(self):
        return len(self.focused_list.items) > self.NUM_ITEMS_PER_COLUMN * 2 and self.focused_list.selected_item.is_loadable and getattr(self.focused_list.selected_item, 'contained_item', None) == None

    def _update_auto_expand(self):
        self.expanded = self._can_auto_expand()
        self._update_list_offset()

    def _update_list_offset(self):
        if self.expanded:
            self.list_offset = max(0, self.focused_list_index - 1)
        else:
            offset = len(self._lists)
            if self.focused_list.selected_item.is_loadable:
                offset += 1
            self.list_offset = max(0, offset - self.NUM_VISIBLE_BROWSER_LISTS)

    def _replace_preview_list_by_task(self):
        self._replace_preview_list()
        self._update_navigation_buttons()

    def _finish_preview_list_task(self):
        if self._preview_list_task.is_running:
            self._replace_preview_list_by_task()
            return True
        return False

    def _replace_preview_list(self):
        self._preview_list_task.kill()
        self._crop_browser_lists(self._focused_list_index + 1)
        selected_item = self.focused_list.selected_item
        children_iterator = selected_item.iter_children
        if len(children_iterator) > 0:
            enable_wrapping = getattr(selected_item, 'enable_wrapping', True) and self.focused_list.items_wrapped
            self._append_browser_list(children_iterator=children_iterator, limit=self.num_preview_items, enable_wrapping=enable_wrapping)

    def _append_browser_list(self, children_iterator, limit = -1, enable_wrapping = True):
        l = BrowserList(item_iterator=children_iterator, item_wrapper=self._wrap_item if enable_wrapping else nop, limit=limit)
        l.items_wrapped = enable_wrapping
        self._lists.append(l)
        self.register_disconnectable(l)
        self.notify_lists()

    def _crop_browser_lists(self, length):
        num_items_to_crop = len(self._lists) - length
        for _ in xrange(num_items_to_crop):
            l = self._lists.pop()
            self.unregister_disconnectable(l)

        if num_items_to_crop > 0:
            self.notify_lists()

    def _make_root_browser_items(self):
        filter_type = self._browser.filter_type
        hotswap_target = self._browser.hotswap_target
        if liveobj_valid(hotswap_target):
            filter_type = filter_type_for_hotswap_target(hotswap_target, default=filter_type)
        return make_root_browser_items(self._browser, filter_type)

    def _content_cache_is_valid(self):
        return self._content_filter_type == self._browser.filter_type and not liveobj_changed(self._content_hotswap_target, self._browser.hotswap_target)

    def _invalidate_content_cache(self):
        self._content_hotswap_target = None
        self._content_filter_type = None

    def _update_content_cache(self):
        self._content_filter_type = self._browser.filter_type
        self._content_hotswap_target = self._browser.hotswap_target

    def _update_root_items(self):
        if not self._content_cache_is_valid():
            self._update_content_cache()
            with self._updating_root_items():
                self._on_focused_selection_changed.subject = None
                self._crop_browser_lists(0)
                self._append_browser_list(children_iterator=self._make_root_browser_items())
                self._focused_list_index = 0
                self.focused_list.selected_index = 0
                self._select_hotswap_target()
                self._on_focused_selection_changed.subject = self.focused_list
                self._on_focused_selection_changed()

    def _select_hotswap_target(self, list_index = 0):
        if list_index < len(self._lists):
            l = self._lists[list_index]
            l.access_all = True
            children = l.items
            i = index_if(lambda i: i.is_selected, children)
            if i < len(children):
                self._focused_list_index = list_index
                l.selected_index = i
                self._replace_preview_list()
                self._select_hotswap_target(list_index + 1)

    @property
    def num_preview_items(self):
        if self._expanded:
            return self.NUM_ITEMS_PER_COLUMN * self.NUM_COLUMNS_IN_EXPANDED_LIST
        return 6

    def update(self):
        super(BrowserComponent, self).update()
        self._invalidate_content_cache()
        if self.is_enabled():
            self._update_root_items()
            self._update_context()
            self._update_list_offset()
            self._update_navigation_buttons()
            self.expanded = False
            self._update_list_offset()
        else:
            self._stop_prehear()
            self.list_offset = 0

    def _wrap_item(self, item):
        if item.is_device:
            return self._wrap_device_item(item)
        if self._is_hotswap_target_plugin(item):
            return self._wrap_hotswapped_plugin_item(item)
        return item

    def _wrap_device_item(self, item):
        """
        Create virtual folder around items that can be loaded AND have children, to avoid
        having two actions on an item (open and load).
        """
        wrapped_loadable = WrappedLoadableBrowserItem(name=item.name, is_loadable=True, contained_item=item)
        return FolderBrowserItem(name=item.name, contained_item=item, wrapped_loadable=wrapped_loadable)

    def _is_hotswap_target_plugin(self, item):
        return isinstance(self._browser.hotswap_target, Live.PluginDevice.PluginDevice) and isinstance(item, Live.Browser.BrowserItem) and self._browser.relation_to_hotswap_target(item) == Live.Browser.Relation.equal

    def _wrap_hotswapped_plugin_item(self, item):
        return PluginBrowserItem(name=item.name, vst_device=self._browser.hotswap_target)


class TrackBrowserItem(BrowserItem):
    filter_type = Live.Browser.FilterType.hotswap_off

    def create_track(self, song, index):
        raise NotImplementedError


class MidiTrackBrowserItem(TrackBrowserItem):
    filter_type = Live.Browser.FilterType.midi_track_devices

    def __init__(self, *a, **k):
        super(MidiTrackBrowserItem, self).__init__(name='MIDI track', *a, **k)

    def create_track(self, song, index):
        song.create_midi_track(index)


class AudioTrackBrowserItem(TrackBrowserItem):
    filter_type = Live.Browser.FilterType.audio_effect_hotswap

    def __init__(self, *a, **k):
        super(AudioTrackBrowserItem, self).__init__(name='Audio track', *a, **k)

    def create_track(self, song, index):
        song.create_audio_track(index)


class ReturnTrackBrowserItem(TrackBrowserItem):
    filter_type = Live.Browser.FilterType.audio_effect_hotswap

    def __init__(self, *a, **k):
        super(ReturnTrackBrowserItem, self).__init__(name='Return track', *a, **k)

    def create_track(self, song, index):
        song.create_return_track()


class DefaultTrackBrowserItem(BrowserItem):
    """
    Represents a loadable item, where the new track browser component checks whether the
    item is of this type, and skips loading the item.
    """

    def __init__(self, *a, **k):
        super(DefaultTrackBrowserItem, self).__init__(name='Default track', is_loadable=True, *a, **k)


class NewTrackBrowserComponent(BrowserComponent):

    def __init__(self, *a, **k):
        self._content = []
        self._track_type_items = [MidiTrackBrowserItem(children=self._content), AudioTrackBrowserItem(children=self._content), ReturnTrackBrowserItem(children=self._content)]
        super(NewTrackBrowserComponent, self).__init__(*a, **k)
        if self.is_enabled():
            self._update_filter_type()

    def _make_root_browser_items(self):
        self._update_root_content()
        return self._track_type_items

    def disconnect(self):
        super(NewTrackBrowserComponent, self).disconnect()
        self._content = []

    @property
    def browse_for_audio_clip(self):
        return False

    def _update_root_content(self):
        real_root_items = super(NewTrackBrowserComponent, self)._make_root_browser_items()
        self._content[:] = [DefaultTrackBrowserItem()] + real_root_items

    def _update_root_items(self):
        self._set_filter_type(self._track_type_items[0].filter_type)
        super(NewTrackBrowserComponent, self)._update_root_items()
        self._on_root_list_selection_changed.subject = self._lists[0]

    def _update_filter_type(self):
        self._set_filter_type(self._selected_track_item().filter_type)

    def _set_filter_type(self, filter_type):
        if self._browser.filter_type != filter_type:
            self._browser.filter_type = filter_type
            self._update_root_content()

    def _update_context(self):
        self.context_text = 'Close'

    def _load_item(self, item):
        self._selected_track_item().create_track(self.song, self._selected_track_index())
        if not isinstance(item, DefaultTrackBrowserItem):
            super(NewTrackBrowserComponent, self)._load_item(item)

    def _make_notification_text(self, browser_item):
        return '%s loaded in track %i' % (browser_item.name, self._selected_track_index() + 1)

    def _selected_track_index(self):
        song = self.song
        selected_track = self._selection.selected_track
        if selected_track in song.tracks:
            return list(song.tracks).index(selected_track) + 1
        return -1

    def _selected_track_item(self):
        return self._lists[0].selected_item

    @listens('selected_index')
    def _on_root_list_selection_changed(self):
        self._update_filter_type()
        self._replace_preview_list()


def wrap_item(item, icon, **k):
    return ProxyBrowserItem(proxied_object=item, icon=icon, **k)


def wrap_items(items, icon):
    for i, place in enumerate(items):
        items[i] = wrap_item(place, icon)

    return items


class UserFilesBrowserItem(BrowserItem):

    def __init__(self, browser, *a, **k):
        super(UserFilesBrowserItem, self).__init__(*a, **k)
        self._browser = browser

    @property
    def is_selected(self):
        return any(imap(lambda c: c.is_selected, self.children))

    @lazy_attribute
    def children(self):
        res = [wrap_item(self._browser.user_library, 'browser_userlibrary.svg')] + wrap_items(list(self._browser.user_folders), 'browser_folder.svg')
        self._browser = None
        return res


def make_root_browser_items(browser, filter_type):
    sounds = wrap_item(browser.sounds, 'browser_sounds.svg')
    drums = wrap_item(browser.drums, 'browser_drums.svg', enable_wrapping=False)
    instruments = wrap_item(browser.instruments, 'browser_instruments.svg')
    audio_effects = wrap_item(browser.audio_effects, 'browser_audioeffect.svg')
    midi_effects = wrap_item(browser.midi_effects, 'browser_midieffect.svg')
    packs = wrap_item(browser.packs, 'browser_packs.svg')
    legacy_libraries = wrap_items(list(browser.legacy_libraries), 'browser_8folder.svg')
    current_project = wrap_item(browser.current_project, 'browser_currentproject.svg')
    if filter_type == Live.Browser.FilterType.samples:
        categories = [packs] + legacy_libraries + [current_project]
    else:
        common_items = [wrap_item(browser.max_for_live, 'browser_max.svg'), wrap_item(browser.plugins, 'browser_plugins.svg'), packs] + legacy_libraries + [current_project]
        if filter_type == Live.Browser.FilterType.audio_effect_hotswap:
            categories = [audio_effects] + common_items
        elif filter_type == Live.Browser.FilterType.midi_effect_hotswap:
            categories = [midi_effects] + common_items
        elif filter_type == Live.Browser.FilterType.instrument_hotswap:
            categories = [sounds, drums, instruments] + common_items
        else:
            categories = [sounds,
             drums,
             instruments,
             audio_effects,
             midi_effects] + common_items
    user_files = UserFilesBrowserItem(browser, name='User Files', icon='browser_userfiles.svg')
    return [user_files] + categories