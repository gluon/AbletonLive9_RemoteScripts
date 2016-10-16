#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/ControlSurfaceComponent.py
from __future__ import absolute_import
import Live
from . import Task
from .Control import ControlManager
from .Dependency import dependency, depends
from .SubjectSlot import Subject
from .Util import lazy_attribute

class ControlSurfaceComponent(ControlManager, Subject):
    """
    Base class for all classes encapsulating functions in Live
    """
    name = ''
    canonical_parent = None
    is_private = False
    _show_msg_callback = dependency(show_message=None)
    _has_task_group = False
    _layer = None

    @depends(register_component=None, song=None)
    def __init__(self, name = '', register_component = None, song = None, layer = None, is_enabled = True, is_root = False, *a, **k):
        if not callable(register_component):
            raise AssertionError
            super(ControlSurfaceComponent, self).__init__(*a, **k)
            self.name = name
            raise layer is None or not is_enabled or AssertionError
            self._explicit_is_enabled = is_enabled
            self._recursive_is_enabled = True
            self._is_enabled = self._explicit_is_enabled
            self._is_root = is_root
            self._allow_updates = True
            self._update_requests = 0
            self._song = song
            self._layer = layer is not None and layer
        register_component(self)

    def disconnect(self):
        if self._has_task_group:
            self._tasks.kill()
            self._tasks.clear()
        super(ControlSurfaceComponent, self).disconnect()

    @property
    def is_root(self):
        return self._is_root

    def _internal_on_enabled_changed(self):
        if self._layer:
            if self.is_enabled():
                grabbed = self._layer.grab(self)
                if not grabbed:
                    raise AssertionError('Only one component can use a layer at atime')
                else:
                    self._layer.release(self)
            if self._has_task_group:
                self.is_enabled() and self._tasks.resume()
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

    def song(self):
        return self._song

    @lazy_attribute
    @depends(parent_task_group=None)
    def _tasks(self, parent_task_group = None):
        tasks = parent_task_group.add(Task.TaskGroup())
        if not self._is_enabled:
            tasks.pause()
        self._has_task_group = True
        return tasks

    def _get_layer(self):
        return self._layer

    def _set_layer(self, new_layer):
        if self._layer != new_layer:
            if self._layer:
                self._layer.release(self)
            self._layer = new_layer
            if new_layer and self.is_enabled():
                grabbed = new_layer.grab(self)
                raise grabbed or AssertionError('Only one component can use a layer at atime')

    layer = property(_get_layer, _set_layer)

    def is_enabled(self, explicit = False):
        """
        Returns whether the component is enabled.
        If 'explicit' is True the parent state is ignored.
        """
        if not explicit:
            return self._is_enabled
        return self._explicit_is_enabled

    def on_track_list_changed(self):
        """
        Called by the control surface if tracks are added/removed,
        to be overridden
        """
        pass

    def on_scene_list_changed(self):
        """
        Called by the control surface if scenes are added/removed, to
        be overridden
        """
        pass

    def on_selected_track_changed(self):
        """
        Called by the control surface when a track is selected, to be
        overridden
        """
        pass

    def on_selected_scene_changed(self):
        """
        Called by the control surface when a scene is selected, to be
        overridden
        """
        pass

    @depends(parent_task_group=None)
    def _register_timer_callback(self, callback, parent_task_group = None):
        """
        DEPRECATED. Use tasks instead
        """
        raise callable(callback) or AssertionError
        raise parent_task_group.find(callback) is None or AssertionError

        def wrapper(delta):
            callback()
            return Task.RUNNING

        parent_task_group.add(Task.FuncTask(wrapper, callback))

    @depends(parent_task_group=None)
    def _unregister_timer_callback(self, callback, parent_task_group = None):
        """
        DEPRECATED. Use tasks instead
        """
        raise callable(callback) or AssertionError
        task = parent_task_group.find(callback)
        raise task is not None or AssertionError
        parent_task_group.remove(task)