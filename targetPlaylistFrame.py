from pathlib import Path
import os

from tkinter import N, W, S, E, ttk, messagebox

from utils import Utils
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
		Utils.add_line_to_file(self.editor.get_current_path(), spotify_wrapper.resource_type + ':' + self.name_entry.get())		
		self.editor.name_changed()
	
	def rename_playlist(self):
		if Path(self.name_entry.get_path()).is_file():
			messagebox.showinfo(message='Playlist already exists')
		else:
			os.rename(self.editor.get_current_path(), self.name_entry.get_path())
			self.editor.name_changed()