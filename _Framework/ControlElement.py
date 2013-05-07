#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/ControlElement.py
from Resource import StackingResource
from Util import lazy_attribute
from Disconnectable import Disconnectable
from Dependency import depends
import Task

class ControlElement(Disconnectable):
    """
    Base class for all classes representing control elements on a
    control surface
    """
    canonical_parent = None
    name = ''
    optimized_send_midi = True
    _has_resource = False
    _resource_type = StackingResource
    _has_task_group = False

    @depends(send_midi=None, register_control=None)
    def __init__(self, name = '', resource_type = None, optimized_send_midi = None, send_midi = None, register_control = None, *a, **k):
        super(ControlElement, self).__init__(*a, **k)
        self._send_midi = send_midi
        self.name = name
        if resource_type is not None:
            self._resource_type = resource_type
        if optimized_send_midi is not None:
            self.optimized_send_midi = optimized_send_midi
        register_control(self)

    def disconnect(self):
        self.reset()
        super(ControlElement, self).disconnect()

    def send_midi(self, message):
        raise message != None or AssertionError
        return self._send_midi(message, optimized=self.optimized_send_midi)

    def clear_send_cache(self):
        pass

    def reset(self):
        raise NotImplementedError

    @property
    def resource(self):
        return self._resource

    @lazy_attribute
    def _resource(self):
        self._has_resource = True
        return self._resource_type(self._on_grab_resource, self._on_release_resource)

    @lazy_attribute
    @depends(parent_task_group=Task.TaskGroup)
    def _tasks(self, parent_task_group = None):
        tasks = parent_task_group.add(Task.TaskGroup())
        self._has_task_group = True
        return tasks

    def _on_grab_resource(self, client, *a, **k):
        client.set_control_element(self, True)

    def _on_release_resource(self, client):
        client.set_control_element(self, False)