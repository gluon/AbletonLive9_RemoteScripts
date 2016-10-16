#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/component.py
from __future__ import absolute_import, print_function
import Live
from .control import ControlManager
from ..base import depends, lazy_attribute, Subject, task, is_iterable
from ..base.dependency import dependency

class Component(ControlManager, Subject):
    """
    Base class for all classes encapsulating functions in Live
    """
    __events__ = ('enabled',)
    name = ''
    canonical_parent = None
    is_private = False
    _show_msg_callback = dependency(show_message=None)
    _has_task_group = False
    _layer = None

    @depends(register_component=None, song=None)
    def __init__(self, name = '', register_component = None, song = None, layer = None, is_enabled = True, is_root = False, *a, **k):
        raise callable(register_component) or AssertionError
        super(Component, self).__init__(*a, **k)
        self.name = name
        raise layer is None or not is_enabled or AssertionError
        self._explicit_is_enabled = is_enabled
        self._recursive_is_enabled = True
        self._is_enabled = self._explicit_is_enabled
        self._is_root = is_root
        self._allow_updates = True
        self._update_requests = 0
        self._song = song
        self._layer = layer
        register_component(self)

    def disconnect(self):
        if self._has_task_group:
            self._tasks.kill()
            self._tasks.clear()
        super(Component, self).disconnect()

    @property
    def is_root(self):
        return self._is_root

    def _internal_on_enabled_changed(self):
        if self.is_enabled():
            self._grab_all_layers()
        else:
            self._release_all_layers()
        if self._has_task_group:
            if self.is_enabled():
                self._tasks.resume()
            else:
                self._tasks.pause()

    def on_enabled_changed(self):
        self.update()

    def update_all(self):
        self.update()

    def set_enabled(self, enable):
        self._explicit_is_enabled = bool(enable)
        self._update_is_enabled()

    def _set_enabled_recursive(self, enable):
        self._recursive_is_enabled = bool(enable)
        self._update_is_enabled()

    def _update_is_enabled(self):
        is_enabled = self._recursive_is_enabled and self._explicit_is_enabled
        if is_enabled != self._is_enabled:
            self._is_enabled = is_enabled
            self._internal_on_enabled_changed()
            self.on_enabled_changed()
            self.notify_enabled(is_enabled)

    def set_allow_update(self, allow_updates):
        allow = bool(allow_updates)
        if self._allow_updates != allow:
            self._allow_updates = allow
            if self._allow_updates and self._update_requests > 0:
                self._update_requests = 0
                self.update()

    def control_notifications_enabled(self):
        return self.is_enabled()

    def application(self):
        return Live.Application.get_application()

    @property
    def song(self):
        return self._song

    @lazy_attribute
    @depends(parent_task_group=None)
    def _tasks(self, parent_task_group = None):
        tasks = parent_task_group.add(task.TaskGroup())
        if not self._is_enabled:
            tasks.pause()
        self._has_task_group = True
        return tasks

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, new_layer):
        if self._layer != new_layer:
            self._release_all_layers()
            self._layer = new_layer
            if self.is_enabled():
                self._grab_all_layers()

    def _grab_all_layers(self):
        for layer in self._get_layer_iterable():
            grabbed = layer.grab(self)
            raise grabbed or AssertionError('Only one component can use a layer at atime')

    def _release_all_layers(self):
        for layer in self._get_layer_iterable():
            layer.release(self)

    def _get_layer_iterable(self):
        if self._layer is None:
            return tuple()
        if is_iterable(self._layer):
            return self._layer
        return (self._layer,)

    def is_enabled(self, explicit = False):
        """
        Returns whether the component is enabled.
        If 'explicit' is True the parent state is ignored.
        """
        if not explicit:
            return self._is_enabled
        return self._explicit_is_enabled

    @depends(parent_task_group=None)
    def _register_timer_callback(self, callback, parent_task_group = None):
        """
        DEPRECATED. Use tasks instead
        """
        raise callable(callback) or AssertionError
        raise parent_task_group.find(callback) is None or AssertionError

        def wrapper(delta):
            callback()
            return task.RUNNING

        parent_task_group.add(task.FuncTask(wrapper, callback))

    @depends(parent_task_group=None)
    def _unregister_timer_callback(self, callback, parent_task_group = None):
        """
        DEPRECATED. Use tasks instead
        """
        raise callable(callback) or AssertionError
        t = parent_task_group.find(callback)
        raise t is not None or AssertionError
        parent_task_group.remove(t)