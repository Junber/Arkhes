from __future__ import annotations
from tkinter import N, W, S, E, ttk, StringVar

from arkhesPlaylists import ArkhesPlaylists
import editor
from spotifyWrapper import spotify_wrapper

class ExportFrame:
	def __init__(self, root: ttk.Widget, owner: editor.Editor) -> None:
		self.owner = owner

		self.frame = ttk.Labelframe(root, text='Export', padding='5 5 5 5')
		self.export_name = StringVar()
		self.export_name_entry = ttk.Entry(self.frame, textvariable=self.export_name)
		self.export_name_entry.grid(column=0, row=0, sticky=(S, N, W, E))
		self.export_button = ttk.Button(self.frame, text='Export current playlist', command=self.export_current_playlist)
		self.export_button.grid(column=0, row=1, sticky=(S, N, W, E))
		self.frame.columnconfigure(0, weight=1)

	def grid(self, **args) -> None:
		self.frame.grid(args)

	def export_current_playlist(self) -> None:
		spotify_wrapper.export_playlist(ArkhesPlaylists.get_playlist(self.owner.get_current_name()), self.export_name.get())

	def save_dict(self) -> dict:
		return {'name' : self.export_name.get()}

	def load_from(self, dct: dict) -> None:
		self.export_name.set(dct['name'])
