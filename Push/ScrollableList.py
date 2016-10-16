#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/ScrollableList.py
from __future__ import with_statement
from functools import partial
from _Framework.Control import ButtonControl, EncoderControl, control_list
from _Framework.CompoundComponent import CompoundComponent
from _Framework.Util import forward_property, in_range, clamp, BooleanContext, index_if
from _Framework.SubjectSlot import subject_slot, Subject
from _Framework import Task, Defaults
from _Framework.ScrollComponent import ScrollComponent, Scrollable
import consts

class ScrollableListItem(object):
    """
    Wrapper of an item of a scrollable list.
    """

    def __init__(self, index = None, content = None, scrollable_list = None, *a, **k):
        super(ScrollableListItem, self).__init__(*a, **k)
        self._content = content
        self._index = index
        self._scrollable_list = scrollable_list

    def __str__(self):
        return unicode(self._content)

    @property
    def content(self):
        return self._content

    @property
    def index(self):
        return self._index

    @property
    def container(self):
        return self._scrollable_list

    @property
    def is_selected(self):
        return self._scrollable_list and self._scrollable_list.is_selected(self)

    def select(self):
        return self._scrollable_list and self._scrollable_list.select_item(self)


class ScrollableList(Subject, Scrollable):
    """
    Class for managing a visual subset of a list of items.
    
    The items will be wrapped in an item_type instance.
    """
    __subject_events__ = ('selected_item', 'item_activated', 'scroll')
    item_type = ScrollableListItem
    fixed_offset = None

    def __init__(self, num_visible_items = 1, item_type = None, *a, **k):
        super(ScrollableList, self).__init__(*a, **k)
        if item_type != None:
            self.item_type = item_type
        self._items = []
        self._num_visible_items = num_visible_items
        self._selected_item_index = -1
        self._last_activated_item_index = None
        self._offset = 0
        self._pager = Scrollable()
        self._pager.scroll_up = self.prev_page
        self._pager.scroll_down = self.next_page
        self._pager.can_scroll_up = self.can_scroll_up
        self._pager.can_scroll_down = self.can_scroll_down

    @property
    def pager(self):
        return self._pager

    def scroll_up(self):
        if self.can_scroll_up():
            self.select_item_index_with_border(self.selected_item_index - 1, 1)
            self.notify_scroll()

    def can_scroll_up(self):
        return self._selected_item_index > 0

    def scroll_down(self):
        if self.can_scroll_down():
            self.select_item_index_with_border(self.selected_item_index + 1, 1)
            self.notify_scroll()

    def can_scroll_down(self):
        return self._selected_item_index < len(self._items) - 1

    def _get_num_visible_items(self):
        return self._num_visible_items

    def _set_num_visible_items(self, num_items):
        raise num_items >= 0 or AssertionError
        self._num_visible_items = num_items
        self._normalize_offset(self._selected_item_index)

    num_visible_items = property(_get_num_visible_items, _set_num_visible_items)

    @property
    def visible_items(self):
        return self.items[self._offset:self._offset + self._num_visible_items]

    def select_item_index_with_offset(self, index, offset):
        """
        Selects an item index but moves the view such that there are,
        if possible, 'offset' number of elements visible before the
        selected one.  Does nothing if the item was already selected.
        """
        if not (index != self.selected_item_index and index >= 0 and index < len(self._items) and self.selected_item_index != -1):
            raise AssertionError
            self._offset = clamp(index - offset, 0, len(self._items))
            self._normalize_offset(index)
            self._do_set_selected_item_index(index)

    def select_item_index_with_border(self, index, border_size):
        """
        Selects an item with an index. Moves the view if the selection would exceed the
        border of the current view.
        """
        if self.fixed_offset is not None:
            self.select_item_index_with_offset(index, self.fixed_offset)
        elif index >= 0 and index < len(self._items):
            if not in_range(index, self._offset + border_size, self._offset + self._num_visible_items - border_size):
                offset = index - (self._num_visible_items - 2 * border_size) if self.selected_item_index < index else index - border_size
                self._offset = clamp(offset, 0, len(self._items))
            self._normalize_offset(index)
            self._do_set_selected_item_index(index)

    def next_page(self):
        if self.can_scroll_down():
            current_page = self.selected_item_index / self.num_visible_items
            last_page_index = len(self.items) - self.num_visible_items
            if self.selected_item_index < last_page_index:
                index = clamp((current_page + 1) * self.num_visible_items, 0, len(self.items) - self.num_visible_items)
            else:
                index = len(self.items) - 1
            self.select_item_index_with_offset(index, 0)

    def prev_page(self):
        if self.can_scroll_up():
            current_page = self.selected_item_index / self.num_visible_items
            last_page_index = len(self.items) - self.num_visible_items
            if self.selected_item_index <= last_page_index:
                index = clamp((current_page - 1) * self.num_visible_items, 0, len(self.items) - self.num_visible_items)
            else:
                index = max(len(self.items) - self.num_visible_items, 0)
            self.select_item_index_with_offset(index, 0)

    def _set_selected_item_index(self, index):
        if not (index >= 0 and index < len(self._items) and self.selected_item_index != -1):
            raise AssertionError
            self._normalize_offset(index)
            self._do_set_selected_item_index(index)

    def _get_selected_item_index(self):
        return self._selected_item_index

    selected_item_index = property(_get_selected_item_index, _set_selected_item_index)

    def _normalize_offset(self, index):
        if index >= 0:
            if index >= self._offset + self._num_visible_items:
                self._offset = index - (self._num_visible_items - 1)
            elif index < self._offset:
                self._offset = index
            self._offset = clamp(self._offset, 0, len(self._items) - self._num_visible_items)

    @property
    def selected_item(self):
        return self._items[self.selected_item_index] if in_range(self._selected_item_index, 0, len(self._items)) else None

    @property
    def items(self):
        return self._items

    def assign_items(self, items):
        old_selection = unicode(self.selected_item)
        for item in self._items:
            item._scrollable_list = None

        self._items = tuple([ self.item_type(index=index, content=item, scrollable_list=self) for index, item in enumerate(items) ])
        if self._items:
            new_selection = index_if(lambda item: unicode(item) == old_selection, self._items)
            self._selected_item_index = new_selection if in_range(new_selection, 0, len(self._items)) else 0
            self._normalize_offset(self._selected_item_index)
        else:
            self._offset = 0
            self._selected_item_index = -1
        self._last_activated_item_index = None
        self.notify_selected_item()
        self.request_notify_item_activated()

    def select_item(self, item):
        self.selected_item_index = item.index

    def is_selected(self, item):
        return item and item.index == self.selected_item_index

    def request_notify_item_activated(self):
        if self._selected_item_index != self._last_activated_item_index:
            self._last_activated_item_index = self._selected_item_index
            self.notify_item_activated()

    def _do_set_selected_item_index(self, index):
        if index != self._selected_item_index:
            self._selected_item_index = index
            self.notify_selected_item()


class ActionListItem(ScrollableListItem):
    """
    Interface for an list element that can be actuated on.
    """
    supports_action = False

    def action(self):
        pass


class ActionList(ScrollableList):
    """
    A scrollable list of items that can be actuated on.
    """
    item_type = ActionListItem


class DefaultItemFormatter(object):
    """
    Item formatter that will indicate selection and show action_message if the item
    is currently performing an action
    """
    action_message = 'Loading...'

    def __call__(self, index, item, action_in_progress):
        display_string = ''
        if item:
            display_string += consts.CHAR_SELECT if item.is_selected else ' '
            display_string += self.action_message if action_in_progress else unicode(item)
        return display_string


class ListComponent(CompoundComponent):
    """
    Component that handles a ScrollableList.  If an action button is
    passed, it can handle an ActionList.
    """
    __subject_events__ = ('item_action',)
    SELECTION_DELAY = 0.5
    ENCODER_FACTOR = 10.0
    empty_list_message = ''
    _current_action_item = None
    _last_action_item = None
    action_button = ButtonControl(color='Browser.Load')
    encoders = control_list(EncoderControl)

    def __init__(self, scrollable_list = None, data_sources = tuple(), *a, **k):
        super(ListComponent, self).__init__(*a, **k)
        self._data_sources = data_sources
        self._activation_task = Task.Task()
        self._action_on_scroll_task = Task.Task()
        self._scrollable_list = None
        self._scroller = self.register_component(ScrollComponent())
        self._pager = self.register_component(ScrollComponent())
        self.last_action_item = lambda : self._last_action_item
        self.item_formatter = DefaultItemFormatter()
        for c in (self._scroller, self._pager):
            for button in (c.scroll_up_button, c.scroll_down_button):
                button.color = 'List.ScrollerOn'
                button.pressed_color = None
                button.disabled_color = 'List.ScrollerOff'

        if scrollable_list == None:
            self.scrollable_list = ActionList(num_visible_items=len(data_sources))
        else:
            self.scrollable_list = scrollable_list
        self._scrollable_list.num_visible_items = len(data_sources)
        self._delay_activation = BooleanContext()
        self._selected_index_float = 0.0
        self._in_encoder_selection = BooleanContext(False)
        self._execute_action_task = self._tasks.add(Task.sequence(Task.delay(1), Task.run(self._execute_action)))
        self._execute_action_task.kill()

    @property
    def _trigger_action_on_scrolling(self):
        return self.action_button.is_pressed

    def _get_scrollable_list(self):
        return self._scrollable_list

    def _set_scrollable_list(self, new_list):
        if new_list != self._scrollable_list:
            self._scrollable_list = new_list
            if new_list != None:
                new_list.num_visible_items = len(self._data_sources)
                self._scroller.scrollable = new_list
                self._pager.scrollable = new_list.pager
                self._on_scroll.subject = new_list
                self._selected_index_float = new_list.selected_item_index
            else:
                self._scroller.scrollable = ScrollComponent.default_scrollable
                self._scroller.scrollable = ScrollComponent.default_pager
            self._on_selected_item_changed.subject = new_list
            self.update_all()

    scrollable_list = property(_get_scrollable_list, _set_scrollable_list)

    def set_data_sources(self, sources):
        self._data_sources = sources
        if self._scrollable_list:
            self._scrollable_list.num_visible_items = len(sources)
        self._update_display()

    select_next_button = forward_property('_scroller')('scroll_down_button')
    select_prev_button = forward_property('_scroller')('scroll_up_button')
    next_page_button = forward_property('_pager')('scroll_down_button')
    prev_page_button = forward_property('_pager')('scroll_up_button')

    def on_enabled_changed(self):
        super(ListComponent, self).on_enabled_changed()
        if not self.is_enabled():
            self._execute_action_task.kill()

    @subject_slot('scroll')
    def _on_scroll(self):
        if self._trigger_action_on_scrolling:
            trigger_selected = partial(self._trigger_action, self.selected_item)
            self._action_on_scroll_task.kill()
            self._action_on_scroll_task = self._tasks.add(Task.sequence(Task.wait(Defaults.MOMENTARY_DELAY), Task.delay(1), Task.run(trigger_selected)))

    @subject_slot('selected_item')
    def _on_selected_item_changed(self):
        self._scroller.update()
        self._pager.update()
        self._update_display()
        self._update_action_feedback()
        self._activation_task.kill()
        self._action_on_scroll_task.kill()
        if self.SELECTION_DELAY and self._delay_activation:
            self._activation_task = self._tasks.add(Task.sequence(Task.wait(self.SELECTION_DELAY), Task.run(self._scrollable_list.request_notify_item_activated)))
        else:
            self._scrollable_list.request_notify_item_activated()
        if not self._in_encoder_selection:
            self._selected_index_float = float(self._scrollable_list.selected_item_index)

    @encoders.value
    def encoders(self, value, encoder):
        self._add_offset_to_selected_index(value)

    def _add_offset_to_selected_index(self, offset):
        if self.is_enabled() and self._scrollable_list:
            with self._delay_activation():
                with self._in_encoder_selection():
                    self._selected_index_float = clamp(self._selected_index_float + offset * self.ENCODER_FACTOR, 0, len(self._scrollable_list.items))
                    self._scrollable_list.select_item_index_with_border(int(self._selected_index_float), 1)

    @action_button.pressed
    def action_button(self, button):
        if self._current_action_item == None:
            self._trigger_action(self.next_item if self._action_target_is_next_item() else self.selected_item)

    def do_trigger_action(self, item):
        item.action()
        self.notify_item_action(item)

    def _trigger_action(self, item):
        if self.is_enabled() and self._can_be_used_for_action(item):
            if self._scrollable_list != None:
                self._scrollable_list.select_item(item)
            self._current_action_item = item
            self.update()
            self._execute_action_task.restart()

    def _execute_action(self):
        """ Is called by the execute action task and should not be called directly
        use _trigger_action instead """
        if self._current_action_item != None:
            self.do_trigger_action(self._current_action_item)
            self._last_action_item = self._current_action_item
            self._current_action_item = None
            self.update()

    @property
    def selected_item(self):
        return self._scrollable_list.selected_item if self._scrollable_list != None else None

    @property
    def next_item(self):
        item = None
        if self._scrollable_list != None:
            all_items = self._scrollable_list.items
            next_index = self._scrollable_list.selected_item_index + 1
            item = all_items[next_index] if in_range(next_index, 0, len(all_items)) else None
        return item

    def _can_be_used_for_action(self, item):
        return item != None and item.supports_action and item != self.last_action_item()

    def _action_target_is_next_item(self):
        return self.selected_item == self.last_action_item() and self._can_be_used_for_action(self.next_item)

    def _update_action_feedback(self):
        color = 'Browser.Loading'
        if self._current_action_item == None:
            if self._action_target_is_next_item():
                color = 'Browser.LoadNext'
            elif self._can_be_used_for_action(self.selected_item):
                color = 'Browser.Load'
            else:
                color = 'Browser.LoadNotPossible'
        self.action_button.color = color

    def _update_display(self):
        visible_items = self._scrollable_list.visible_items if self._scrollable_list else []
        for index, data_source in enumerate(self._data_sources):
            item = visible_items[index] if index < len(visible_items) else None
            action_in_progress = item and item == self._current_action_item
            display_string = self.item_formatter(index, item, action_in_progress)
            data_source.set_display_string(display_string)

        if not visible_items and self._data_sources and self.empty_list_message:
            self._data_sources[0].set_display_string(self.empty_list_message)

    def update(self):
        super(ListComponent, self).update()
        if self.is_enabled():
            self._update_action_feedback()
            self._update_display()