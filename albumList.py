from spotipy.client import Spotify
from spotifyWrapper import SpotifyWrapper, spotify_wrapper
from utils import Utils
from tkinter import N, W, S, E, ttk
from pathlib import Path

class AlbumList:
	def __init__(self, parent, owner, name, album_clicked_callback, extra_callbacks=[]) -> None:
		self.albums_frame = ttk.Labelframe(parent, text=name, padding='4 5 4 5')
		self.album_clicked_callback = album_clicked_callback
		self.extra_callbacks = extra_callbacks

		self.albums_frame.columnconfigure(0, weight=1)
		
		self.owner = owner
	
	def grid(self, **args):
		self.albums_frame.grid(args)
	
	def prefix(self):
		return spotify_wrapper.prefix

	def resource_type(self):
		return spotify_wrapper.resource_type
	
	def get_album(self, i, resource):
		album = spotify_wrapper.get_resource(resource)
		
		album['playlistLine'] = resource
		album['lineNumber'] = i
		return album
	
	def get_albums_from_file(self, filename):
		lines = Utils.get_lines_from_file(filename)
		
		spotify_wrapper.cache_uncached_albums(lines)
		uris = [self.get_album(i, line) for i, line in enumerate(lines)]

		return uris
	
	def add_button(self, i, album, albumNum):
		button = ttk.Button(self.albums_frame, text=album['name'], style=album['type']+'.TButton')
		button.configure(command = lambda album=album: self.album_clicked_callback(album))
		button.grid(column = 0, row = i, sticky = (W, E))
		button.grid_configure(padx=1, pady=1)

		for extraButtonIndex, extra in enumerate(self.extra_callbacks):
			extraButton = ttk.Button(self.albums_frame, text=extra[0], style=album['type']+'.TButton', width=len(extra[0]) + 2)
			extraButton.configure(command = (lambda callback : lambda album=album: callback(album))(extra[1]))
			extraButton.grid(column = extraButtonIndex + 1, row = i, sticky = (W, E))
			extraButton.grid_configure(padx=1, pady=1)
			if len(extra) > 2 and not extra[2](album, albumNum):
				extraButton.state(['disabled'])
	
	def add_buttons(self, albums):
		for i, album in enumerate(albums):
			self.add_button(i, album, len(albums))
	
	def update(self, path):
		for child in self.albums_frame.winfo_children(): 
			child.destroy()

		if Path(path).is_file():
			self.add_buttons(self.get_albums_from_file(path))
	
	def update_with_saved_albums(self, page, categorization_mode):
		for child in self.albums_frame.winfo_children(): 
			child.destroy()

		self.add_buttons(spotify_wrapper.saved_albums(page, categorization_mode))