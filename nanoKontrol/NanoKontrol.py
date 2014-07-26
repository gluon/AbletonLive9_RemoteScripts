"""
# Copyright (C) 2009 Myralfur <james@waterworth.org.uk>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# For questions regarding this module contact
# Myralfur <james@waterworth.org.uk>
"""

from consts import *
from Transport import Transport
from Pads import Pads
from Encoders import Encoders
from SliderSection import SliderSection
import Live
import MidiRemoteScript

class NanoKontrol:
    __module__ = __name__
    __doc__ = ' A controller script for the Korg NanoKontrol '

    def __init__(self, c_instance):
        self._NanoKontrol__c_instance = c_instance
        self._NanoKontrol__current_track = self.song().view.selected_track
        self._NanoKontrol__current_device = self._NanoKontrol__current_track.view.selected_device
        self.song().add_tracks_listener(self._NanoKontrol__tracks_changed)
        self._NanoKontrol__transport_unit = Transport(self)
        self._NanoKontrol__encoder_unit = Encoders(self, True)
        self._NanoKontrol__slider_unit = SliderSection(self)
        self._NanoKontrol__pad_unit = Pads(self)



    def application(self):
        """returns a reference to the application that we are running in
    """
        return Live.Application.get_application()



    def song(self):
        """returns a reference to the Live song instance that we do control
    """
        return self._NanoKontrol__c_instance.song()



    def disconnect(self):
        """Live -> Script 
    Called right before we get disconnected from Live.
    """
        self.song().remove_tracks_listener(self._NanoKontrol__tracks_changed)



    def can_lock_to_devices(self):
        return True



    def suggest_input_port(self):
        """Live -> Script
    Live can ask the script for an input port name to find a suitable one.
    """
        return str('USB NanoKontrol')



    def suggest_output_port(self):
        """Live -> Script
    Live can ask the script for an output port name to find a suitable one.
    """
        return str('USB NanoKontrol')



    def suggest_map_mode(self, cc_no, channel):
        """Live -> Script
    Live can ask the script for a suitable mapping mode for a given CC.
    """
        suggested_map_mode = Live.MidiMap.MapMode.absolute
        return suggested_map_mode



    def show_message(self, message):
        self._NanoKontrol__c_instance.show_message(message)



    def connect_script_instances(self, instanciated_scripts):
        """Called by the Application as soon as all scripts are initialized.
    You can connect yourself to other running scripts here, as we do it
    connect the extension modules (MackieControlXTs).
    """
        pass


    def request_rebuild_midi_map(self):
        """Script -> Live
    When the internal MIDI controller has changed in a way that you need to rebuild
    the MIDI mappings, request a rebuild by calling this function
    This is processed as a request, to be sure that its not too often called, because
    its time-critical.
    """
        self._NanoKontrol__c_instance.request_rebuild_midi_map()



    def send_midi(self, midi_event_bytes):
        """Script -> Live
    Use this function to send MIDI events through Live to the _real_ MIDI devices
    that this script is assigned to.
    """
        self._NanoKontrol__c_instance.send_midi(midi_event_bytes)



    def refresh_state(self):
        """Live -> Script
    Send out MIDI to completely update the attached MIDI controller.
    Will be called when requested by the user, after for example having reconnected 
    the MIDI cables...
    """
        pass


    def build_midi_map(self, midi_map_handle):
        """Live -> Script
    Build DeviceParameter Mappings, that are processed in Audio time, or
    forward MIDI messages explicitly to our receive_midi_functions.
    Which means that when you are not forwarding MIDI, nor mapping parameters, you will 
    never get any MIDI messages at all.
    """
        print 'Midi Map reloaded'
        script_handle = self._NanoKontrol__c_instance.handle()
        self._NanoKontrol__transport_unit.build_midi_map(script_handle, midi_map_handle)
        self._NanoKontrol__encoder_unit.build_midi_map(script_handle, midi_map_handle)
        self._NanoKontrol__slider_unit.build_midi_map(script_handle, midi_map_handle)
        self._NanoKontrol__pad_unit.build_midi_map(script_handle, midi_map_handle)



    def update_display(self):
        """Live -> Script
    Aka on_timer. Called every 100 ms and should be used to update display relevant
    parts of the controller
    """
        if self._NanoKontrol__transport_unit:
            self._NanoKontrol__transport_unit.refresh_state()



    def receive_midi(self, midi_bytes):
        """Live -> Script
    MIDI messages are only received through this function, when explicitly 
    forwarded in 'build_midi_map'.
    """
        if ((midi_bytes[0] & 240) == CC_STATUS):
            channel = (midi_bytes[0] & 15)
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            if (list(NANOKONTROL_TRANSPORT).count(cc_no) > 0):
                self._NanoKontrol__transport_unit.receive_midi_cc(cc_no, cc_value)
            elif (list(NANOKONTROL_BUTTONS).count(cc_no) > 0):
                self._NanoKontrol__slider_unit.receive_midi_cc(cc_no, cc_value, channel)
            elif (list(NANOKONTROL_ENCODERS).count(cc_no) > 0):
                self._NanoKontrol__encoder_unit.receive_midi_cc(cc_no, cc_value, channel)
            elif (list(NANOKONTROL_PADS).count(cc_no) > 0):
                self._NanoKontrol__pad_unit.receive_midi_cc(cc_no, cc_value, channel)
        elif (midi_bytes[0] == 240):
            pass



    def lock_to_device(self, device):
        self._NanoKontrol__encoder_unit.lock_to_device(device)



    def unlock_from_device(self, device):
        self._NanoKontrol__encoder_unit.unlock_from_device(device)



    def set_appointed_device(self, device):
        self._NanoKontrol__encoder_unit.set_appointed_device(device)



    def __tracks_changed(self):
        self.request_rebuild_midi_map()



    def bank_changed(self, new_bank):
        if self._NanoKontrol__encoder_unit.set_bank(new_bank):
            self.request_rebuild_midi_map()



    def restore_bank(self, bank):
        self._NanoKontrol__encoder_unit.restore_bank(bank)
        self.request_rebuild_midi_map()



    def instance_identifier(self):
        return self._NanoKontrol__c_instance.instance_identifier()



