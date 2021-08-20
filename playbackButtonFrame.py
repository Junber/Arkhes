import tkinter
from tkinter import N, W, S, E, ttk

from spotifyWrapper import spotify_wrapper
from tooltip import CreateToolTip

class PlaybackButtonFrame:
	def __init__(self, root):
		self.frame = ttk.Frame(root)

		self.go_back_album_button = ttk.Button(self.frame, text='<<', command=self.go_back_album)
		self.go_back_album_button.grid(column=0, row=0)
		CreateToolTip(self.go_back_album_button, "Go to previous album")

		ttk.Button(self.frame, text='<', command=self.go_back_track).grid(column=1, row=0)
		self.current_track_name = tkinter.StringVar(value='[No playback started from here]')
		self.current_track_button = ttk.Button(self.frame, textvariable=self.current_track_name, command=self.pause)
		self.current_track_button.grid(column=2, row=0, sticky=(N, S, W, E))
		CreateToolTip(self.current_track_button, "Click to pause/resume playback")

		ttk.Button(self.frame, text='>', command=self.go_forward_track).grid(column=3, row=0)
		self.go_forward_album_button = ttk.Button(self.frame, text='>>', command=self.go_forward_album)
		self.go_forward_album_button.grid(column=4, row=0)
		CreateToolTip(self.go_forward_album_button, "Go to next album")

		self.frame.columnconfigure(2, weight=1)
	
	def grid(self, **args):
		self.frame.grid(args)
	
	def set_album_navigation_enabled(self, state):
		if state:
			self.go_back_album_button.state(['!disabled'])
			self.go_forward_album_button.state(['!disabled'])
		else:
			self.go_back_album_button.state(['disabled'])
			self.go_forward_album_button.state(['disabled'])

	def go_back_album(self, *args):
		pass # TODO

	def go_forward_album(self, *args):
		pass # TODO

	def go_back_track(self, *args):
		spotify_wrapper.go_back_track()

	def go_forward_track(self, *args):
		spotify_wrapper.go_forward_track()
	
	def pause(self, *args):
		spotify_wrapper.toggle_pause()