#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AxiomPro/PageableDeviceComponent.py
import Live
from _Generic.Devices import *
from _Framework.DeviceComponent import DeviceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.DisplayDataSource import DisplayDataSource
SPECIAL_NAME_DICT = {'InstrumentImpulse': (('Pad1', 'Pad2'),
                       ('Pad3', 'Pad4'),
                       ('Pad5', 'Pad6'),
                       ('Pad7', 'Pad8')),
 'Operator': (('OscA', 'OscB', 'OscC', 'OscD'),
              ('LFO', 'Fltr'),
              ('Pitch',),
              ('Glob.',)),
 'MultiSampler': (('Vol.', 'Pitch'),
                  ('Fltr', 'FEnv'),
                  ('LFO1', 'LFO2', 'LFO3'),
                  ('Osc',)),
 'UltraAnalog': (('Osc',),
                 ('Fltr', 'FEnv', 'FMod'),
                 ('VEnv', 'Mix'),
                 ('Out',)),
 'LoungeLizard': (('Ma&Ti',),
                  ('To&Da',),
                  ('Pick', 'Mod'),
                  ('Glob.',)),
 'StringStudio': (('Ex&St', 'Damp'),
                  ('Te&Pi', 'Body'),
                  ('Fltr', 'LFO'),
                  ('Glob.', 'Vibr')),
 'Eq8': (('Bands', 'EQ1-3'),
         ('Freq', 'Gain'),
         ('Reso', 'Fltr'),
         ('Glob.',))}
SPECIAL_DEVICE_DICT = {'InstrumentImpulse': [(IMP_BANK1, IMP_BANK2),
                       (IMP_BANK3, IMP_BANK4),
                       (IMP_BANK5, IMP_BANK6),
                       (IMP_BANK7, IMP_BANK8)],
 'Operator': [(OPR_BANK1,
               OPR_BANK2,
               OPR_BANK3,
               OPR_BANK4),
              (OPR_BANK5, OPR_BANK6),
              (OPR_BANK7,),
              (OPR_BANK8,)],
 'MultiSampler': [(SAM_BANK1, SAM_BANK8),
                  (SAM_BANK2, SAM_BANK3),
                  (SAM_BANK4, SAM_BANK5, SAM_BANK6),
                  (SAM_BANK7,)],
 'UltraAnalog': [(ALG_BANK1,),
                 (ALG_BANK2, ALG_BANK3, ALG_BANK4),
                 (ALG_BANK5, ALG_BANK6),
                 (ALG_BANK7,)],
 'LoungeLizard': [(ELC_BANK1,),
                  (ELC_BANK2,),
                  (ELC_BANK3, ELC_BANK4),
                  (ELC_BANK5,)],
 'StringStudio': [(TNS_BANK1, TNS_BANK2),
                  (TNS_BANK3, TNS_BANK4),
                  (TNS_BANK6, TNS_BANK7),
                  (TNS_BANK8, TNS_BANK5)],
 'Eq8': [(EQ8_BANK1, EQ8_BANK7),
         (EQ8_BANK2, EQ8_BANK3),
         (EQ8_BANK4, EQ8_BANK5),
         (EQ8_BANK6,)]}

class PageableDeviceComponent(DeviceComponent):
    """ Class representing a device on the AxiomPro """

    def __init__(self):
        DeviceComponent.__init__(self)
        self._parameter_value_data_source = DisplayDataSource()
        self._parameter_name_data_sources = []
        self._page_name_data_sources = []
        self._page_index = [0,
         0,
         0,
         0]
        for new_index in range(8):
            self._parameter_name_data_sources.append(DisplayDataSource())
            self._page_name_data_sources.append(DisplayDataSource())
            self._parameter_name_data_sources[-1].set_display_string(' - ')
            self._page_name_data_sources[-1].set_display_string(' - ')

    def disconnect(self):
        self._parameter_value_data_source = None
        self._parameter_name_data_sources = None
        self._page_name_data_sources = None
        DeviceComponent.disconnect(self)

    def set_device(self, device):
        DeviceComponent.set_device(self, device)
        if self._device == None:
            for source in self._parameter_name_data_sources:
                source.set_display_string(' - ')

            for source in self._page_name_data_sources:
                source.set_display_string(' - ')

    def set_bank_buttons(self, buttons):
        raise buttons == None or isinstance(buttons, tuple) and len(buttons) == 4 or AssertionError
        DeviceComponent.set_bank_buttons(self, buttons)

    def set_parameter_controls(self, controls):
        raise controls == None or isinstance(controls, tuple) and len(controls) == 8 or AssertionError
        if self._parameter_controls != None:
            for control in self._parameter_controls:
                if self._device != None:
                    control.release_parameter()

        self._parameter_controls = controls
        if self._parameter_controls != None:
            for control in self._parameter_controls:
                raise control != None or AssertionError
                raise isinstance(control, EncoderElement) or AssertionError

        self.update()

    def parameter_value_data_source(self):
        return self._parameter_value_data_source

    def parameter_name_data_source(self, index):
        raise index in range(8) or AssertionError
        return self._parameter_name_data_sources[index]

    def page_name_data_source(self, index):
        raise index in range(8) or AssertionError
        return self._page_name_data_sources[index]

    def _bank_value(self, value, button):
        if not self._bank_buttons != None:
            raise AssertionError
            raise value != None or AssertionError
            raise button != None or AssertionError
            raise isinstance(value, int) or AssertionError
            raise isinstance(button, ButtonElement) or AssertionError
            if not list(self._bank_buttons).count(button) == 1:
                raise AssertionError
                if self.is_enabled():
                    if not button.is_momentary() or value is not 0:
                        bank = list(self._bank_buttons).index(button)
                        self._bank_index = self._device != None and bank != self._bank_index and bank
                    else:
                        self._page_index[bank] += 1
                    self.update()

    def _assign_parameters(self):
        if not self.is_enabled():
            raise AssertionError
            raise self._device != None or AssertionError
            raise self._parameter_controls != None or AssertionError
            self._device.class_name in SPECIAL_DEVICE_DICT.keys() and self.__assign_parameters_special()
        elif self._device.class_name in DEVICE_DICT.keys():
            self.__assign_parameters_normal()
        else:
            self.__assign_parameters_plugin()
        self._parameter_value_data_source.set_display_string('')
        for index in range(len(self._parameter_controls)):
            if self._parameter_controls[index].mapped_parameter() != None:
                self._parameter_name_data_sources[index].set_display_string(self._parameter_controls[index].mapped_parameter().name)
            else:
                self._parameter_name_data_sources[index].set_display_string(' - ')

    def __assign_parameters_special(self):
        """ Assign the controls to the parameters of a device with more than 4 pages """
        banks = SPECIAL_DEVICE_DICT[self._device.class_name]
        bank_names = SPECIAL_NAME_DICT[self._device.class_name]
        pages = banks[self._bank_index]
        self._page_index[self._bank_index] %= len(pages)
        self._bank_name = bank_names[self._bank_index][self._page_index[self._bank_index]]
        page = pages[self._page_index[self._bank_index]]
        raise len(page) >= len(self._parameter_controls) or AssertionError
        for index in range(len(self._parameter_controls)):
            parameter = get_parameter_by_name(self._device, page[index])
            if parameter != None:
                self._parameter_controls[index].connect_to(parameter)
            else:
                self._parameter_controls[index].release_parameter()

        for index in range(len(self._page_name_data_sources)):
            if index < len(bank_names):
                page_names = bank_names[index]
                if index == self._bank_index:
                    self._page_name_data_sources[index].set_display_string(page_names[(self._page_index[index] + 1) % len(page_names)])
                else:
                    self._page_name_data_sources[index].set_display_string(page_names[self._page_index[index] % len(page_names)])
            else:
                self._page_name_data_sources[index].set_display_string(' - ')

    def __assign_parameters_normal(self):
        """ Assign the controls to the parameters of a device with 4 pages or less """
        if not self._device.class_name in DEVICE_BOB_DICT.keys():
            raise AssertionError
            self._page_index[self._bank_index] = 0
            banks = DEVICE_DICT[self._device.class_name]
            bank_names = []
            if len(banks) > self._bank_index:
                if self._device.class_name in BANK_NAME_DICT.keys() and len(BANK_NAME_DICT[self._device.class_name]) > 1:
                    bank_names = BANK_NAME_DICT[self._device.class_name]
                bank = banks[self._bank_index]
                self._bank_name = self._bank_index in range(len(bank_names)) and bank_names[self._bank_index]
            else:
                self._bank_name = 'Bank ' + str(self._bank_index + 1)
            raise len(bank) >= len(self._parameter_controls) or AssertionError
            for index in range(len(self._parameter_controls)):
                parameter = get_parameter_by_name(self._device, bank[index])
                if parameter != None:
                    self._parameter_controls[index].connect_to(parameter)
                else:
                    self._parameter_controls[index].release_parameter()

        for index in range(len(self._page_name_data_sources)):
            if index < len(bank_names):
                self._page_name_data_sources[index].set_display_string(bank_names[index])
            else:
                self._page_name_data_sources[index].set_display_string(' - ')

    def __assign_parameters_plugin(self):
        """ Assign the controls to the parameters of a plugin """
        num_controls = len(self._parameter_controls)
        num_banks = min(8, number_of_parameter_banks(self._device))
        num_double_pages = 0
        num_double_pages_before = 0
        parameters_to_use = self._device.parameters[1:]
        self._bank_name = 'Bank ' + str(self._bank_index + 1)
        if num_banks > 4:
            num_double_pages = num_banks - 4
        if self._bank_index < num_double_pages:
            self._page_index[self._bank_index] %= 2
            num_double_pages_before = self._bank_index
        else:
            self._page_index[self._bank_index] = 0
            num_double_pages_before = num_double_pages
        if self._bank_index + num_double_pages_before < num_banks:
            bank_offset = (self._bank_index + num_double_pages_before) * num_controls
            page_offset = bank_offset + self._page_index[self._bank_index] * num_controls
            for control in self._parameter_controls:
                if page_offset < len(parameters_to_use):
                    control.connect_to(parameters_to_use[page_offset])
                else:
                    control.release_parameter()
                page_offset += 1

            bank_names = []
            parameter_offset = 0
            for index in range(4):
                display_string = ' - '
                if index < num_banks:
                    if index < num_double_pages:
                        add_offset_before = index == self._bank_index and self._page_index[index] == 0 or index != self._bank_index and self._page_index[index] != 0
                        if add_offset_before:
                            parameter_offset += num_controls
                        display_string = str(parameter_offset + 1).rjust(2) + '-' + str(parameter_offset + num_controls).rjust(2)
                        if not add_offset_before:
                            parameter_offset += num_controls
                    else:
                        display_string = str(parameter_offset + 1).rjust(2) + '-' + str(parameter_offset + num_controls).rjust(2)
                self._page_name_data_sources[index].set_display_string(display_string)
                parameter_offset += num_controls