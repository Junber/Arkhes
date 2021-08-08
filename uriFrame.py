from tkinter import N, W, S, E, ttk, messagebox

from utils import Utils
from playlistNameEntry import PlaylistNameEntry
from spotifyWrapper import spotify_wrapper

class UriFrame:
	def __init__(self, root, editor):
		self.editor = editor

		self.frame = ttk.Labelframe(root, text='URI', padding='5 5 5 5')
		self.frame.columnconfigure(0, weight=1)
		self.uri_name_entry = PlaylistNameEntry(self.frame, lambda *args: args)
		self.uri_name_entry.grid(column=0, row=0, columnspan=2, sticky=(N, S, W, E))
		self.uri_name_entry.bind_return(self.add_uri)
		ttk.Button(self.frame, text='Add', command=self.add_uri).grid(column=0, row=1, sticky=(S, N, W, E))
	
	def grid(self, **args):
		self.frame.grid(args)

	def add_uri(self):
		object = spotify_wrapper.get_resource(self.uri_name_entry.get())
		if len(object) == 0:
			messagebox.showinfo(message='Invalid URI')
			return
		self.editor.add_uri(object['uri'])