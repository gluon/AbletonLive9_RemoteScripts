#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_13/LC2Sequencer.py
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from LC2Sysex import LC2Sysex, LC2SysexParser
import random
import math

class LC2Sequencer(ControlSurfaceComponent):

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._register_timer_callback(self._on_timer)
        self._refresh = 0
        self._clip = None
        self._note_cache = []
        self._last_note = 36
        self._last_pos = 0
        self._quantisation = 0.25
        self._default_length = 1
        self._default_velocity = 100
        self._time_offset = 0
        self._note_offset = 36
        self._num_steps = 16
        self._height = 16
        self._root = 0
        self._scale = 0
        self._scales = [[],
         [0,
          2,
          4,
          5,
          7,
          9,
          11],
         [0,
          2,
          3,
          5,
          7,
          8,
          10],
         [0,
          2,
          3,
          5,
          7,
          8,
          11],
         [0,
          2,
          4,
          7,
          9]]
        self._mutes = [ 0 for i in range(127) ]
        self._fader_type = 0
        self._fold_notes = 0
        self._save_note = 0
        self._ltime = ''
        self._chord_intervals = [[0, 4, 7],
         [0, 3, 7],
         [0, 4, 8],
         [0, 4, 6],
         [0, 3, 6],
         [0, 5, 7]]
        self._quick_chord = 127
        self._durations = [0.125,
         0.25,
         0.5,
         0.75,
         1,
         1.25,
         1.5,
         2,
         4]
        self._selection = [0,
         0,
         0,
         0]
        self._last_details = [-1,
         -1,
         -1,
         -1,
         -1]
        if LC2Sysex.l9():
            self._clisten = ('loop_start', 'loop_end', 'start_marker', 'end_marker')
        else:
            self._clisten = ('loop_start', 'loop_end')

    def select(self, slot):
        if slot.has_clip:
            self.set_clip(slot.clip, slot)
            self._selection = [-1,
             -1,
             -1,
             -1]
            self._send_selection(127)

    def set_clip(self, clip, slot):
        if self._clip is not None:
            try:
                if self._clip.playing_position_has_listener(self._on_playing_position_changed):
                    self._clip.remove_playing_position_listener(self._on_playing_position_changed)
                if self._clip.notes_has_listener(self._on_notes_changed):
                    self._clip.remove_notes_listener(self._on_notes_changed)
                if self._slot.has_clip_has_listener(self._on_slot_changed):
                    self._slot.remove_has_clip_listener(self._on_slot_changed)
                for l in self._clisten:
                    chk = getattr(self._clip, l + '_has_listener')
                    if chk(self._on_length_changed):
                        rem = getattr(self._clip, 'remove_' + l + '_listener')
                        rem(self._on_length_changed)

            except:
                pass

        self._clip = clip
        self._slot = slot
        if clip is not None:
            self._clip.add_playing_position_listener(self._on_playing_position_changed)
            self._clip.add_notes_listener(self._on_notes_changed)
            self._slot.add_has_clip_listener(self._on_slot_changed)
            for l in self._clisten:
                add = getattr(self._clip, 'add_' + l + '_listener')
                add(self._on_length_changed)

            LC2Sysex.log_message(str(self._clip.length))
            self._quantisation = 0.25
            self._time_offset = 0
        sysex = LC2Sysex('CLIP_TITLE')
        sysex.ascii(clip is not None and clip.canonical_parent.canonical_parent.name + ': ' + str(list(clip.canonical_parent.canonical_parent.clip_slots).index(clip.canonical_parent) + 1) + '. ' + (clip.name and clip.name or 'Unnamed') or '')
        sysex.rgb(clip is not None and clip.color or 0)
        sysex.send()
        self._cache_notes()
        if self._clip is not None:
            min = 128
            for note in self._note_cache:
                if note[0] < min:
                    min = note[0]

            self._note_offset = len(self._note_cache) == 0 and 36 or min
        self._fold_notes = 0
        self._save_note = 0
        self._send_offsets()
        self._on_playing_position_changed()
        self.update()

    def _on_length_changed(self):
        self.update()
        self._send_offsets()

    def _on_slot_changed(self):
        if not self._slot.has_clip:
            sysex = LC2Sysex('SEQ_CLOSE')
            sysex.send()

    def _cache_notes(self):
        if self._clip is not None:
            self._clip.select_all_notes()
            self._mutes = [ 0 for i in range(127) ]
            for n in self._clip.get_selected_notes():
                self._note_cache.append(list(n))
                if not self._mutes[n[0]]:
                    if n[4] == True:
                        self._mutes[n[0]] = 1

            self._note_cache = [ list(n) for n in self._clip.get_selected_notes() ]
            self._clip.deselect_all_notes()
        else:
            self._note_cache = []

    def handle_sysex(self, sysex):
        cmds = [self._note_press,
         self._fader_press,
         self._select_note,
         self._mute_note,
         self._scroll_time,
         self._scroll_note,
         self._zoom,
         self._set_quick_chord,
         self._set_selection,
         self._midi_action,
         self._set_root_scale,
         self._randomise_fader,
         self._set_defaults,
         self._set_fader_fn,
         self._set_height,
         self._set_fold,
         self._set_save]
        cmd = sysex[0]
        if cmd < len(cmds):
            if self._clip is not None:
                cmds[cmd](LC2SysexParser(sysex[1:]))

    def _set_save(self, sysex):
        self._save_note = not self._save_note
        self.update()

    def _set_fold(self, sysex):
        if self._fold_notes:
            self._fold_notes = 0
        else:
            self._fold_notes = 1
        self.update()

    def _set_height(self, sysex):
        self._height = sysex.parse('b') and 12 or 16
        self.update()

    def _set_fader_fn(self, sysex):
        self._fader_type = sysex.parse('b')
        self.update()

    def _set_defaults(self, sysex):
        len_pow, self._default_velocity = sysex.parse('bb')
        self._default_length = pow(2, int((len_pow / 100.0 - 0.5) * 4))

    def _zoom(self, sysex):
        ud = sysex.parse('b')
        if self._clip is not None:
            old = self._clip.length / (self._num_steps * self._quantisation)
        if ud:
            if self._quantisation > 0.0625:
                self._quantisation /= 2
                if self._clip is not None:
                    self._time_offset = int(self._time_offset / old * (self._clip.length / (self._num_steps * self._quantisation)))
        elif self._quantisation < 8:
            if self._clip is not None:
                if self._quantisation * self._num_steps < self._clip.length:
                    self._quantisation *= 2
                    self._time_offset = int(self._time_offset / old * (self._clip.length / (self._num_steps * self._quantisation)))
        self._send_selection(127)
        self._selection = [-1,
         -1,
         -1,
         -1]
        self._send_offsets()
        self.update()

    def _set_selection(self, sysex):
        self._selection = sysex.parse('bbbb')

    def _send_selection(self, x1 = 0, x2 = 0, y1 = 0, y2 = 0):
        sysex = LC2Sysex('SEQ_SEND_SELECTION')
        sysex.byte(x1)
        sysex.byte(x2)
        sysex.byte(y1)
        sysex.byte(y2)
        sysex.send()

    def _midi_action(self, sysex):
        acts = [self._arpeggiate,
         self._randomise_steps,
         self._duplicate,
         self._transpose,
         self._double,
         self._strum,
         self._flip,
         self._compress,
         self._harmonise,
         self._undo,
         self._move,
         self._clear,
         self._half]
        args = sysex.parse('bbbb')
        if args[0] < acts:
            acts[args[0]](args[1:])

    def _clear(self, args):
        if self._clip is not None:
            self._clip.select_all_notes()
            self._clip.replace_selected_notes(tuple())
            self.update()

    def _undo(self, args):
        self.song().undo()

    def _get_selection(self):
        time_lower = self._pos(self._selection[2])
        time_upper = self._pos(self._selection[3])
        pitch_upper = self._note(self._selection[0])
        pitch_lower = self._note(self._selection[1])
        selection = []
        remainder = []
        for note in self._note_cache:
            if note[0] >= pitch_lower and note[0] <= pitch_upper and note[1] >= time_lower and note[1] <= time_upper:
                selection.append(note)
            else:
                remainder.append(note)

        return [selection, remainder]

    def _in_selection(self, pos, pitch):
        sel, rem = self._get_selection()
        found = 0
        for note in sel:
            if pos == note[1] and pitch == note[0]:
                found = 1
                break

        return found

    def _arpeggiate(self, args):
        intervals = [0.125,
         0.25,
         0.5,
         1,
         2]
        idx, octaves, gate = args
        interval = intervals[idx]
        octaves += 1
        gate /= 127.0
        notes, left = self._get_selection()
        note = notes[0]
        new_notes = []
        steps = int((note[1] + note[2]) / interval)
        for step in range(steps):
            pitch = note[0] + step % octaves * 12
            new_notes.append([pitch,
             note[1] + step * interval,
             interval * gate,
             note[3],
             False])

        if self._clip is not None:
            self._clip.deselect_all_notes()
            self._clip.replace_selected_notes(tuple(new_notes))
            self._note_cache.extend(new_notes)

    def _duplicate(self, args):
        if self._clip is not None:
            new_notes = []
            for note in self._note_cache:
                new_notes.append([note[0],
                 note[1] + self._clip.length,
                 note[2],
                 note[3],
                 note[4]])

            self._clip.deselect_all_notes()
            self._clip.replace_selected_notes(tuple(new_notes))
            self._clip.loop_end += self._clip.length
            self._note_cache.extend(new_notes)
            self._send_offsets()

    def _double(self, args):
        if self._clip is not None:
            self._clip.loop_end += self._clip.length
            self._send_offsets()

    def _half(self, args):
        if self._clip is not None:
            self._clip.loop_end -= self._clip.length / 2
            if LC2Sysex.l9():
                if self._clip.end_marker > self._clip.loop_end:
                    self._clip.end_marker = self._clip.loop_end
            self._time_offset = 0
            self.update()
            self._send_offsets()

    def _move(self, args):
        dire = args[0] == 1 and 1 or -1
        selection, left = self._get_selection()
        for note in selection:
            note[1] = self._pos(self._step(note[1]) + dire)

        self._clip.select_all_notes()
        self._clip.replace_selected_notes(tuple(selection + left))
        self._selection[2] += dire
        self._selection[3] += dire
        self.update()

    def _transpose(self, args):
        if not self._fold_notes:
            pitch = args[0] == 1 and 1 or -1
            selection, left = self._get_selection()
            for note in selection:
                id = self._note_step(note[0])
                LC2Sysex.log_message('old ' + str(note[0]))
                note[0] = self._note(id + pitch)
                LC2Sysex.log_message('new ' + str(note[0]) + ' ' + str(id))

            self._clip.select_all_notes()
            self._clip.replace_selected_notes(tuple(selection + left))
            self._selection[0] += pitch
            self._selection[1] += pitch
            self.update()

    def _compress(self, args):
        sel, rem = self._get_selection()
        min = 99999
        for note in sel:
            if note[1] < min:
                min = note[1]

        for note in sel:
            LC2Sysex.log_message('before: ' + str(note))
            if not args[0]:
                note[1] = (note[1] - min) / 0.5 + min
                note[2] = note[2] / 0.5
            else:
                note[1] = (note[1] - min) * 0.5 + min
                note[2] = note[2] * 0.5
            LC2Sysex.log_message('after: ' + str(note))

        self._clip.select_all_notes()
        self._clip.replace_selected_notes(tuple(sel + rem))

    def _harmonise(self, args):
        if self._scale > 0:
            pass

    def _flip(self, args):
        dir = args[0]
        sel, rem = self._get_selection()
        LC2Sysex.log_message('Fliping ' + str(dir) + ' ' + str(sel) + ' ' + str(rem))
        if dir:
            if not self._fold_notes:
                min = 127
                max = 0
                for note in sel:
                    if note[0] > max:
                        max = note[0]
                    if note[0] < min:
                        min = note[0]

                cs = (self._note_step(max) - self._note_step(min)) / 2.0 + self._note_step(min)
                LC2Sysex.log_message(str(cs) + ' ' + str(self._note_step(max)) + ' ' + str(max) + ' ' + str(self._note_step(min)) + ' ' + str(min))
                for note in sel:
                    new_step = cs + (cs - self._note_step(note[0]))
                    note[0] = self._note(int(new_step))

                self._clip.select_all_notes()
                self._clip.replace_selected_notes(tuple(sel + rem))
        else:
            min = 99999
            max = -99999
            for note in sel:
                if note[1] > max:
                    max = note[1]
                if note[1] < min:
                    min = note[1]

            centre = (max - min) / 2 + min
            for note in sel:
                note[1] = centre + (centre - note[1])

            LC2Sysex.log_message('cent' + str(centre) + ' ' + str(min) + ' ' + str(max))
            self._clip.select_all_notes()
            self._clip.replace_selected_notes(tuple(sel + rem))

    def _strum(self, args):
        offset = 0.0625 / 2 * (args[0] / 127.0)
        sel, rem = self._get_selection()
        groups = {}
        for note in sel:
            if note[1] not in groups:
                groups[note[1]] = []
            groups[note[1]].append(note)

        for group in groups.itervalues():
            group.sort(lambda x, y: cmp(x[1::-1], y[1::-1]))
            for i, note in enumerate(group):
                note[1] += pow(i, 2) * offset

        self._clip.select_all_notes()
        self._clip.replace_selected_notes(tuple(sel + rem))

    def _randomise_steps(self, args):
        sel, rem = self._get_selection()
        notes = []
        for n in sel:
            if int(random.random() * 127) > 127 - args[0]:
                n[1] = self._pos(int(random.random() * (self._selection[3] - self._selection[2])) + self._selection[2])

        self._clip.select_all_notes()
        self._clip.replace_selected_notes(tuple(sel + rem))

    def _set_root_scale(self, sysex):
        self._root, self._scale = sysex.parse('bb')
        self.update()

    def _randomise_fader(self, sysex):
        u, l = sysex.parse('bb')
        for n in self._get_last_notes():
            if self._fader_type == 0:
                self._set_note_param(self._last_note, n[1], 3, int(random.random() * (u - l) + l))
            elif self._fader_type == 1:
                self._set_note_param(self._last_note, n[1], 2, pow(2, int((int(random.random() * (u - l) + l) - 64) / 11)))
            elif self._fader_type == 2:
                if random.random() > 0.5:
                    new = n[1] + int(random.random() * (u - l) + l) / 127.0 * (self._quantisation / 2)
                else:
                    new = n[1] - int(random.random() * (u - l) + l) / 127.0 * (self._quantisation / 2)
                self._set_note_param(self._last_note, n[1], 1, new)

        self.update()

    def _get_last_notes(self):
        notes = []
        for note in self._note_cache:
            if note[0] == self._last_note:
                notes.append(note)

        return notes

    def _set_quick_chord(self, sysex):
        self._quick_chord = sysex.parse('b')

    def _scroll_time(self, sysex):
        u, l = sysex.parse('bb')
        new = round(self._clip.length / (self._quantisation * self._num_steps) * u / 127.0, 4)
        new = round(new, 0)
        if new != self._time_offset:
            self._time_offset = new
            self.update()

    def _scroll_note(self, sysex):
        u, l = sysex.parse('bb')
        if u != self._note_offset:
            diff = u - self._note_offset
            self._last_note += diff
            self._note_offset = u
            self.update()

    def _fader_press(self, sysex):
        x, v = sysex.parse('bb')
        cur, act = self._get_fader(x)
        if self._fader_type == 0:
            if self._in_selection(act, self._last_note):
                if cur > 0:
                    pc = float(v) / float(cur)
                    sel, rem = self.f_get_selection()
                    for note in sel:
                        note[3] = min(127, note[3] * pc)

                    self._clip.select_all_notes()
                    self._clip.replace_selected_notes(tuple(sel + rem))
                    return
            id = 3
            val = v
        elif self._fader_type == 1:
            id = 2
            val = self._durations[int(round(v / 15.875, 0))]
        else:
            id = 1
            val = self._pos(x) + v / 127.0 * self._quantisation
        if not self._set_note_param(self._last_note, act, id, val):
            self.update()

    def _select_note(self, sysex):
        self._last_note = self._note(sysex.parse('b'))
        self.update()

    def _mute_note(self, sysex):
        y, state = sysex.parse('bb')
        pitch = self._note(y)
        self._mutes[pitch] = state
        found = 0
        for note in self._note_cache:
            if note[0] == pitch:
                found = 1
                note[4] = bool(state)

        if found:
            self._clip.select_all_notes()
            self._clip.replace_selected_notes(tuple(self._note_cache))
            self._clip.deselect_all_notes()

    def _note_press(self, sysex):
        x, y = sysex.parse('bb')
        pos = self._pos(x)
        pos2 = self._pos(x + 1)
        pitch = self._note(y)
        found = 0
        for note in self._note_cache:
            if note[1] >= pos and note[1] < pos2 and note[0] == pitch:
                LC2Sysex.log_message(str(note[1]) + ' ' + str(pos) + ' ' + str(pos2))
                found = 1

        if found:
            self.rem_note(pos, pos2, pitch)
        else:
            self.add_note(pos, pos2, pitch)

    def disconnect(self):
        self._unregister_timer_callback(self._on_timer)
        if self._clip is not None:
            try:
                if self._clip.playing_position_has_listener(self._on_playing_position_changed):
                    self._clip.remove_playing_position_listener(self._on_playing_position_changed)
                if self._clip.notes_has_listener(self._on_notes_changed):
                    self._clip.remove_notes_listener(self._on_notes_changed)
                for l in self._clisten:
                    chk = getattr(self._clip, l + '_has_listener')
                    if chk(self._on_length_changed):
                        rem = getattr(self._clip, 'remove_' + l + '_listener')
                        rem(self._on_length_changed)

            except:
                pass

        self._clip = None

    def on_enabled_changed(self):
        pass

    def _on_notes_changed(self):
        self._refresh = 5

    def _on_timer(self):
        if self._refresh > 0:
            if self._refresh == 1:
                self._cache_notes()
                self.update()
            self._refresh -= 1

    def add_note(self, pos, pos2, pitch):
        if self._clip is not None and pitch > -1:
            notes = []
            if self._quick_chord < 127:
                if self._scale == 0:
                    if self._quick_chord < len(self._chord_intervals):
                        for offset in self._chord_intervals[self._quick_chord]:
                            notes.append([pitch + offset,
                             pos,
                             self._quantisation * self._default_length,
                             self._default_velocity,
                             False])

                else:
                    for i in range(self._quick_chord + 3):
                        ns = self._note_step(pitch)
                        notes.append([self._note(ns + i * 2),
                         pos,
                         self._quantisation * self._default_length,
                         self._default_velocity,
                         False])

            elif self._last_details[1] >= pos and self._last_details[1] < pos2 and self._save_note:
                notes.append([pitch,
                 self._last_details[1],
                 self._last_details[2],
                 self._last_details[3],
                 self._mutes[pitch]])
                self._last_details = [-1,
                 -1,
                 -1,
                 -1,
                 -1]
            else:
                notes.append([pitch,
                 pos,
                 self._quantisation * self._default_length,
                 self._default_velocity,
                 self._mutes[pitch]])
            self._clip.deselect_all_notes()
            self._clip.replace_selected_notes(tuple(notes))
            self._note_cache.extend(notes)
            self._send_selection(127)
            self._selection = [-1,
             -1,
             -1,
             -1]
            self.update()

    def rem_note(self, pos, pos2, pitch):
        if self._clip is not None:
            new_notes = []
            for nt in self._note_cache:
                self._last_details = nt[0] == pitch and nt[1] >= pos and nt[1] < pos2 and nt
                continue
                new_notes.append(nt)

            self._clip.select_all_notes()
            self._clip.replace_selected_notes(tuple(new_notes))
            self._clip.deselect_all_notes()
            self._note_cache = new_notes
            if len(self._note_keys()) == 0:
                self._fold_notes = 0
            self.update()

    def update(self):
        array = [ 0 for i in range(self._height) ]
        array_l = [ 0 for i in range(self._height) ]
        for note in self._note_cache:
            step = self._step(note[1])
            nstep = self._note_step(note[0])
            if step in range(16) and nstep in range(self._height):
                array[self._height - 1 - nstep] |= 1 << step
                last = self._step(note[1] + note[2])
                for j in range(step + 1, min(last, 16)):
                    array_l[self._height - 1 - nstep] |= 1 << j

        sysex = LC2Sysex('STEPS')
        for b in array:
            sysex.int2(b)

        sysex.send()
        sysex = LC2Sysex('STEPS2')
        for b in array_l:
            sysex.int2(b)

        sysex.send()
        sysex = LC2Sysex('SEQ_FADERS')
        states = 0
        for i in range(16):
            fad = self._get_fader(i)[0]
            if fad == -1:
                sysex.byte(0)
            else:
                states |= 1 << i
                sysex.byte(fad)

        sysex.int2(states)
        sysex.send()
        self._get_timeline()
        self._get_note_line()
        sysex = LC2Sysex('SEQ_MUTES')
        mutes = 0
        for i in range(self._height):
            mutes |= self._mutes[self._note(i)] << self._height - 1 - i

        sysex.int2(mutes)
        sysex.send()
        sysex = LC2Sysex('SEQ_FOLD')
        sysex.byte(self._fold_notes)
        sysex.send()
        sysex = LC2Sysex('SEQ_QUANT')
        sysex.int(int(self._quantisation * 1000))
        LC2Sysex.log_message(str(int(self._quantisation * 1000)))
        sysex.send()
        sysex = LC2Sysex('SEQ_SAVE_NOTE')
        sysex.byte(self._save_note)
        sysex.send()

    def _send_offsets(self):
        sysex = LC2Sysex('SEQ_OFFSETS')
        if self._clip is not None:
            clen = self._clip.length
            if clen % 4 > 0:
                clen += 4 - clen % 4
            width = int(round(self._quantisation * self._num_steps))
            pc = width / clen * 127
            st = self._time_offset * self._quantisation * self._num_steps / clen * 127
            len = int(clen / (16 * self._quantisation))
            sysex.byte(len)
            sysex.byte(min(127, int(round(st))))
            sysex.byte(min(127, int(round(st + pc))))
            sysex.byte(min(127, self._note_offset))
            sysex.byte(min(127, self._note_offset + 11))
            sysex.send()

    def _get_fader(self, step):
        val = -1
        pos = -1
        for note in self._note_cache:
            if note[0] == self._last_note:
                if self._step(note[1]) == step:
                    pos = note[1]
                    if self._fader_type == 0:
                        val = note[3]
                    elif self._fader_type == 1:
                        val = int(round(self._nearest(self._durations, note[2]) * 15.875, 0))
                    else:
                        val = int(note[1] % self._quantisation / self._quantisation * 127)

        return [val, pos]

    def _nearest(self, list, val):
        for i, v in enumerate(list):
            if val <= v:
                return i

        return list[-1]

    def _pos(self, step):
        return self._time_offset * self._num_steps * self._quantisation + step * self._quantisation

    def _step(self, pos):
        return int((pos - self._time_offset * self._num_steps * self._quantisation) / self._quantisation)

    def _note_step(self, note):
        if self._scale == 0 and not self._fold_notes:
            return note - self._note_offset - self._root
        elif note in self._note_keys():
            return self._note_keys().index(note)
        else:
            start = 0 - self._note(0)
            below = [ self._note(i) for i in range(start, 0) ]
            end = 127 - self._note(self._height)
            above = [ self._note(i) for i in range(self._height, end) ]
            if note in below:
                return start + below.index(note)
            elif note in above:
                return self._height + above.index(note)
            else:
                return 16

    def _note(self, note_step):
        if self._fold_notes:
            notes = self._note_keys()
            if note_step < len(notes):
                return notes[note_step]
            else:
                return -1
        elif self._scale == 0:
            return min(self._note_offset, 115) + note_step + self._root
        else:
            offset = int(round(min(self._note_offset, 107) * (len(self._scales[self._scale]) / 12.0), 0))
            nid = (note_step + offset) % len(self._scales[self._scale])
            oid = int((note_step + offset) / len(self._scales[self._scale]))
            return self._root + self._scales[self._scale][nid] + 12 * oid

    def _note_keys(self):
        if self._fold_notes == 1:
            return sorted(dict(([note[0], 1] for note in self._note_cache)).keys())
        else:
            return [ self._note(i) for i in range(self._height) ]

    def _on_playing_position_changed(self):
        if self._clip is not None:
            step = self._step(self._clip.playing_position)
            if step != self._last_pos:
                if step not in range(16):
                    step = 16
                sysex = LC2Sysex('SEQ_POSITION')
                sysex.byte(step)
                sysex.send()
                self._last_pos = step

    def _set_note_param(self, pitch, start, param, val):
        found = 0
        for note in self._note_cache:
            if note[0] == pitch and note[1] == start:
                note[param] = val
                self._clip.select_all_notes()
                self._clip.replace_selected_notes(tuple(self._note_cache))
                self._clip.deselect_all_notes()
                found = 1

        return found

    def _get_timeline(self):
        sysex = LC2Sysex('SEQ_TIMELINE')
        for i in range(8):
            if self._clip != None:
                if self._pos(i * 2) < self._clip.length:
                    name = self._beat_time(self._pos(i * 2))
                    if name != self._ltime:
                        sysex.ascii(name)
                        self._ltime = name
                    else:
                        sysex.ascii('')
                else:
                    sysex.ascii('')
            else:
                sysex.ascii('')

        sysex.send()

    def _get_note_line(self):
        if self._fold_notes == 1:
            folded_notes = self._note_keys()
        sysex = LC2Sysex('SEQ_NOTELINE')
        for i in range(self._height - 1, -1, -1):
            if self._fold_notes == 1:
                if i < len(folded_notes):
                    sysex.ascii(self._to_note(folded_notes[i]))
                else:
                    sysex.ascii('')
            else:
                sysex.ascii(self._to_note(self._note(i)))

        sysex.send()

    def _beat_time(self, time):
        beats = int(time % 4)
        bars = int(time / 4)
        qb = int(time * 4 % 4)
        return str(bars + 1) + (self._quantisation < 2 and '.' + str(beats + 1) or '') + (self._quantisation < 0.5 and '.' + str(qb + 1) or '')

    def _to_note(self, note):
        notes = ['C',
         'C#',
         'D',
         'D#',
         'E',
         'F',
         'F#',
         'G',
         'G#',
         'A',
         'A#',
         'B']
        return notes[int(note % 12)] + str(int(note / 12) - 2)