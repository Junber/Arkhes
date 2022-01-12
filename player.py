import random

from tkinter import N, W, S, E, ttk
import tkinter

from resources import ArkhesResource
from spotifyWrapper import spotify_wrapper
from arkhesPlaylists import ArkhesPlaylists
from resourceList import ResourceList
from currentPlaylistFrame import CurrentPlaylistFrame
import currentPlaybackFrame

class Player:
	def __init__(self, root: ttk.Widget) -> None:
		self.current_playback = []
		self.current_playback_album_position = 0
		self.current_playback_track_position = 0
		self.root = root

		self.current_playlist_frame = CurrentPlaylistFrame(root, self)
		self.current_playlist_frame.grid(column=0, row=0, sticky=(N, W, E))

		ttk.Button(root, text='Play', command=self.play).grid(column=0, row=2, sticky=(N, W, E))

		self.track_shuffle = tkinter.BooleanVar(value=False)
		self.album_shuffle = tkinter.BooleanVar(value=False)
		shuffle_frame = ttk.Frame(root)
		shuffle_frame.grid(column=0, row=1, sticky=(W, E, S))
		ttk.Checkbutton(shuffle_frame, text='Track-Shuffle', variable=self.track_shuffle, command=self.changed_shuffle).grid(column=0, row=0, sticky=(N, S, W, E))
		ttk.Checkbutton(shuffle_frame, text='Album-Shuffle', variable=self.album_shuffle, command=self.changed_shuffle).grid(column=1, row=0, sticky=(N, S, W, E))

		self.album_list = ResourceList(root, self, 'Contents', 10, self.clicked_album)
		self.album_list.grid(column=1, row=0, rowspan=3, sticky=(N, W, E, S))

		self.current_playback_frame = currentPlaybackFrame.CurrentPlaybackFrame(self.root, self, 320)
		self.current_playback_frame.grid(column=0, row=3, columnspan=2, sticky=(N, S, W, E))

		for thing in [root, shuffle_frame]:
			for child in thing.winfo_children():
				child.grid_configure(padx=5, pady=5)

		root.columnconfigure(0, weight=1)
		root.columnconfigure(1, weight=2)

		self.name_changed()

	def save_dict(self) -> dict:
		return {
			'track_shuffle' : self.track_shuffle.get(),
			'album_shuffle' : self.album_shuffle.get(),
			'current' : self.current_playlist_frame.save_dict(),
			'volume' : self.current_playback_frame.volume.get(),
			'album_list' : self.album_list.save_dict()
			}

	def load_from(self, dct: dict) -> None:
		self.track_shuffle.set(dct['track_shuffle'])
		self.album_shuffle.set(dct['album_shuffle'])
		self.current_playlist_frame.load_from(dct['current'])
		self.current_playback_frame.volume.set(dct['volume'])
		self.album_list.load_from(dct['album_list'])

		self.name_changed()

	def get_playlist_and_shuffle(self, playlist: ArkhesResource) -> list:
		uris = playlist.track_uris()

		if self.album_shuffle.get():
			random.shuffle(uris)
		if self.track_shuffle.get():
			for uri_list in uris:
				random.shuffle(uri_list)

		return uris

	def flatten_uris(self, uris: list) -> list:
		uris = ArkhesResource.flatten(uris)

		if self.album_shuffle.get() and self.track_shuffle.get():
			random.shuffle(uris)

		return uris

	def get_name(self) -> str:
		return self.current_playlist_frame.name_entry.get()

	def play(self, *_) -> None:
		self.current_playback = self.get_playlist_and_shuffle(ArkhesPlaylists.get_playlist(self.get_name()))
		self.current_playback_album_position = 0
		self.current_playback_track_position = 0
		uris = self.flatten_uris(self.current_playback)
		if len(uris) > 0:
			spotify_wrapper.play_uris(uris)

	def clicked_album(self, album: ArkhesResource) -> None:
		if album.type() == spotify_wrapper.resource_type:
			self.current_playlist_frame.save_current_position()
			self.current_playlist_frame.name_entry.set(album.name())
		else:
			spotify_wrapper.shuffle(self.track_shuffle.get())
			spotify_wrapper.play(album.uri())

	def name_changed(self, *_) -> None:
		self.album_list.set_items_with_path(self.get_name())

	def changed_shuffle(self, *_) -> None:
		self.current_playback_frame.set_album_navigation_enabled(not (self.album_shuffle.get() and self.track_shuffle.get()))

	def set_active(self, new_active: bool) -> None:
		self.current_playback_frame.set_active(new_active)

	def update_playback_position(self, current_song_uri: str) -> None:
		while self.current_playback_album_position < len(self.current_playback):
			while self.current_playback_track_position < len(self.current_playback[self.current_playback_album_position]):
				if self.current_playback[self.current_playback_album_position][self.current_playback_track_position] == current_song_uri:
					return
				self.current_playback_track_position += 1

			self.current_playback_track_position = 0
			self.current_playback_album_position += 1

	def tracks_to_next_album(self) -> int:
		if self.current_playback_album_position >= len(self.current_playback):
			return 1
		return len(self.current_playback[self.current_playback_album_position]) - self.current_playback_track_position

	def tracks_to_previous_album(self) -> int:
		if self.current_playback_album_position >= len(self.current_playback):
			return 1
		return self.current_playback_track_position + 1
