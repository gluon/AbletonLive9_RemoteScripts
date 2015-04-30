#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/_Serato/PySCAClipControl.py
import libInterprocessCommsAPIPython

class PySCAClipControl:
    writer = 0
    writer_events = 0
    reader = 0
    reader_events = 0
    writer_clip_control_atom = 0

    def __init__(self):
        pass

    def interface_module(self):
        """ Simple getter to the module to avoid import conflicts in the unit tests """
        return libInterprocessCommsAPIPython

    def PySCA_InitializeClipControl(self):
        self.writer = libInterprocessCommsAPIPython.SCARetrieveWriterObject(libInterprocessCommsAPIPython.kAbletonClipControlCommunicationPath)
        self.writer_events = libInterprocessCommsAPIPython.SCAGetEventQueue(self.writer, libInterprocessCommsAPIPython.SCAGetAtomRef(self.writer, libInterprocessCommsAPIPython.kAbletonClipAndDeviceEventQueue))
        self.writer_clip_control_atom = libInterprocessCommsAPIPython.SCAGetAtomRef(self.writer, libInterprocessCommsAPIPython.kAbletonClipControl)

    def PySCA_InitializeIncomingPath(self):
        self.reader = libInterprocessCommsAPIPython.SCARetrieveReaderObject(libInterprocessCommsAPIPython.kSeratoToAbletonCommunicationPath)
        self.reader_events = libInterprocessCommsAPIPython.SCAGetEventQueue(self.reader, libInterprocessCommsAPIPython.SCAGetAtomRef(self.reader, libInterprocessCommsAPIPython.kSeratoAbletonClipAndDeviceEventQueue))

    def PySCA_DeinitializeClipControl(self):
        self.writer_events = 0
        self.writer_clip_control_atom = 0
        if self.writer != 0:
            libInterprocessCommsAPIPython.SCAReleaseWriterObject(libInterprocessCommsAPIPython.kAbletonClipControlCommunicationPath)
        self.writer = 0
        self.reader_events = 0
        if self.reader != 0:
            libInterprocessCommsAPIPython.SCAReleaseReaderObject(libInterprocessCommsAPIPython.kSeratoToAbletonCommunicationPath)
        self.reader = 0
        libInterprocessCommsAPIPython.SCACleanUpAllObjects()

    def PySCA_HandleIncomingEvents(self):
        event_type = 0
        event_key1 = 0
        event_key2 = 0
        event_data_size = 0
        event_data = 0
        while self.PySCA_GetIncomingEvent(event_type, event_key1, event_key2, event_data_size, event_data) == 0:
            pass

    def PySCA_PeekIncomingEvent(self, event_type, event_key1, event_key2, data_size, data):
        if not reader or not reader_events:
            self.PySCA_InitializeIncomingPath()
        if reader == 0 or reader_events == 0 or libInterprocessCommsAPIPython.SCAValidateReaderObject(self.reader) != 0:
            return -1
        return libInterprocessCommsAPIPython.SCAEventsReadEvent(event_type, event_key1, event_key2, data_size, data, None)

    def PySCA_HasIncomingEvent(self):
        if not self.reader or not self.reader_events:
            self.PySCA_InitializeIncomingPath()
        if self.reader == 0 or self.reader_events == 0 or libInterprocessCommsAPIPython.SCAValidateReaderObject(self.reader) != 0:
            return False
        return libInterprocessCommsAPIPython.SCAEventsPeekEvent(self.reader_events).type > -1

    def PySCA_GetIncomingEvent(self):
        if not self.reader or not self.reader_events:
            self.PySCA_InitializeIncomingPath()
        if self.reader == 0 or self.reader_events == 0 or libInterprocessCommsAPIPython.SCAValidateReaderObject(self.reader) != 0:
            return -1
        return libInterprocessCommsAPIPython.SCAEventsReadEvent(self.reader_events)

    def PySCA_SetSelectedTrack(self, track_id):
        self.PySCA_SetShMemClipControlIntVariableState(track_id, libInterprocessCommsAPIPython.kAbletonActiveTrackIndex, libInterprocessCommsAPIPython.kAbletonEventActiveTrackChanged)

    def PySCA_SetSelectedScene(self, scene_id):
        self.PySCA_SetShMemClipControlIntVariableState(scene_id, libInterprocessCommsAPIPython.kAbletonActiveSceneIndex, libInterprocessCommsAPIPython.kAbletonEventActiveSceneChanged)

    def PySCA_SetClipPlayState(self, track_id, clip_id, playstate):
        self.PySCA_SetShMemClipIntVariableState(track_id, clip_id, playstate, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonClip, libInterprocessCommsAPIPython.kAbletonClipPlayState, libInterprocessCommsAPIPython.kAbletonEventClipStateChanged)

    def PySCA_SetClipLoadState(self, track_id, clip_id, playstate):
        self.PySCA_SetShMemClipIntVariableState(track_id, clip_id, playstate, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonClip, libInterprocessCommsAPIPython.kAbletonClipLoadState, libInterprocessCommsAPIPython.kAbletonEventClipStateChanged)

    def PySCA_SetClipLabel(self, track_id, clip_id, label):
        self.PySCA_SetShMemClipLabelVariableState(track_id, clip_id, label, 40, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonClip, libInterprocessCommsAPIPython.kAbletonClipLabel, libInterprocessCommsAPIPython.kAbletonEventClipChanged)

    def PySCA_SetClipColor(self, track_id, clip_id, color):
        self.PySCA_SetShMemClipIntVariableState(track_id, clip_id, color, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonClip, libInterprocessCommsAPIPython.kAbletonClipColor, libInterprocessCommsAPIPython.kAbletonEventClipChanged)

    def PySCA_SetClipFilename(self, track_id, clip_id, filename):
        self.PySCA_SetShMemClipLabelVariableState(track_id, clip_id, label, 255, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonClip, libInterprocessCommsAPIPython.kAbletonClipLabel, libInterprocessCommsAPIPython.kAbletonEventClipChanged)

    def PySCA_SetSceneLabel(self, scene_id, label):
        self.PySCA_SetShMemClipLabelVariableState(0, scene_id, label, 40, libInterprocessCommsAPIPython.kAbletonMasterTrack, libInterprocessCommsAPIPython.kAbletonClip, libInterprocessCommsAPIPython.kAbletonClipLabel, libInterprocessCommsAPIPython.kAbletonEventClipChanged)

    def PySCA_SetSceneColor(self, scene_id, color):
        self.PySCA_SetShMemClipIntVariableState(0, scene_id, color, libInterprocessCommsAPIPython.kAbletonMasterTrack, libInterprocessCommsAPIPython.kAbletonClip, libInterprocessCommsAPIPython.kAbletonClipColor, libInterprocessCommsAPIPython.kAbletonEventClipChanged)

    def PySCA_SetTrackColor(self, track_id, color):
        self.PySCA_SetShMemTrackIntVariableState(track_id, color, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackColor, libInterprocessCommsAPIPython.kAbletonEventTrackChanged)

    def PySCA_SetTrackLabel(self, track_id, label):
        self.PySCA_SetShMemTrackLabelVariableState(track_id, label, 40, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackName, libInterprocessCommsAPIPython.kAbletonEventTrackChanged)

    def PySCA_SetTrackNumber(self, track_id, track_num):
        self.PySCA_SetShMemTrackIntVariableState(track_id, track_num, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackNumber, libInterprocessCommsAPIPython.kAbletonEventTrackChanged)

    def PySCA_SetTrackGainState(self, track_id, gain_value):
        self.PySCA_SetShMemTrackDoubleVariableState(track_id, gain_value, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackLevelState, libInterprocessCommsAPIPython.kAbletonEventTrackGainChanged)

    def PySCA_SetMasterGainState(self, gain_value):
        self.PySCA_SetShMemTrackDoubleVariableState(0, gain_value, libInterprocessCommsAPIPython.kAbletonMasterTrack, libInterprocessCommsAPIPython.kAbletonTrackLevelState, libInterprocessCommsAPIPython.kAbletonEventTrackGainChanged)

    def PySCA_SetTrackSendAState(self, track_id, send_value):
        self.PySCA_SetShMemTrackDoubleVariableState(track_id, send_value, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackSendAState, libInterprocessCommsAPIPython.kAbletonEventTrackSendsChanged)

    def PySCA_SetTrackSendBState(self, track_id, send_value):
        self.PySCA_SetShMemTrackDoubleVariableState(track_id, send_value, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackSendBState, libInterprocessCommsAPIPython.kAbletonEventTrackSendsChanged)

    def PySCA_SetTrackLevel(self, track_id, level_value):
        self.PySCA_SetShMemTrackDoubleVariableState(track_id, level_value, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackLevelMeterLevel, 0)

    def PySCA_SetMasterLevel(self, track_id, level_value):
        self.PySCA_SetShMemTrackDoubleVariableState(0, level_value, libInterprocessCommsAPIPython.kAbletonMasterTrack, libInterprocessCommsAPIPython.kAbletonTrackLevelMeterLevel, 0)

    def PySCA_SetTrackSoloState(self, track_id, solo_value):
        self.PySCA_SetShMemTrackIntVariableState(track_id, solo_value, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackSoloState, libInterprocessCommsAPIPython.kAbletonEventTrackSoloStateChanged)

    def PySCA_SetTrackRecordState(self, track_id, record_value):
        self.PySCA_SetShMemTrackIntVariableState(track_id, record_value, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackRecordState, libInterprocessCommsAPIPython.kAbletonEventTrackRecordStateChanged)

    def PySCA_SetTrackActiveState(self, track_id, active_value):
        self.PySCA_SetShMemTrackIntVariableState(track_id, active_value, libInterprocessCommsAPIPython.kAbletonTrack, libInterprocessCommsAPIPython.kAbletonTrackActiveState, libInterprocessCommsAPIPython.kAbletonEventTrackActiveStateChanged)

    def PySCA_SetDeviceActive(self, active_state):
        self.PySCA_SetShMemDeviceIndexVariableState(active_state, libInterprocessCommsAPIPython.kAbletonDeviceActive, libInterprocessCommsAPIPython.kAbletonEventDeviceActiveStateChanged)

    def PySCA_SetDeviceLabel(self, label):
        self.PySCA_SetShMemDeviceLabelVariableState(label, 40, libInterprocessCommsAPIPython.kAbletonDeviceName, libInterprocessCommsAPIPython.kAbletonEventDeviceLabelChanged)

    def PySCA_SetDeviceParamValue(self, param_id, param_value):
        self.PySCA_SetShMemDeviceParamDoubleVariableState(param_id, param_value, libInterprocessCommsAPIPython.kAbletonDevice, libInterprocessCommsAPIPython.kAbletonDeviceParamValue, libInterprocessCommsAPIPython.kAbletonEventDeviceParamValueChanged)

    def PySCA_SetDeviceParamLabel(self, param_id, label):
        self.PySCA_SetShMemDeviceParamLabelVariableState(param_id, label, 40, libInterprocessCommsAPIPython.kAbletonDevice, libInterprocessCommsAPIPython.kAbletonDeviceParamName, libInterprocessCommsAPIPython.kAbletonEventDeviceParamNameChanged)

    def PySCA_SetShMemClipControlIntVariableState(self, int_value, key_name, event_name):
        if self.writer and self.writer_events and self.writer_clip_control_atom:
            atom = libInterprocessCommsAPIPython.SCAGetAtomRefInsideContainer(self.writer, self.writer_clip_control_atom, key_name)
            libInterprocessCommsAPIPython.SCASetIntValue(self.writer, atom, int_value)
            if event_name:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, 0, 0, 0, None)

    def PySCA_SetShMemTrackDoubleVariableState(self, track_id, double_value, track_key_name, key_name, event_name):
        if self.writer and self.writer_events and self.writer_clip_control_atom:
            atom = libInterprocessCommsAPIPython.SCAGetAtomRefInsideContainerTwoKey(self.writer, self.writer_clip_control_atom, track_key_name, track_id, key_name)
            libInterprocessCommsAPIPython.SCASetDoubleValue(self.writer, atom, double_value)
            if event_name:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, track_id, 0, 0, None)

    def PySCA_SetShMemTrackIntVariableState(self, track_id, int_value, track_key_name, key_name, event_name):
        if self.writer and self.writer_events and self.writer_clip_control_atom:
            atom = libInterprocessCommsAPIPython.SCAGetAtomRefInsideContainerTwoKey(self.writer, self.writer_clip_control_atom, track_key_name, track_id, key_name)
            libInterprocessCommsAPIPython.SCASetIntValue(self.writer, atom, int_value)
            if event_name:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, track_id, 0, 0, None)

    def PySCA_SetShMemTrackLabelVariableState(self, track_id, label, max_length, track_key_name, key_name, event_name):
        if self.writer and self.writer_events and self.writer_clip_control_atom:
            atom = libInterprocessCommsAPIPython.SCAGetAtomRefInsideContainerTwoKey(self.writer, self.writer_clip_control_atom, track_key_name, track_id, key_name)
            result = libInterprocessCommsAPIPython.SCASetDataValue(self.writer, atom, label, max_length)
            if event_name and result == 0:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, track_id, 0, 0, None)

    def PySCA_SetShMemClipIntVariableState(self, track_id, clip_id, int_value, track_key_name, clip_key_name, key_name, event_name):
        if self.writer and self.writer_events and self.writer_clip_control_atom:
            track_atom = libInterprocessCommsAPIPython.SCAGetContainerAtomRefInsideContainer(self.writer, self.writer_clip_control_atom, track_key_name, track_id)
            atom = libInterprocessCommsAPIPython.SCAGetAtomRefInsideContainerTwoKey(self.writer, track_atom, clip_key_name, clip_id, key_name)
            libInterprocessCommsAPIPython.SCASetIntValue(self.writer, atom, int_value)
            if event_name:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, track_id, clip_id, 0, None)

    def PySCA_SetShMemClipLabelVariableState(self, track_id, clip_id, label, max_length, track_key_name, clip_key_name, key_name, event_name):
        if self.writer and self.writer_events and self.writer_clip_control_atom:
            track_atom = libInterprocessCommsAPIPython.SCAGetContainerAtomRefInsideContainer(self.writer, self.writer_clip_control_atom, track_key_name, track_id)
            atom = libInterprocessCommsAPIPython.SCAGetAtomRefInsideContainerTwoKey(self.writer, track_atom, clip_key_name, clip_id, key_name)
            result = libInterprocessCommsAPIPython.SCASetDataValue(self.writer, atom, label, max_length)
            if event_name and result == 0:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, track_id, clip_id, 0, None)

    def PySCA_SetShMemDeviceLabelVariableState(self, label, max_length, key_name, event_name):
        if self.writer and self.writer_events:
            atom = libInterprocessCommsAPIPython.SCAGetAtomRef(self.writer, key_name)
            result = libInterprocessCommsAPIPython.SCASetDataValue(self.writer, atom, label, max_length)
            if event_name and result == 0:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, 0, 0, 0, None)

    def PySCA_SetShMemDeviceIndexVariableState(self, int_value, key_name, event_name):
        if self.writer and self.writer_events:
            atom = libInterprocessCommsAPIPython.SCAGetAtomRef(self.writer, key_name)
            libInterprocessCommsAPIPython.SCASetIntValue(self.writer, atom, int_value)
            if event_name:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, 0, 0, 0, None)

    def PySCA_SetShMemDeviceParamDoubleVariableState(self, device_id, double_value, device_key_name, key_name, event_name):
        if self.writer and self.writer_events:
            atom = libInterprocessCommsAPIPython.SCAGetAtomRefTwoKey(self.writer, device_key_name, device_id, key_name)
            libInterprocessCommsAPIPython.SCASetDoubleValue(self.writer, atom, double_value)
            if event_name:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, device_id, 0, 0, None)

    def PySCA_SetShMemDeviceParamLabelVariableState(self, device_id, label, max_length, device_key_name, key_name, event_name):
        if self.writer and self.writer_events:
            atom = libInterprocessCommsAPIPython.SCAGetAtomRefTwoKey(self.writer, device_key_name, device_id, key_name)
            result = libInterprocessCommsAPIPython.SCASetDataValue(self.writer, atom, label, max_length)
            if event_name and result == 0:
                libInterprocessCommsAPIPython.SCAEventsWriteEvent(self.writer_events, event_name, device_id, 0, 0, None)