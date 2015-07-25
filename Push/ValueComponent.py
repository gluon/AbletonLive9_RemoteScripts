#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/ValueComponent.py
from _Framework.Control import EncoderControl, ButtonControl
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import forward_property
from _Framework.InputControlElement import ParameterSlot
from DeviceParameterComponent import convert_parameter_value_to_graphic
import consts
NUM_SEGMENTS = 4

def convert_value_to_graphic(value):
    index = int(value * (len(consts.GRAPH_VOL) - 1))
    if index != None and index < len(consts.GRAPH_VOL):
        graphic_display_string = consts.GRAPH_VOL[index]
    else:
        graphic_display_string = ' '
    return graphic_display_string


class ValueDisplayComponentBase(ControlSurfaceComponent):

    def __init__(self, display_label = ' ', display_seg_start = 0, *a, **k):
        super(ValueDisplayComponentBase, self).__init__(*a, **k)
        self._label_data_source = DisplayDataSource(display_label)
        self._value_data_source = DisplayDataSource()
        self._graphic_data_source = DisplayDataSource()
        self._display_label = display_label
        self._display_seg_start = display_seg_start

    def get_value_string(self):
        raise NotImplementedError

    def get_graphic_string(self):
        raise NotImplementedError

    def set_label_display(self, display):
        self._set_display(display, self._label_data_source)

    def set_value_display(self, display):
        self._set_display(display, self._value_data_source)

    def set_graphic_display(self, display):
        self._set_display(display, self._graphic_data_source)

    def set_clear_display1(self, display):
        self._clear_display(display)

    def set_clear_display2(self, display):
        self._clear_display(display)

    def set_clear_display3(self, display):
        self._clear_display(display)

    def set_clear_display4(self, display):
        self._clear_display(display)

    def _set_display(self, display, source):
        if display:
            display.set_data_sources((None,) * NUM_SEGMENTS)
            display.segment(self._display_seg_start).set_data_source(source)

    def _clear_display(self, display):
        if display:
            display.set_data_sources((None,))
            display.reset()

    def update(self):
        super(ValueDisplayComponentBase, self).update()
        if self.is_enabled():
            self._value_data_source.set_display_string(self.get_value_string())
            self._graphic_data_source.set_display_string(self.get_graphic_string())


class ValueComponentBase(CompoundComponent):
    """
    Component to control one continuous property with a infinite
    touch-sensitive encoder. You can optionally give it a display and
    a button such that the value will be displayed while its pressed.
    """

    def create_display_component(self, *a, **k):
        raise NotImplementedError

    encoder = EncoderControl()

    def __init__(self, display_label = ' ', display_seg_start = 0, *a, **k):
        super(ValueComponentBase, self).__init__(*a, **k)
        self._display = self.register_component(self.create_display_component(display_label=display_label, display_seg_start=display_seg_start))
        self._display.set_enabled(False)

    display_layer = forward_property('_display')('layer')

    @encoder.touched
    def encoder(self, encoder):
        self._update_display_state()

    @encoder.released
    def encoder(self, encoder):
        self._update_display_state()

    @encoder.value
    def encoder(self, value, encoder):
        self._on_value(value)

    def _on_value(self, value):
        pass

    def _update_display_state(self):
        self._display.set_enabled(self.encoder.is_touched)


class ValueDisplayComponent(ValueDisplayComponentBase):
    """
    Display for values from standard Python properties.
    """

    def __init__(self, property_name = None, subject = None, display_format = '%f', view_transform = None, graphic_transform = None, *a, **k):
        super(ValueDisplayComponent, self).__init__(*a, **k)
        self._subject = subject
        self._property_name = property_name
        self._display_format = display_format
        if view_transform is not None:
            self.view_transform = view_transform
        if graphic_transform is not None:
            self.graphic_transform = graphic_transform
        self.register_slot(subject, self._on_value_changed, property_name)
        self._on_value_changed()

    def view_transform(self, x):
        return x

    def graphic_transform(self, x):
        return self.view_transform(x)

    def get_value_string(self):
        value = getattr(self._subject, self._property_name)
        return self._display_format % self.view_transform(value)

    def get_graphic_string(self):
        value = getattr(self._subject, self._property_name)
        graph = self.graphic_transform(value)
        return convert_value_to_graphic(graph)

    def _on_value_changed(self):
        self.update()


class ValueComponent(ValueComponentBase):
    """
    Component to control one continuous property with a infinite
    touch-sensitive encoder. You can optionally give it a display and
    a button such that the value will be displayed while its pressed.
    """
    shift_button = ButtonControl()
    encoder_factor = 1.0

    def create_display_component(self, *a, **k):
        return ValueDisplayComponent(property_name=self._property_name, subject=self._subject, display_format=self._display_format, view_transform=(lambda x: self.view_transform(x)), graphic_transform=(lambda x: self.graphic_transform(x)), *a, **k)

    def __init__(self, property_name = None, subject = None, display_format = '%f', model_transform = None, view_transform = None, graphic_transform = None, encoder_factor = None, *a, **k):
        self._property_name = property_name
        self._subject = subject
        self._display_format = display_format
        super(ValueComponent, self).__init__(*a, **k)
        if model_transform is not None:
            self.model_transform = model_transform
        if view_transform is not None:
            self.view_transform = view_transform
        if graphic_transform is not None:
            self.graphic_transform = graphic_transform
        if encoder_factor is not None:
            self.encoder_factor = encoder_factor
        self._original_encoder_factor = self.encoder_factor

    def model_transform(self, x):
        """
        Tranform a value 'x' from the view domain to the domain as
        stored in the subject.
        """
        return x

    def view_transform(self, x):
        """
        Transform a value 'x' from the model domain to the view domain
        as represented to the user.
        """
        return x

    def graphic_transform(self, x):
        """
        Transform a value 'x' from the model domain to [0..1] range to
        be used in the slider-representation of the value.
        """
        return self.view_transform(x) / self.encoder_factor

    @shift_button.pressed
    def shift_button(self, button):
        self.encoder_factor = self._original_encoder_factor / 10.0

    @shift_button.released
    def shift_button(self, button):
        self.encoder_factor = self._original_encoder_factor

    def _on_value(self, value):
        super(ValueComponent, self)._on_value(value)
        value = self.view_transform(getattr(self._subject, self._property_name)) + value * self.encoder_factor
        setattr(self._subject, self._property_name, self.model_transform(value))


class ParameterValueDisplayComponent(ValueDisplayComponentBase):
    """
    Display for values from device parameters.
    """

    def __init__(self, device_parameter = None, *a, **k):
        super(ParameterValueDisplayComponent, self).__init__(*a, **k)
        self._on_value_changed.subject = device_parameter
        self._on_value_changed()

    def get_value_string(self):
        return str(self._on_value_changed.subject)

    def get_graphic_string(self):
        return convert_parameter_value_to_graphic(self._on_value_changed.subject)

    @subject_slot('value')
    def _on_value_changed(self):
        self.update()


class ParameterValueComponent(ValueComponentBase):
    """
    Component to control a device parameter with a infinite
    touch-sensitive encoder. You can optionally give it a display and
    a button such that the value will be displayed while its pressed.
    """

    def create_display_component(self, *a, **k):
        return ParameterValueDisplayComponent(device_parameter=self._parameter_slot.parameter, *a, **k)

    def __init__(self, device_parameter = None, *a, **k):
        self._parameter_slot = ParameterSlot(device_parameter)
        super(ParameterValueComponent, self).__init__(*a, **k)
        self.register_disconnectable(self._parameter_slot)

    def set_encoder(self, encoder):
        self.encoder.set_control_element(encoder)
        self._parameter_slot.control = encoder