#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_UserScript/__init__.py
from ConfigParser import ConfigParser
from _Generic.GenericScript import GenericScript
import Live
HIDE_SCRIPT = True

def interpret_map_mode(map_mode_name):
    result = Live.MidiMap.MapMode.absolute
    if map_mode_name == 'Absolute14Bit':
        result = Live.MidiMap.MapMode.absolute_14_bit
    elif map_mode_name == 'AccelSignedBit':
        result = Live.MidiMap.MapMode.relative_signed_bit
    elif map_mode_name == 'LinearSignedBit':
        result = Live.MidiMap.MapMode.relative_smooth_signed_bit
    elif map_mode_name == 'AccelSignedBit2':
        result = Live.MidiMap.MapMode.relative_signed_bit2
    elif map_mode_name == 'LinearSignedBit2':
        result = Live.MidiMap.MapMode.relative_smooth_signed_bit2
    elif map_mode_name == 'AccelBinaryOffset':
        result = Live.MidiMap.MapMode.relative_binary_offset
    elif map_mode_name == 'LinearBinaryOffset':
        result = Live.MidiMap.MapMode.relative_smooth_binary_offset
    elif map_mode_name == 'AccelTwoCompliment':
        result = Live.MidiMap.MapMode.relative_two_compliment
    elif map_mode_name == 'LinearTwoCompliment':
        result = Live.MidiMap.MapMode.relative_smooth_two_compliment
    return result


def create_instance(c_instance, user_path = ''):
    """ The generic script can be customised by using parameters.
        In this case, the user has written a text file with all necessary info.
        Here we read this file and fill the necessary data structures before
        instantiating the generic script.
    """
    device_map_mode = Live.MidiMap.MapMode.absolute
    volume_map_mode = Live.MidiMap.MapMode.absolute
    sends_map_mode = Live.MidiMap.MapMode.absolute
    if not user_path == '':
        file_object = open(user_path)
        if file_object:
            file_data = None
            config_parser = ConfigParser()
            config_parser.readfp(file_object, user_path)
            device_controls = [(-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1)]
            transport_controls = {'STOP': -1,
             'PLAY': -1,
             'REC': -1,
             'LOOP': -1,
             'RWD': -1,
             'FFWD': -1}
            volume_controls = [(-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1),
             (-1, -1)]
            trackarm_controls = [-1,
             -1,
             -1,
             -1,
             -1,
             -1,
             -1,
             -1]
            bank_controls = {'TOGGLELOCK': -1,
             'NEXTBANK': -1,
             'PREVBANK': -1,
             'BANK1': -1,
             'BANK2': -1,
             'BANK3': -1,
             'BANK4': -1,
             'BANK5': -1,
             'BANK6': -1,
             'BANK7': -1,
             'BANK8': -1}
            controller_descriptions = {'INPUTPORT': '',
             'OUTPUTPORT': '',
             'CHANNEL': -1}
            mixer_options = {'NUMSENDS': 2,
             'SEND1': [-1,
                       -1,
                       -1,
                       -1,
                       -1,
                       -1,
                       -1,
                       -1],
             'SEND2': [-1,
                       -1,
                       -1,
                       -1,
                       -1,
                       -1,
                       -1,
                       -1],
             'MASTERVOLUME': -1,
             'MASTERVOLUMECHANNEL': -1}
            for index in range(8):
                if config_parser.has_section('DeviceControls'):
                    encoder_tuple = [-1, -1]
                    option_name = 'Encoder' + str(index + 1)
                    if config_parser.has_option('DeviceControls', option_name):
                        option_value = config_parser.getint('DeviceControls', option_name)
                        if option_value in range(128):
                            encoder_tuple[0] = option_value
                    option_name = 'EncoderChannel' + str(index + 1)
                    if config_parser.has_option('DeviceControls', option_name):
                        option_value = config_parser.getint('DeviceControls', option_name)
                        if option_value in range(128):
                            encoder_tuple[1] = option_value
                    device_controls[index] = tuple(encoder_tuple)
                    option_name = 'Bank' + str(index + 1) + 'Button'
                    if config_parser.has_option('DeviceControls', option_name):
                        option_value = config_parser.getint('DeviceControls', option_name)
                        if option_value in range(128):
                            option_key = 'BANK' + str(index + 1)
                            bank_controls[option_key] = option_value
                if config_parser.has_section('MixerControls'):
                    volume_tuple = [-1, -1]
                    option_name = 'VolumeSlider' + str(index + 1)
                    if config_parser.has_option('MixerControls', option_name):
                        option_value = config_parser.getint('MixerControls', option_name)
                        if option_value in range(128):
                            volume_tuple[0] = option_value
                    option_name = 'Slider' + str(index + 1) + 'Channel'
                    if config_parser.has_option('MixerControls', option_name):
                        option_value = config_parser.getint('MixerControls', option_name)
                        if option_value in range(16):
                            volume_tuple[1] = option_value
                    volume_controls[index] = tuple(volume_tuple)
                    option_name = 'TrackArmButton' + str(index + 1)
                    if config_parser.has_option('MixerControls', option_name):
                        option_value = config_parser.getint('MixerControls', option_name)
                        if option_value in range(128):
                            trackarm_controls[index] = option_value
                    option_name = 'Send1Knob' + str(index + 1)
                    if config_parser.has_option('MixerControls', option_name):
                        option_value = config_parser.getint('MixerControls', option_name)
                        if option_value in range(128):
                            mixer_options['SEND1'][index] = option_value
                    option_name = 'Send2Knob' + str(index + 1)
                    if config_parser.has_option('MixerControls', option_name):
                        option_value = config_parser.getint('MixerControls', option_name)
                        if option_value in range(128):
                            mixer_options['SEND2'][index] = option_value
                if config_parser.has_section('Globals'):
                    if config_parser.has_option('Globals', 'GlobalChannel'):
                        option_value = config_parser.getint('Globals', 'GlobalChannel')
                        if option_value in range(16):
                            controller_descriptions['CHANNEL'] = option_value
                    if config_parser.has_option('Globals', 'InputName'):
                        controller_descriptions['INPUTPORT'] = config_parser.get('Globals', 'InputName')
                    if config_parser.has_option('Globals', 'OutputName'):
                        controller_descriptions['OUTPUTPORT'] = config_parser.get('Globals', 'OutputName')
                    pad_translation = []
                    for pad in range(16):
                        pad_info = []
                        note = -1
                        channel = -1
                        option_name = 'Pad' + str(pad + 1) + 'Note'
                        if config_parser.has_option('Globals', option_name):
                            note = config_parser.getint('Globals', option_name)
                            if note in range(128):
                                option_name = 'Pad' + str(pad + 1) + 'Channel'
                                if config_parser.has_option('Globals', option_name):
                                    channel = config_parser.getint('Globals', option_name)
                                if channel is -1 and controller_descriptions['CHANNEL'] is not -1:
                                    channel = controller_descriptions['CHANNEL']
                                if channel in range(16):
                                    pad_info.append(pad % 4)
                                    pad_info.append(int(pad / 4))
                                    pad_info.append(note)
                                    pad_info.append(channel)
                                    pad_translation.append(tuple(pad_info))

                    if len(pad_translation) > 0:
                        controller_descriptions['PAD_TRANSLATION'] = tuple(pad_translation)
                if config_parser.has_section('DeviceControls'):
                    if config_parser.has_option('DeviceControls', 'NextBankButton'):
                        option_value = config_parser.getint('DeviceControls', 'NextBankButton')
                        if option_value in range(128):
                            bank_controls['NEXTBANK'] = option_value
                    if config_parser.has_option('DeviceControls', 'PrevBankButton'):
                        option_value = config_parser.getint('DeviceControls', 'PrevBankButton')
                        if option_value in range(128):
                            bank_controls['PREVBANK'] = option_value
                    if config_parser.has_option('DeviceControls', 'LockButton'):
                        option_value = config_parser.getint('DeviceControls', 'LockButton')
                        if option_value in range(128):
                            bank_controls['TOGGLELOCK'] = option_value
                    if config_parser.has_option('DeviceControls', 'EncoderMapMode'):
                        device_map_mode = interpret_map_mode(config_parser.get('DeviceControls', 'EncoderMapMode'))
                if config_parser.has_section('MixerControls'):
                    if config_parser.has_option('MixerControls', 'MasterVolumeSlider'):
                        option_value = config_parser.getint('MixerControls', 'MasterVolumeSlider')
                        if option_value in range(128):
                            mixer_options['MASTERVOLUME'] = option_value
                    if config_parser.has_option('MixerControls', 'MasterSliderChannel'):
                        option_value = config_parser.getint('MixerControls', 'MasterSliderChannel')
                        if option_value in range(16):
                            mixer_options['MASTERVOLUMECHANNEL'] = option_value
                    if config_parser.has_option('MixerControls', 'VolumeMapMode'):
                        volume_map_mode = interpret_map_mode(config_parser.get('MixerControls', 'VolumeMapMode'))
                    if config_parser.has_option('MixerControls', 'SendsMapMode'):
                        sends_map_mode = interpret_map_mode(config_parser.get('MixerControls', 'SendsMapMode'))
                        mixer_options['SENDMAPMODE'] = sends_map_mode
                if config_parser.has_section('TransportControls'):
                    if config_parser.has_option('TransportControls', 'StopButton'):
                        option_value = config_parser.getint('TransportControls', 'StopButton')
                        if option_value in range(128):
                            transport_controls['STOP'] = option_value
                    if config_parser.has_option('TransportControls', 'PlayButton'):
                        option_value = config_parser.getint('TransportControls', 'PlayButton')
                        if option_value in range(128):
                            transport_controls['PLAY'] = option_value
                    if config_parser.has_option('TransportControls', 'RecButton'):
                        option_value = config_parser.getint('TransportControls', 'RecButton')
                        if option_value in range(128):
                            transport_controls['REC'] = option_value
                    if config_parser.has_option('TransportControls', 'LoopButton'):
                        option_value = config_parser.getint('TransportControls', 'LoopButton')
                        if option_value in range(128):
                            transport_controls['LOOP'] = option_value
                    if config_parser.has_option('TransportControls', 'RwdButton'):
                        option_value = config_parser.getint('TransportControls', 'RwdButton')
                        if option_value in range(128):
                            transport_controls['RWD'] = option_value
                    if config_parser.has_option('TransportControls', 'FfwdButton'):
                        option_value = config_parser.getint('TransportControls', 'FfwdButton')
                        if option_value in range(128):
                            transport_controls['FFWD'] = option_value

    return GenericScript(c_instance, device_map_mode, volume_map_mode, tuple(device_controls), transport_controls, tuple(volume_controls), tuple(trackarm_controls), bank_controls, controller_descriptions, mixer_options)