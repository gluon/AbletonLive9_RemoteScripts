#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/Debug.py
enable_debug_output = True

def debug_print(*a):
    """ Special function for debug output """
    if enable_debug_output:
        print ' '.join(map(str, a))