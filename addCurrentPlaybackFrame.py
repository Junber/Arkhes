from tkinter import N, W, S, E, ttk, messagebox

from utils import Utils
from spotifyWrapper import spotify_wrapper

class AddCurrentPlaybackFrame:
	def __init__(self, root, editor):
		self.editor = editor

		self.frame = ttk.Labelframe(root, text='Current Playback', padding='5 5 5 5')
		self.frame.columnconfigure(0, weight=1)
		ttk.Button(self.frame, text='Add current song', command=self.add_song).grid(column=0, row=0, sticky=(S, N, W, E))
		ttk.Button(self.frame, text='Add current album', command=self.add_album).grid(column=0, row=1, sticky=(S, N, W, E))
		ttk.Button(self.frame, text='Add current context', command=self.add_context).grid(column=0, row=2, sticky=(S, N, W, E))
	
	def grid(self, **args):
		self.frame.grid(args)

	def add_song(self):
		self.editor.add_album(spotify_wrapper.get_current_playback()['item'])
	
	def add_album(self):
		self.editor.add_album(spotify_wrapper.get_current_playback()['item']['album'])
	
	def add_context(self):
		self.editor.add_album(spotify_wrapper.get_current_playback()['context'])