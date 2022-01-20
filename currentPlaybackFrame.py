from __future__ import annotations
import tkinter
from tkinter import N, W, S, E, ttk, HORIZONTAL
import editor
import player

from spotifyWrapper import spotify_wrapper
from playbackButtonFrame import PlaybackButtonFrame

class CurrentPlaybackFrame:
	def __init__(self, root: tkinter.Widget, master : player.Player | editor.Editor, cover_size):
		self.cover_size = cover_size
		self.root = root
		self.master = master
		self.active = True

		self.frame = ttk.Labelframe(root, text='Current Playback', padding='5 5 5 5')

		self.album_cover_label = ttk.Label(self.frame, anchor='center')
		self.album_cover_label.grid(column=0, row=0, rowspan=5, sticky=(N, S, W, E))
		self.set_cover(spotify_wrapper.get_image('no_cover.jpg', self.cover_size))

		# TODO: Save album and artist to recover on start-up
		self.current_album_name = tkinter.StringVar(value='[Album]')
		self.current_album_label = ttk.Label(self.frame, textvar=self.current_album_name, anchor='center')
		self.current_album_label.grid(column=1, row=1, sticky=(S, W, E))

		self.current_artist_name = tkinter.StringVar(value='[Artist]')
		self.current_artist_label = ttk.Label(self.frame, textvar=self.current_artist_name, anchor='center')
		self.current_artist_label.grid(column=1, row=2, sticky=(S, W, E))

		self.playback_button_frame = PlaybackButtonFrame(self.frame, self.master)
		self.playback_button_frame.grid(column=1, row=3, sticky=(S, W, E))

		self.current_track_progress_frame = tkinter.Frame(self.frame)
		self.current_track_progress_frame.grid(column=1, row=4, sticky=(S, W, E))
		self.current_track_progress = tkinter.IntVar(value=0)
		self.current_track_progress_string = tkinter.StringVar(value ='[Time]')
		self.total_track_time_string = tkinter.StringVar(value ='[Time]')
		tkinter.Label(self.current_track_progress_frame, textvariable=self.current_track_progress_string)\
			.grid(column=0, row=0, sticky=(N, S, W, E))

		self.current_track_progress_scale = ttk.Scale(self.current_track_progress_frame, orient=HORIZONTAL,
			variable=self.current_track_progress, command=self.changed_track_progress)

		self.current_track_progress_scale.grid(column=1, row=0, sticky=(N, S, W, E))
		tkinter.Label(self.current_track_progress_frame, textvariable=self.total_track_time_string)\
			.grid(column=2, row=0, sticky=(N, S, W, E))

		self.build_volume_frame()
		self.volume_frame.grid(column=1, row=0, sticky=(S, W, E))

		self.frame.columnconfigure(1, weight=1)
		self.frame.rowconfigure(0, weight=1)
		self.current_track_progress_frame.columnconfigure(1, weight=1)

		for thing in [self.frame, self.volume_frame]:
			for child in thing.winfo_children():
				child.grid_configure(padx=5, pady=5)

		self.current_playback = []
		self.update_current_track_loop()


	def build_volume_frame(self):
		self.volume_frame = ttk.Frame(self.frame)
		ttk.Label(self.volume_frame, text='Volume').grid(column=0, row=0, sticky=(N, S, W, E))
		self.volume = tkinter.IntVar()
		ttk.Scale(self.volume_frame, orient=HORIZONTAL, variable=self.volume, to=100, command=self.changed_volume)\
			.grid(column=1, row=0, sticky=(N, S, W, E))

	def grid(self, **args):
		self.frame.grid(args)

	def grid_forget(self):
		self.frame.grid_forget()

	def set_cover(self, img):
		self.album_cover_label.configure(image = img)
		self.image = img

	def changed_volume(self, *_):
		spotify_wrapper.set_volume(self.volume.get())

	def changed_track_progress(self, *_):
		spotify_wrapper.set_track_progress(self.current_track_progress.get())

	def update_current_track(self):
		if not self.active:
			return

		playback = spotify_wrapper.get_current_playback()
		if playback is not None and not playback.is_none():
			self.current_track_progress.set(playback.progress_ms()) # TODO: Make smoother
			self.current_track_progress_string.set(str(playback.progress()))
			self.volume.set(playback.volume())

			name = playback.name()
			if name != self.get_current_track_name():
				self.master.update_playback_position(playback.uri())
				self.current_track_progress_scale.configure(to=playback.duration_ms())
				self.total_track_time_string.set(playback.duration())
				album = playback.album()
				self.set_current_track_name(name)

				album_string = f'Album: {album.name()} (Track: {playback.track_number()}/{album.number_of_tracks()})'
				self.current_album_name.set(album_string)
				self.current_artist_name.set('Artist: ' + playback.artist().name())
				self.set_cover(spotify_wrapper.get_album_cover(album, self.cover_size))

	def get_current_track_name(self):
		return self.playback_button_frame.current_track_name.get()

	def set_current_track_name(self, value):
		return self.playback_button_frame.current_track_name.set(value)

	def update_current_track_loop(self):
		self.update_current_track()
		self.root.after(1000, self.update_current_track_loop)

	def set_active(self, new_active):
		if not self.active and new_active:
			self.update_current_track()
		self.active = new_active

	def set_album_navigation_enabled(self, state):
		self.playback_button_frame.set_album_navigation_enabled(state)
