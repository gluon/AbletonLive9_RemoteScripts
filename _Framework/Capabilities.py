#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/_Framework/Capabilities.py
PORTS_KEY = 'ports'
CONTROLLER_ID_KEY = 'controller_id'
TYPE_KEY = 'surface_type'
FIRMWARE_KEY = 'firmware_version'
AUTO_LOAD_KEY = 'auto_load'
VENDORID = 'vendor_id'
PRODUCTIDS = 'product_ids'
MODEL_NAME = 'model_name'
DIRECTIONKEY = 'direction'
PORTNAMEKEY = 'name'
MACNAMEKEY = 'mac_name'
PROPSKEY = 'props'
HIDDEN = 'hidden'
SYNC = 'sync'
SCRIPT = 'script'
NOTES_CC = 'notes_cc'
REMOTE = 'remote'
PLAIN_OLD_MIDI = 'plain_old_midi'

def __create_port_dict(direction, port_name, mac_name, props):
    if not type(direction) is str:
        raise AssertionError
        raise type(port_name) is str or AssertionError
        raise props == None or type(props) is list or AssertionError
        if props:
            for prop in props:
                raise type(prop) is str or AssertionError

        raise mac_name == None or type(mac_name) is str or AssertionError
        capabilities = {DIRECTIONKEY: direction,
         PORTNAMEKEY: port_name,
         PROPSKEY: props}
        capabilities[MACNAMEKEY] = mac_name and mac_name
    return capabilities


def inport(port_name = '', props = [], mac_name = None):
    """ Generate a ..."""
    return __create_port_dict('in', port_name, mac_name, props)


def outport(port_name = '', props = [], mac_name = None):
    """ Generate a ..."""
    return __create_port_dict('out', port_name, mac_name, props)


def controller_id(vendor_id, product_ids, model_name):
    """ Generate a hardwareId dict"""
    raise type(vendor_id) is int or AssertionError
    raise type(product_ids) is list or AssertionError
    for product_id in product_ids:
        raise type(product_id) is int or AssertionError

    raise type(model_name) is str or AssertionError
    return {VENDORID: vendor_id,
     PRODUCTIDS: product_ids,
     MODEL_NAME: model_name}