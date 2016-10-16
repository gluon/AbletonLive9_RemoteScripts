#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Arturia/ScrollComponent.py
from _Framework.ScrollComponent import ScrollComponent as ScrollComponentBase
from _Framework.Control import EncoderControl

class ScrollComponent(ScrollComponentBase):
    scroll_encoder = EncoderControl()

    def set_scroll_encoder(self, encoder):
        self.scroll_encoder.set_control_element(encoder)
        self.update()

    @scroll_encoder.value
    def scroll_encoder(self, value, encoder):
        scroll_step = None
        if value > 0 and self.can_scroll_down():
            scroll_step = self._do_scroll_down
        elif value < 0 and self.can_scroll_up():
            scroll_step = self._do_scroll_up
        if scroll_step is not None:
            scroll_step()