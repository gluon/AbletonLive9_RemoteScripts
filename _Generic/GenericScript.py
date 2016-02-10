#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Generic/GenericScript.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.DeviceComponent import DeviceComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from SpecialMixerComponent import SpecialMixerComponent

class GenericScript(ControlSurface):
    """ A generic script class with predefined behaviour.
        It can be customised to use/not use certain controls on instantiation.
    """

    def __init__(self, c_instance, macro_map_mode, volume_map_mode, device_controls, transport_controls, volume_controls, trackarm_controls, bank_controls, descriptions = None, mixer_options = None):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            global_channel = 0
            if descriptions:
                if list(descriptions.keys()).count('INPUTPORT') > 0:
                    self._suggested_input_port = descriptions['INPUTPORT']
                if list(descriptions.keys()).count('OUTPUTPORT') > 0:
                    self._suggested_output_port = descriptions['OUTPUTPORT']
                if list(descriptions.keys()).count('CHANNEL') > 0:
                    global_channel = descriptions['CHANNEL']
                    if global_channel not in range(16):
                        global_channel = 0
                if list(descriptions.keys()).count('PAD_TRANSLATION') > 0:
                    self.set_pad_translations(descriptions['PAD_TRANSLATION'])
            self._init_mixer_component(volume_controls, trackarm_controls, mixer_options, global_channel, volume_map_mode)
            self._init_device_component(device_controls, bank_controls, global_channel, macro_map_mode)
            self._init_transport_component(transport_controls, global_channel)

    def handle_sysex(self, midi_bytes):
        pass

    def _init_mixer_component(self, volume_controls, trackarm_controls, mixer_options, global_channel, volume_map_mode):
        if volume_controls != None and trackarm_controls != None:
            num_strips = max(len(volume_controls), len(trackarm_controls))
            send_info = []
            momentary_buttons = False
            mixer = SpecialMixerComponent(num_strips)
            mixer.name = 'Mixer'
            mixer.master_strip().name = 'Master_Channel_Strip'
            mixer.selected_strip().name = 'Selected_Channel_Strip'
            if mixer_options != None:
                if 'MASTERVOLUME' in mixer_options.keys() and mixer_options['MASTERVOLUME'] in range(128):
                    encoder = EncoderElement(MIDI_CC_TYPE, global_channel, mixer_options['MASTERVOLUME'], volume_map_mode)
                    encoder.name = 'Master_Volume_Control'
                    mixer.master_strip().set_volume_control(encoder)
                if 'NUMSENDS' in mixer_options.keys() and mixer_options['NUMSENDS'] > 0:
                    for send in range(mixer_options['NUMSENDS']):
                        key = 'SEND' + str(send + 1)
                        raise key in mixer_options.keys() or AssertionError
                        send_info.append(mixer_options[key])

                momentary_buttons = 'NOTOGGLE' in mixer_options.keys()
                next_bank_button = None
                prev_bank_button = None
                if 'NEXTBANK' in mixer_options.keys() and mixer_options['NEXTBANK'] in range(128):
                    next_bank_button = ButtonElement(momentary_buttons, MIDI_CC_TYPE, global_channel, mixer_options['NEXTBANK'])
                    next_bank_button.name = 'Mixer_Next_Bank_Button'
                if 'PREVBANK' in mixer_options.keys() and mixer_options['PREVBANK'] in range(128):
                    prev_bank_button = ButtonElement(momentary_buttons, MIDI_CC_TYPE, global_channel, mixer_options['PREVBANK'])
                    prev_bank_button.name = 'Mixer_Previous_Bank_Button'
                mixer.set_bank_buttons(next_bank_button, prev_bank_button)
            for track in range(num_strips):
                strip = mixer.channel_strip(track)
                strip.name = 'Channel_Strip_' + str(track)
                if track in range(len(volume_controls)):
                    channel = global_channel
                    cc = volume_controls[track]
                    if isinstance(volume_controls[track], (tuple, list)):
                        cc = volume_controls[track][0]
                        if volume_controls[track][1] in range(16):
                            channel = volume_controls[track][1]
                    if cc in range(128) and channel in range(16):
                        encoder = EncoderElement(MIDI_CC_TYPE, channel, cc, volume_map_mode)
                        encoder.name = str(track) + '_Volume_Control'
                        strip.set_volume_control(encoder)
                if track in range(len(trackarm_controls)) and trackarm_controls[track] in range(128):
                    button = ButtonElement(momentary_buttons, MIDI_CC_TYPE, global_channel, trackarm_controls[track])
                    button.name = str(track) + '_Arm_Button'
                    strip.set_arm_button(button)
                send_controls = []
                for send in send_info:
                    encoder = None
                    if track in range(len(send)):
                        channel = global_channel
                        cc = send[track]
                        if isinstance(send[track], (tuple, list)):
                            cc = send[track][0]
                            if send[track][1] in range(16):
                                channel = send[track][1]
                        if cc in range(128) and channel in range(16):
                            encoder = EncoderElement(MIDI_CC_TYPE, channel, cc, volume_map_mode)
                            encoder.name = str(track) + '_Send_' + str(list(send_info).index(send)) + '_Control'
                    send_controls.append(encoder)

                strip.set_send_controls(tuple(send_controls))

    def _init_device_component(self, device_controls, bank_controls, global_channel, macro_map_mode):
        is_momentary = True
        if device_controls:
            device = DeviceComponent()
            device.name = 'Device_Component'
            if bank_controls:
                next_button = None
                prev_button = None
                if 'NEXTBANK' in bank_controls.keys() and bank_controls['NEXTBANK'] in range(128):
                    next_button = ButtonElement(is_momentary, MIDI_CC_TYPE, global_channel, bank_controls['NEXTBANK'])
                    next_button.name = 'Device_Next_Bank_Button'
                if 'PREVBANK' in bank_controls.keys() and bank_controls['PREVBANK'] in range(128):
                    prev_button = ButtonElement(is_momentary, MIDI_CC_TYPE, global_channel, bank_controls['PREVBANK'])
                    prev_button.name = 'Device_Previous_Bank_Button'
                device.set_bank_nav_buttons(prev_button, next_button)
                if 'TOGGLELOCK' in bank_controls.keys() and bank_controls['TOGGLELOCK'] in range(128):
                    lock_button = ButtonElement(is_momentary, MIDI_CC_TYPE, global_channel, bank_controls['TOGGLELOCK'])
                    lock_button.name = 'Device_Lock_Button'
                    device.set_lock_button(lock_button)
                bank_buttons = []
                for index in range(8):
                    key = 'BANK' + str(index + 1)
                    if key in bank_controls.keys():
                        control_info = bank_controls[key]
                        channel = global_channel
                        cc = -1
                        if isinstance(control_info, (tuple, list)):
                            cc = control_info[0]
                            if control_info[1] in range(16):
                                channel = control_info[1]
                        else:
                            cc = control_info
                        if cc in range(128) and channel in range(16):
                            button = ButtonElement(is_momentary, MIDI_CC_TYPE, channel, cc)
                            button.name = 'Device_Bank_' + str(index) + '_Button'
                            bank_buttons.append(button)

                if len(bank_buttons) > 0:
                    device.set_bank_buttons(tuple(bank_buttons))
            parameter_encoders = []
            for control_info in device_controls:
                channel = global_channel
                cc = -1
                if isinstance(control_info, (tuple, list)):
                    cc = control_info[0]
                    if control_info[1] in range(16):
                        channel = control_info[1]
                else:
                    cc = control_info
                if cc in range(128) and channel in range(16):
                    encoder = EncoderElement(MIDI_CC_TYPE, channel, cc, macro_map_mode)
                    encoder.name = 'Device_Parameter_' + str(list(device_controls).index(control_info)) + '_Control'
                    parameter_encoders.append(encoder)

            if len(parameter_encoders) > 0:
                device.set_parameter_controls(tuple(parameter_encoders))
            self.set_device_component(device)

    def _init_transport_component(self, transport_controls, global_channel):
        is_momentary = True
        if transport_controls:
            transport = TransportComponent()
            transport.name = 'Transport'
            if 'STOP' in transport_controls.keys() and transport_controls['STOP'] in range(128):
                stop_button = ButtonElement(is_momentary, MIDI_CC_TYPE, global_channel, transport_controls['STOP'])
                stop_button.name = 'Stop_Button'
                transport.set_stop_button(stop_button)
            if 'PLAY' in transport_controls.keys() and transport_controls['PLAY'] in range(128):
                play_button = ButtonElement(is_momentary, MIDI_CC_TYPE, global_channel, transport_controls['PLAY'])
                play_button.name = 'Play_Button'
                transport.set_play_button(play_button)
            if 'REC' in transport_controls.keys() and transport_controls['REC'] in range(128):
                rec_button = ButtonElement(is_momentary, MIDI_CC_TYPE, global_channel, transport_controls['REC'])
                rec_button.name = 'Record_Button'
                transport.set_record_button(rec_button)
            if 'LOOP' in transport_controls.keys() and transport_controls['LOOP'] in range(128):
                loop_button = ButtonElement(is_momentary, MIDI_CC_TYPE, global_channel, transport_controls['LOOP'])
                loop_button.name = 'Loop_Button'
                transport.set_loop_button(loop_button)
            ffwd_button = None
            rwd_button = None
            momentary_seek = 'NORELEASE' not in transport_controls.keys()
            if 'FFWD' in transport_controls.keys() and transport_controls['FFWD'] in range(128):
                ffwd_button = ButtonElement(momentary_seek, MIDI_CC_TYPE, global_channel, transport_controls['FFWD'])
                ffwd_button.name = 'FFwd_Button'
            if 'RWD' in transport_controls.keys() and transport_controls['RWD'] in range(128):
                rwd_button = ButtonElement(momentary_seek, MIDI_CC_TYPE, global_channel, transport_controls['RWD'])
                rwd_button.name = 'Rwd_Button'
            transport.set_seek_buttons(ffwd_button, rwd_button)