from __future__ import annotations
from tkinter import N, W, S, E, ttk, messagebox
import tkinter

from playlistNameEntry import PlaylistNameEntry
from spotifyWrapper import spotify_wrapper
import editor

class UriFrame:
	def __init__(self, root: tkinter.Widget, owner: editor.Editor) -> None:
		self.owner = owner

		self.frame = ttk.Labelframe(root, text='URI', padding='5 5 5 5')
		self.frame.columnconfigure(0, weight=1)
		self.uri_name_entry = PlaylistNameEntry(self.frame, lambda *_: _)
		self.uri_name_entry.grid(column=0, row=0, columnspan=2, sticky=(N, S, W, E))
		self.uri_name_entry.bind_return(self.add_uri)
		ttk.Button(self.frame, text='Add', command=self.add_uri).grid(column=0, row=1, sticky=(S, N, W, E))

	def grid(self, **args) -> None:
		self.frame.grid(args)

	def grid_forget(self) -> None:
		self.frame.grid_forget()

	def add_uri(self) -> None:
		resource = spotify_wrapper.get_resource(self.uri_name_entry.get())
		if len(resource) == 0:
			messagebox.showinfo(message='Invalid URI')
			return
		self.owner.add_uri(resource.uri())
