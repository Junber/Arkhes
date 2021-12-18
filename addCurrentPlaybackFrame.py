from tkinter import N, W, S, E, ttk

from spotifyWrapper import spotify_wrapper

class AddCurrentPlaybackFrame:
	def __init__(self, root, editor):
		self.editor = editor

		self.frame = ttk.Labelframe(root, text='Current Playback', padding='5 5 5 5')
		self.frame.columnconfigure(0, weight=1)
		self.frame.columnconfigure(1, weight=1)

		self.add_frame = ttk.Labelframe(self.frame, text='Add', padding='5 5 5 5')
		self.add_frame.grid(column=0, row=0, sticky=(S, N, W, E))
		self.add_frame.columnconfigure(0, weight=1)
		ttk.Button(self.add_frame, text='Song', command=self.add_song).grid(column=0, row=0, sticky=(S, N, W, E))
		ttk.Button(self.add_frame, text='Album', command=self.add_album).grid(column=0, row=1, sticky=(S, N, W, E))
		ttk.Button(self.add_frame, text='Artist', command=self.add_artist).grid(column=0, row=2, sticky=(S, N, W, E))
		ttk.Button(self.add_frame, text='Context', command=self.add_context).grid(column=0, row=3, sticky=(S, N, W, E))

		self.open_frame = ttk.Labelframe(self.frame, text='Open', padding='5 5 5 5')
		self.open_frame.grid(column=1, row=0, sticky=(S, N, W, E))
		self.open_frame.columnconfigure(0, weight=1)
		open_song_button = ttk.Button(self.open_frame, text='Song', command=self.open_song)
		open_song_button.grid(column=0, row=0, sticky=(S, N, W, E))
		open_song_button.state(['disabled'])
		ttk.Button(self.open_frame, text='Album', command=self.open_album).grid(column=0, row=1, sticky=(S, N, W, E))
		ttk.Button(self.open_frame, text='Artist', command=self.open_artist).grid(column=0, row=2, sticky=(S, N, W, E))
		ttk.Button(self.open_frame, text='Context', command=self.open_context).grid(column=0, row=3, sticky=(S, N, W, E))

	def grid(self, **args):
		self.frame.grid(args)


	def add_song(self):
		self.editor.add_item(spotify_wrapper.get_current_playback().song())

	def add_album(self):
		self.editor.add_item(spotify_wrapper.get_current_playback().album())

	def add_artist(self):
		self.editor.add_item(spotify_wrapper.get_current_playback().artist())

	def add_context(self):
		self.editor.add_item(spotify_wrapper.get_current_playback().context())


	def open_song(self):
		self.editor.open_item(spotify_wrapper.get_current_playback().song())

	def open_album(self):
		self.editor.open_item(spotify_wrapper.get_current_playback().album())

	def open_artist(self):
		self.editor.open_item(spotify_wrapper.get_current_playback().artist())

	def open_context(self):
		self.editor.open_item(spotify_wrapper.get_current_playback().context())
