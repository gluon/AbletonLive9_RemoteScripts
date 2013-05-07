#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk2\MaschineDeviceComponent.py
import Live
from _Generic.Devices import *
from _Framework.DeviceComponent import DeviceComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector
from MIDI_Map import *

class MaschineDeviceComponent(DeviceComponent):
    """ Class representing a device in Live """

    def __init__(self, surface):
        DeviceComponent.__init__(self)
        self.surface = surface
        self.device_listener = None
        self.device_parm_listener = None
        self._control_translation_selector = ChannelTranslationSelector(8)

    def set_device(self, device):
        DeviceComponent.set_device(self, device)
        if self.device_listener != None:
            self.device_listener(device)

    def set_parameter_controls(self, controls):
        DeviceComponent.set_parameter_controls(self, controls)
        self._control_translation_selector.set_controls_to_translate(controls)
        self._control_translation_selector.set_mode(self._bank_index)

    def _on_parameters_changed(self):
        DeviceComponent._on_parameters_changed(self)
        if self.device_parm_listener != None:
            self.device_parm_listener()

    def set_device_changed_listener(self, listener):
        self.device_listener = listener

    def set_device_parm_listener(self, listener):
        self.device_parm_listener = listener

    def show_message(self, message):
        self.surface.show_message(message)

    def disconnect(self):
        DeviceComponent.disconnect(self)
        self._control_translation_selector.disconnect()
        self.surface = None
        self.device_listener = None
        self.device_parm_listener = None