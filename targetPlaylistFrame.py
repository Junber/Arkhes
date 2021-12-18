from tkinter import N, W, S, E, ttk

from arkhesPlaylists import ArkhesPlaylists
from playlistNameEntry import PlaylistNameEntry
from spotifyWrapper import spotify_wrapper

class TargetPlaylistFrame:
	def __init__(self, root, editor):
		self.editor = editor

		self.frame = ttk.Labelframe(root, text='Target', padding='5 5 5 5')

		self.name_entry = PlaylistNameEntry(self.frame, lambda *_: _)
		self.name_entry.grid(column=0, row=0, columnspan=2, sticky=(N, S, W, E))
		self.name_entry.bind_return(self.add_playlist)
		self.frame.columnconfigure(0, weight=1)
		self.frame.columnconfigure(1, weight=1)
		ttk.Button(self.frame, text='Add', command=self.add_playlist).grid(column=0, row=1, sticky=(S, N, W, E))
		ttk.Button(self.frame, text='Rename', command=self.rename_playlist).grid(column=1, row=1, sticky=(S, N, W, E))

	def grid(self, **args):
		self.frame.grid(args)

	def add_playlist(self):
		item = spotify_wrapper.get_resource(spotify_wrapper.resource_type + ':' + self.name_entry.get())
		ArkhesPlaylists.add_item_to_playlist(self.editor.get_current_name(), item)
		self.editor.name_changed()

	def rename_playlist(self):
		ArkhesPlaylists(self.editor.get_current_name(), self.name_entry.get())
		self.editor.name_changed()
