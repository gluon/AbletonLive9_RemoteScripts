#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AxiomPro/EncoderMixerModeSelector.py
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.DisplayDataSource import DisplayDataSource
from NotifyingMixerComponent import NotifyingMixerComponent

class EncoderMixerModeSelector(ModeSelectorComponent):
    """ Class that reassigns encoders on the AxiomPro to different mixer functions """

    def __init__(self, mixer):
        raise isinstance(mixer, NotifyingMixerComponent) or AssertionError
        ModeSelectorComponent.__init__(self)
        self._mixer = mixer
        self._controls = None
        self._page_names = ('Vol', 'Pan', 'SendA', 'SendB', 'SendC')
        self._page_name_sources = None
        self._current_page_data_source = DisplayDataSource()
        self._parameter_sources = [ DisplayDataSource() for index in range(8) ]
        self._show_volume_page = False
        self._mixer.set_update_callback(self._mixer_assignments_changed)

    def disconnect(self):
        for button in self._modes_buttons:
            button.remove_value_listener(self._mode_value)

        self._mixer = None
        self._controls = None
        self._page_names = None
        self._page_name_sources = None
        self._current_page_data_source = None
        self._parameter_sources = None
        ModeSelectorComponent.disconnect(self)

    def set_modes_buttons(self, buttons):
        raise buttons == None or isinstance(buttons, tuple) or len(buttons) == self.number_of_modes() or AssertionError
        identify_sender = True
        for button in self._modes_buttons:
            button.remove_value_listener(self._mode_value)

        self._modes_buttons = []
        if buttons != None:
            for button in buttons:
                raise isinstance(button, ButtonElement) or AssertionError
                self._modes_buttons.append(button)
                button.add_value_listener(self._mode_value, identify_sender)

        self.set_mode(0)
        self.update()

    def set_controls(self, controls):
        raise controls == None or isinstance(controls, tuple) and len(controls) == 8 or AssertionError
        self._controls = controls
        self.set_mode(0)
        self.update()

    def set_show_volume_page(self, show):
        if not isinstance(show, type(False)):
            raise AssertionError
            if show != self._show_volume_page:
                self._show_volume_page = show
                if self._page_name_sources != None:
                    offset = 0
                    offset = self._show_volume_page or 1
                for idx in range(4):
                    self._page_name_sources[idx].set_display_string(self._page_names[idx + offset])

            self.update()

    def page_name_data_source(self, index):
        if not index in range(4):
            raise AssertionError
            if self._page_name_sources == None:
                self._page_name_sources = []
                offset = 0
                offset = self._show_volume_page or 1
            for idx in range(4):
                self._page_name_sources.append(DisplayDataSource())
                self._page_name_sources[idx].set_display_string(self._page_names[idx + offset])

        return self._page_name_sources[index]

    def parameter_data_source(self, index):
        raise self._controls != None or AssertionError
        raise index in range(len(self._controls)) or AssertionError
        return self._mixer.channel_strip(index).track_name_data_source()

    def current_page_data_source(self):
        return self._current_page_data_source

    def number_of_modes(self):
        return 4

    def update(self):
        super(EncoderMixerModeSelector, self).update()
        if not self._modes_buttons != None:
            raise AssertionError
            if self.is_enabled() and self._controls != None:
                mode = self._mode_index
                self._show_volume_page or mode += 1
            self._current_page_data_source.set_display_string(self._page_names[mode])
            for index in range(len(self._controls)):
                self._controls[index].release_parameter()
                self._mixer.channel_strip(index).track_name_data_source().update()
                self._mixer.channel_strip(index).set_pan_control(None)
                self._mixer.channel_strip(index).set_send_controls((None, None, None))
                if self._show_volume_page:
                    self._mixer.channel_strip(index).set_volume_control(None)
                if not (mode == 0 and self._show_volume_page):
                    raise AssertionError
                    self._mixer.channel_strip(index).set_volume_control(self._controls[index])
                elif mode == 1:
                    self._mixer.channel_strip(index).set_pan_control(self._controls[index])
                elif mode == 2:
                    self._mixer.channel_strip(index).set_send_controls((self._controls[index], None, None))
                elif mode == 3:
                    self._mixer.channel_strip(index).set_send_controls((None, self._controls[index], None))
                elif not (mode == 4 and not self._show_volume_page):
                    raise AssertionError
                    self._mixer.channel_strip(index).set_send_controls((None, None, self._controls[index]))
                else:
                    print 'Invalid mode index'
                    raise False or AssertionError

    def _mixer_assignments_changed(self):
        self.update()