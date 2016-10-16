#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl_Classic/MainDisplayController.py
from MackieControlComponent import *

class MainDisplayController(MackieControlComponent):
    """ Controlling all available main displays (the display above the channel strips),
        which will be only one when only using the 'main' Mackie Control, and severals
        when using at least one Mackie Control XT, attached to the main Mackie Control
    
        The Displays can be run in two modes: Channel and Global mode:
        - In channel mode 2*6 characters can be shown for each channel strip
        - In global mode, you can setup the two 54 charchter lines to whatever you want
    
        See 'class ChannelStripController' for descriptions of the stack_index or details
        about the different assignment modes.
    """

    def __init__(self, main_script, display):
        MackieControlComponent.__init__(self, main_script)
        self.__left_extensions = []
        self.__right_extensions = []
        self.__displays = [display]
        self.__own_display = display
        self.__parameters = [ [] for x in range(NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_strings = [ '' for x in range(NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_mode = True
        self.__show_parameter_names = False
        self.__bank_channel_offset = 0
        self.__meters_enabled = False
        self.__show_return_tracks = False

    def destroy(self):
        self.enable_meters(False)
        MackieControlComponent.destroy(self)

    def set_controller_extensions(self, left_extensions, right_extensions):
        """ Called from the main script (after all scripts where initialized), to let us
            know where and how many MackieControlXT are installed.
        """
        self.__left_extensions = left_extensions
        self.__right_extensions = right_extensions
        self.__displays = []
        stack_offset = 0
        for le in left_extensions:
            self.__displays.append(le.main_display())
            le.main_display().set_stack_offset(stack_offset)
            stack_offset += NUM_CHANNEL_STRIPS

        self.__displays.append(self.__own_display)
        self.__own_display.set_stack_offset(stack_offset)
        stack_offset += NUM_CHANNEL_STRIPS
        for re in right_extensions:
            self.__displays.append(re.main_display())
            re.main_display().set_stack_offset(stack_offset)
            stack_offset += NUM_CHANNEL_STRIPS

        self.__parameters = [ [] for x in range(len(self.__displays) * NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_strings = [ '' for x in range(len(self.__displays) * NUM_CHANNEL_STRIPS) ]
        self.refresh_state()

    def enable_meters(self, enabled):
        if self.__meters_enabled != enabled:
            self.__meters_enabled = enabled
            self.refresh_state()

    def set_show_parameter_names(self, enable):
        self.__show_parameter_names = enable

    def set_channel_offset(self, channel_offset):
        self.__bank_channel_offset = channel_offset

    def parameters(self):
        return self.__parameters

    def set_parameters(self, parameters):
        if parameters:
            self.set_channel_strip_strings(None)
        for d in self.__displays:
            self.__parameters = parameters

    def channel_strip_strings(self):
        return self.__channel_strip_strings

    def set_channel_strip_strings(self, channel_strip_strings):
        if channel_strip_strings:
            self.set_parameters(None)
        self.__channel_strip_strings = channel_strip_strings

    def set_show_return_track_names(self, show_returns):
        self.__show_return_tracks = show_returns

    def refresh_state(self):
        for d in self.__displays:
            d.refresh_state()

    def on_update_display_timer(self):
        strip_index = 0
        for display in self.__displays:
            if self.__channel_strip_mode:
                upper_string = u''
                lower_string = u''
                track_index_range = range(self.__bank_channel_offset + display.stack_offset(), self.__bank_channel_offset + display.stack_offset() + NUM_CHANNEL_STRIPS)
                if self.__show_return_tracks:
                    tracks = self.song().return_tracks
                else:
                    tracks = self.song().visible_tracks
                for t in track_index_range:
                    if self.__parameters and self.__show_parameter_names:
                        if self.__parameters[strip_index]:
                            upper_string += self.__generate_6_char_string(self.__parameters[strip_index][1])
                        else:
                            upper_string += self.__generate_6_char_string('')
                    elif t < len(tracks):
                        upper_string += self.__generate_6_char_string(tracks[t].name)
                    else:
                        upper_string += self.__generate_6_char_string('')
                    upper_string += ' '
                    if self.__parameters and self.__parameters[strip_index]:
                        if self.__parameters[strip_index][0]:
                            lower_string += self.__generate_6_char_string(unicode(self.__parameters[strip_index][0]))
                        else:
                            lower_string += self.__generate_6_char_string('')
                    elif self.__channel_strip_strings and self.__channel_strip_strings[strip_index]:
                        lower_string += self.__generate_6_char_string(self.__channel_strip_strings[strip_index])
                    else:
                        lower_string += self.__generate_6_char_string('')
                    lower_string += ' '
                    strip_index += 1

                display.send_display_string(upper_string, 0, 0)
                if not self.__meters_enabled:
                    display.send_display_string(lower_string, 1, 0)
            else:
                ascii_message = '< _1234 guck ma #!?:;_ >'
                if not self.__test:
                    self.__test = 0
                self.__test = self.__test + 1
                if self.__test > NUM_CHARS_PER_DISPLAY_LINE - len(ascii_message):
                    self.__test = 0
                self.send_display_string(ascii_message, 0, self.__test)

    def __generate_6_char_string(self, display_string):
        if not display_string:
            return '      '
        if len(display_string.strip()) > 6 and display_string.endswith('dB') and display_string.find('.') != -1:
            display_string = display_string[:-2]
        if len(display_string) > 6:
            for um in [' ',
             'i',
             'o',
             'u',
             'e',
             'a']:
                while len(display_string) > 6 and display_string.rfind(um, 1) != -1:
                    um_pos = display_string.rfind(um, 1)
                    display_string = display_string[:um_pos] + display_string[um_pos + 1:]

        else:
            display_string = display_string.center(6)
        ret = u''
        for i in range(6):
            ret += display_string[i]

        raise len(ret) == 6 or AssertionError
        return ret