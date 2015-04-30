#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/KeyFadr/KeyFadr.py
from KeyPad import KeyPad

class KeyFadr(KeyPad):
    """
    Reloop KeyFadr controller script.
    """
    _encoder_range = range(80, 72, -1)
    _product_model_id = 102

    def __init__(self, *a, **k):
        super(KeyFadr, self).__init__(*a, **k)