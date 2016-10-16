from RemoteSLComponent import RemoteSLComponent
from consts import *

class DisplayController(RemoteSLComponent):
    """Controls the 4 display rows of the RemoteSL.
    The left and right display can be individually controlled. Both displays will
    show in the upper row a freely defineable string, per strip (the parameter or
    track name). The lower rows will always show parameter values.
    """


    def __init__(self, remote_sl_parent):
        RemoteSLComponent.__init__(self, remote_sl_parent)
        self.__left_strip_names = [ str() for x in range(NUM_CONTROLS_PER_ROW) ]
        self.__left_strip_parameters = [ None for x in range(NUM_CONTROLS_PER_ROW) ]
        self.__right_strip_names = [ str() for x in range(NUM_CONTROLS_PER_ROW) ]
        self.__right_strip_parameters = [ None for x in range(NUM_CONTROLS_PER_ROW) ]
        self.refresh_state()



    def disconnect(self):
        self.__send_clear_displays()



    def setup_left_display(self, names, parameters):
        """Shows the given strings on the upper left row, the parameters values
                in the lower left row.
        
                'names' can be an array of NUM_CONTROLS_PER_ROW strings, or a list with
                exactly one string, which then will fill up the whole display
                """
        assert len(parameters) == NUM_CONTROLS_PER_ROW
        assert len(names) == NUM_CONTROLS_PER_ROW or len(names) == 1
        self.__left_strip_names = names
        self.__left_strip_parameters = parameters



    def setup_right_display(self, names, parameters):
        """Shows the given strings on the upper right row, the parameters values
                in the lower right row.
        
                'names' can be an array of NUM_CONTROLS_PER_ROW strings, or a list with
                exactly one string, which then will fill up the whole display
                """
        assert len(parameters) == NUM_CONTROLS_PER_ROW
        assert len(names) == NUM_CONTROLS_PER_ROW or len(names) == 1
        self.__right_strip_names = names
        self.__right_strip_parameters = parameters



    def update_display(self):
        for row_id in (1, 2, 3, 4):
            message_string = ''
            if row_id == 1 or row_id == 2:
                if row_id == 1:
                    strip_names = self.__left_strip_names
                else:
                    strip_names = self.__right_strip_names
                if len(strip_names) == NUM_CONTROLS_PER_ROW:
                    for s in strip_names:
                        message_string += self.__generate_strip_string(s)

                else:
                    assert len(strip_names) == 1
                message_string += strip_names[0]
            elif row_id == 3 or row_id == 4:
                if row_id == 3:
                    parameters = self.__left_strip_parameters
                else:
                    parameters = self.__right_strip_parameters
                assert len(parameters) == NUM_CONTROLS_PER_ROW
                for p in parameters:
                    if p:
                        message_string += self.__generate_strip_string(unicode(p))
                    else:
                        message_string += self.__generate_strip_string('')

            else:
                assert False
            self.__send_display_string(message_string, row_id, offset=0)




    def refresh_state(self):
        self.__last_send_row_id_messages = [None,
         [],
         [],
         [],
         []]



    def __send_clear_displays(self):
        start_clear_sysex = (240, 0, 32, 41, 3, 3, 18, 0)
        left_end_sysex = (ABLETON_PID,
         0,
         2,
         2,
         4,
         247)
        right_end_sysex = (ABLETON_PID,
         0,
         2,
         2,
         5,
         247)
        self.send_midi(start_clear_sysex + left_end_sysex)
        self.send_midi(start_clear_sysex + right_end_sysex)



    def __send_display_string(self, message, row_id, offset = 0):
        """Sends a sysex to update a complete row.
        
                'message' must be smaller than NUM_CHARS_PER_DISPLAY_LINE,
                'offset' can be something form 0 to NUM_CHARS_PER_DISPLAY_LINE - 1
                  (then the text is clipped)
        
                'row_id' is defined as followed: left_row1 = 1 | left_row2 = 2
                   left_row1 = 3] | left_row2 = 4
                """
        assert row_id in (1, 2, 3, 4)
        final_message = ' ' * offset + message
        if len(final_message) < NUM_CHARS_PER_DISPLAY_LINE:
            fill_up = NUM_CHARS_PER_DISPLAY_LINE - len(final_message)
            final_message = final_message + ' ' * fill_up
        elif len(final_message) >= NUM_CHARS_PER_DISPLAY_LINE:
            final_message = final_message[0:NUM_CHARS_PER_DISPLAY_LINE]
        final_offset = 0
        sysex_header = (240,
         0,
         32,
         41,
         3,
         3,
         18,
         0,
         ABLETON_PID,
         0,
         2,
         1)
        sysex_pos = (final_offset, row_id)
        sysex_text_command = (4,)
        sysex_text = tuple([ ord(c) for c in final_message ])
        sysex_close_up = (247,)
        full_sysex = sysex_header + sysex_pos + sysex_text_command + sysex_text + sysex_close_up
        if self.__last_send_row_id_messages[row_id] != full_sysex:
            self.__last_send_row_id_messages[row_id] = full_sysex
            self.send_midi(full_sysex)



    def __generate_strip_string(self, display_string):
        """ Hack: Shamelessly stolen from the MainDisplayController of the Mackie Control.
                Should share this in future in a 'Common' package!
        
                returns a 6 char string for of the passed string, trying to remove not so important
                letters and signs first...
                """
        if not display_string:
            return ' ' * NUM_CHARS_PER_DISPLAY_STRIP
        if len(display_string.strip()) > NUM_CHARS_PER_DISPLAY_STRIP - 1 and display_string.endswith('dB') and display_string.find('.') != -1:
            display_string = display_string[:-2]
        if len(display_string) > NUM_CHARS_PER_DISPLAY_STRIP - 1:
            for um in [' ',
             'i',
             'o',
             'u',
             'e',
             'a']:
                while len(display_string) > NUM_CHARS_PER_DISPLAY_STRIP - 1 and display_string.rfind(um, 1) != -1:
                    um_pos = display_string.rfind(um, 1)
                    display_string = display_string[:um_pos] + display_string[(um_pos + 1):]


        else:
            display_string = display_string.center(NUM_CHARS_PER_DISPLAY_STRIP - 1)
        ret = u''
        for i in range(NUM_CHARS_PER_DISPLAY_STRIP - 1):
            if ord(display_string[i]) > 127 or ord(display_string[i]) < 0:
                ret += ' '
            else:
                ret += display_string[i]

        ret += ' '
        assert len(ret) == NUM_CHARS_PER_DISPLAY_STRIP
        return ret




