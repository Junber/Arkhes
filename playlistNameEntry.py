from tkinter import ttk
import tkinter
from utils import Utils

class PlaylistNameEntry:
	def __init__(self, root, changed_callback):
		self.playlist_name = tkinter.StringVar()
		self.playlist_name.trace_add('write', changed_callback)

		self.playlist_name_entry = ttk.Entry(root, width=7, textvariable=self.playlist_name)
		self.playlist_name_entry.focus()

	def grid(self, **args):
		self.playlist_name_entry.grid(args)

	def bind_return(self, func):
		self.playlist_name_entry.bind('<Return>', (lambda _: func()))
	
	def set(self, name):
		self.playlist_name.set(name)
		
	def get(self):
		return self.playlist_name.get()

	def get_path(self):
		return Utils.path_for(self.get())
