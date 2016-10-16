#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_Pro/TranslationComponent.py
from functools import partial
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

class TranslationComponent(ControlSurfaceComponent):
    """
    Simple component that translates the MIDI channel of a one or more groups
    of buttons and will also enable/disable the buttons.
    """

    def __init__(self, translated_channel, should_enable = True, should_reset = True, *a, **k):
        raise translated_channel in range(16) or AssertionError
        self._translated_channel = translated_channel
        self._should_enable = bool(should_enable)
        self._should_reset = should_reset
        super(TranslationComponent, self).__init__(*a, **k)

    def __getattr__(self, name):
        if len(name) > 4 and name[:4] == 'set_':
            return partial(self._set_control_elements, name[4:])
        raise AttributeError(name)

    def _set_control_elements(self, name, control_elements):
        if bool(control_elements):
            buttons = control_elements
            for button in buttons:
                if button:
                    if self._should_reset:
                        button.reset()
                    else:
                        button.reset_state()
                    button.set_enabled(self._should_enable)
                    button.set_channel(self._translated_channel)