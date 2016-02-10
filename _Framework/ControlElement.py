#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/ControlElement.py
from __future__ import absolute_import
import traceback
from . import Task
from .Dependency import depends
from .Disconnectable import Disconnectable
from .Resource import StackingResource
from .Util import lazy_attribute, nop, const, second, print_message

class ControlElementClient(object):

    def set_control_element(self, control_element, grabbed):
        pass


class ElementOwnershipHandler(object):
    """
    A ControlElementOwnershipHandler deals with the actual delivery of
    the control element to its clients.
    """

    def handle_ownership_change(self, control, client, status):
        client.set_control_element(control, status)


class OptimizedOwnershipHandler(ElementOwnershipHandler):
    """
    Control element ownership handler that delays notification of
    ownership changes and minimizes the number of actual owernship
    changes that are delivered.
    """

    def __init__(self, *a, **k):
        super(OptimizedOwnershipHandler, self).__init__(*a, **k)
        self._ownership_changes = {}
        self._sequence_number = 0

    def handle_ownership_change(self, control, client, status):
        if (control, client, not status) in self._ownership_changes:
            del self._ownership_changes[control, client, not status]
        else:
            self._ownership_changes[control, client, status] = self._sequence_number
        self._sequence_number += 1

    @depends(log_message=const(print_message), traceback=const(traceback))
    def commit_ownership_changes(self, log_message = None, traceback = None):
        notify = super(OptimizedOwnershipHandler, self).handle_ownership_change
        while self._ownership_changes:
            notifications = sorted(self._ownership_changes.iteritems(), key=second)
            self._ownership_changes.clear()
            for (control, client, status), _ in notifications:
                try:
                    notify(control, client, status)
                except Exception:
                    log_message('Error when trying to give control:', control.name)
                    traceback.print_exc()

        self._ownership_changes.clear()
        self._sequence_number = 0


class ControlElement(Disconnectable):
    """
    Base class for all classes representing control elements on a
    control surface
    """

    class ProxiedInterface(object):
        """
        Declaration of the interface to be used when the
        ControlElement is wrapped in any form of Proxy object.
        """
        send_midi = nop
        reset_state = nop

        def __init__(self, outer = None, *a, **k):
            super(ControlElement.ProxiedInterface, self).__init__(*a, **k)
            self._outer = outer

        @property
        def outer(self):
            return self._outer

    @lazy_attribute
    def proxied_interface(self):
        return self.ProxiedInterface(outer=self)

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

    def reset_state(self):
        pass

    @property
    def resource(self):
        return self._resource

    @lazy_attribute
    def _resource(self):
        self._has_resource = True
        return self._resource_type(self._on_resource_received, self._on_resource_lost)

    @lazy_attribute
    @depends(parent_task_group=Task.TaskGroup)
    def _tasks(self, parent_task_group = None):
        tasks = parent_task_group.add(Task.TaskGroup())
        self._has_task_group = True
        return tasks

    def _on_resource_received(self, client, *a, **k):
        self.notify_ownership_change(client, True)

    def _on_resource_lost(self, client):
        self.notify_ownership_change(client, False)

    @depends(element_ownership_handler=const(ElementOwnershipHandler()))
    def notify_ownership_change(self, client, grabbed, element_ownership_handler = None):
        element_ownership_handler.handle_ownership_change(self, client, grabbed)