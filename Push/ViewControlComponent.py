#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/ViewControlComponent.py
import Live
NavDirection = Live.Application.Application.View.NavDirection
from _Framework.CompoundComponent import CompoundComponent
from _Framework.Dependency import depends
from _Framework.ScrollComponent import ScrollComponent, Scrollable
from _Framework.Util import in_range
from SpecialMixerComponent import tracks_to_use_from_song
VIEWS = ('Browser', 'Arranger', 'Session', 'Detail', 'Detail/Clip', 'Detail/DeviceChain')

class _DeltaSongScroller(Scrollable):

    @depends(song=None)
    def __init__(self, song = None, *a, **k):
        super(_DeltaSongScroller, self).__init__(*a, **k)
        self._song = song

    _do_scroll = NotImplemented
    _can_scroll = NotImplemented

    def scroll_up(self):
        if self.can_scroll_up():
            self._do_scroll(-1)

    def scroll_down(self):
        if self.can_scroll_down():
            self._do_scroll(1)

    def can_scroll_up(self):
        return self._can_scroll(-1)

    def can_scroll_down(self):
        return self._can_scroll(1)


def tracks_to_use(song):
    return list(tracks_to_use_from_song(song) + (song.master_track,))


def next_item(seq, item, delta):
    return seq[list(seq).index(item) + delta]


def has_next_item(seq, item, delta):
    try:
        return in_range(list(seq).index(item) + delta, 0, len(seq))
    except ValueError:
        return False


class TrackScroller(_DeltaSongScroller):

    def _do_scroll(self, delta):
        song = self._song
        tracks = tracks_to_use(song)
        track = next_item(tracks, song.view.selected_track, delta)
        song.view.selected_track = track
        if track.can_be_armed:
            playing_slot_index = track.playing_slot_index
            if playing_slot_index >= 0 and track.clip_slots[playing_slot_index].clip:
                song.view.highlighted_clip_slot = track.clip_slots[playing_slot_index]

    def _can_scroll(self, delta):
        tracks = tracks_to_use(self._song)
        try:
            return has_next_item(tracks, self._song.view.selected_track, delta)
        except ValueError:
            return False


class BasicSceneScroller(_DeltaSongScroller):

    def _do_scroll(self, delta):
        song = self._song
        view = song.view
        view.selected_scene = next_item(song.scenes, view.selected_scene, delta)

    def _can_scroll(self, delta):
        song = self._song
        view = song.view
        return has_next_item(song.scenes, view.selected_scene, delta)


class SceneScroller(BasicSceneScroller):

    def _do_scroll(self, delta):
        super(SceneScroller, self)._do_scroll(delta)
        if self._song.view.highlighted_clip_slot != None:
            if self._song.view.highlighted_clip_slot.has_clip:
                self._song.view.highlighted_clip_slot.fire(force_legato=True, launch_quantization=Live.Song.Quantization.q_no_q)
            else:
                self._song.view.selected_track.stop_all_clips(False)


class SceneListScroller(BasicSceneScroller):

    def _do_scroll(self, delta):
        super(SceneListScroller, self)._do_scroll(delta)
        self._song.view.selected_scene.fire(force_legato=True, can_select_scene_on_launch=False)


class ViewControlComponent(CompoundComponent):
    """
    Component that can toggle the device chain- and clip view of the
    selected track
    """

    def __init__(self, *a, **k):
        super(ViewControlComponent, self).__init__(*a, **k)
        self._scroll_tracks, self._scroll_scene_list, self._scroll_scenes = self.register_components(ScrollComponent(TrackScroller()), ScrollComponent(SceneListScroller()), ScrollComponent(SceneScroller()))
        song = self.song()
        view = song.view
        self.register_slot(song, self._scroll_tracks.update, 'visible_tracks')
        self.register_slot(song, self._scroll_tracks.update, 'return_tracks')
        self.register_slot(song, self._scroll_scenes.update, 'scenes')
        self.register_slot(song, self._scroll_scene_list.update, 'scenes')
        self.register_slot(view, self._scroll_tracks.update, 'selected_track')
        self.register_slot(view, self._scroll_scenes.update, 'selected_scene')
        self.register_slot(view, self._scroll_scene_list.update, 'selected_scene')

    def set_next_track_button(self, button):
        self._scroll_tracks.set_scroll_down_button(button)

    def set_prev_track_button(self, button):
        self._scroll_tracks.set_scroll_up_button(button)

    def set_next_scene_button(self, button):
        self._scroll_scenes.set_scroll_down_button(button)

    def set_prev_scene_button(self, button):
        self._scroll_scenes.set_scroll_up_button(button)

    def set_next_scene_list_button(self, button):
        self._scroll_scene_list.set_scroll_down_button(button)

    def set_prev_scene_list_button(self, button):
        self._scroll_scene_list.set_scroll_up_button(button)

    def show_view(self, view):
        raise view in VIEWS or AssertionError
        app_view = self.application().view
        try:
            if view == 'Detail/DeviceChain' or 'Detail/Clip':
                if not app_view.is_view_visible('Detail'):
                    app_view.show_view('Detail')
            if not app_view.is_view_visible(view):
                app_view.show_view(view)
        except RuntimeError:
            pass

    def focus_view(self, view):
        if not view in VIEWS:
            raise AssertionError
            app_view = self.application().view
            if view == 'Detail/DeviceChain' or 'Detail/Clip':
                if not app_view.is_view_visible('Detail'):
                    app_view.show_view('Detail')
            app_view.is_view_visible(view) or app_view.focus_view(view)