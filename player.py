import random

from tkinter import N, W, S, E, ttk
import tkinter

from spotifyWrapper import SpotifyWrapper, spotify_wrapper
from utils import Utils
from albumList import AlbumList
from currentPlaylistFrame import CurrentPlaylistFrame
from currentPlaybackFrame import CurrentPlaybackFrame

class Player:
	def __init__(self, root):
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

		self.album_list = AlbumList(root, self, 'Contents', self.clicked_album)
		self.album_list.grid(column=1, row=0, rowspan=3, sticky=(N, W, E, S))

		self.current_playback_frame = CurrentPlaybackFrame(self.root)
		self.current_playback_frame.grid(column=0, row=3, columnspan=2, sticky=(N, S, W, E))

		for thing in [root, shuffle_frame]:
			for child in thing.winfo_children(): 
				child.grid_configure(padx=5, pady=5)
		
		root.columnconfigure(0, weight=1)
		root.columnconfigure(1, weight=2)

		self.name_changed()
	
	def save_dict(self):
		return {'track_shuffle' : self.track_shuffle.get(), 'album_shuffle' : self.album_shuffle.get(), 'current' : self.current_playlist_frame.save_dict(), 'volume' : self.current_playback_frame.volume.get()}
	
	def load_from(self, dct):
		self.track_shuffle.set(dct['track_shuffle'])
		self.album_shuffle.set(dct['album_shuffle'])
		self.current_playlist_frame.load_from(dct['current'])
		self.current_playback_frame.volume.set(dct['volume'])
		
		self.name_changed()
	
	def get_uris(self, resource):
		uris = []
		if SpotifyWrapper.is_album(resource):
			tracks = spotify_wrapper.get_resource(resource)['tracks']['items']
			uris = [track['uri'] for track in tracks]
			if not self.album_shuffle.get() and self.track_shuffle.get():
				random.shuffle(uris)
			uris = [uris]
		elif SpotifyWrapper.is_arkhes_playlist(resource):
			path = Utils.path_for(resource[len(spotify_wrapper.prefix):].strip())
			uris = self.get_uris_from_file(path)
		elif SpotifyWrapper.is_song(resource):
			uris = [[resource]]
		elif SpotifyWrapper.is_spotify_playlist(resource):
			tracks = spotify_wrapper.get_resource(resource)['tracks']['items']
			uris = [item['track']['uri'] for item in tracks]
			if not self.album_shuffle.get() and self.track_shuffle.get():
				random.shuffle(uris)
			uris = [uris]
		
		return uris
	
	def get_uris_from_file(self, filename):
		lines = Utils.get_lines_from_file(filename)		
		spotify_wrapper.cache_uncached_albums(lines)
		return Utils.flatten([self.get_uris(line) for line in lines])

	def get_uris_from_file_and_shuffle(self, filename):
		uris = self.get_uris_from_file(filename)

		if self.album_shuffle.get() and not self.track_shuffle.get():
			random.shuffle(uris)
		
		return uris
	
	def flatten_uris(self, uris):
		uris = Utils.flatten(uris)

		if self.album_shuffle.get() and self.track_shuffle.get():
			random.shuffle(uris)
		
		return uris
	
	def get_path(self):
		return self.current_playlist_frame.name_entry.get_path()
	
	def play(self, *args):
		self.current_playback = self.get_uris_from_file_and_shuffle(self.get_path())
		uris = self.flatten_uris(self.current_playback)
		if len(uris) > 0:
			spotify_wrapper.play_uris(uris)
	
	def clicked_album(self, album):
		if album['type'] == spotify_wrapper.resource_type:
			self.current_playlist_frame.save_current_position()
			self.current_playlist_frame.name_entry.set(album['name'])
		else:
			spotify_wrapper.shuffle(self.track_shuffle.get())
			spotify_wrapper.play(album['uri'])

	def name_changed(self, *args):
		self.album_list.set_items_with_path(self.get_path())
	
	def changed_shuffle(self, *args):
		if self.album_shuffle.get() and self.track_shuffle.get():
			self.go_back_album_button.state(['disabled'])
			self.go_forward_album_button.state(['disabled'])
		else:
			self.go_back_album_button.state(['!disabled'])
			self.go_forward_album_button.state(['!disabled'])
	
	def set_active(self, new_active):
		self.current_playback_frame.set_active(new_active)

