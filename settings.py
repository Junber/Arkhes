from tkinter import N, W, S, E, ttk

from spotifyWrapper import SpotifyWrapper, spotify_wrapper


class Settings:
	def __init__(self, root: ttk.Widget):
		self.settings_frame = ttk.Labelframe(root, text='Update', padding='5 5 5 5')
		self.settings_frame.grid(column=0, row=0, sticky=(N, S, W, E))

		ttk.Button(self.settings_frame, text='Complete Cache', command=self.clear_cache, width=0).grid(column=0, row=0, sticky=(S, N, W, E))

		saved_frame = ttk.Frame(self.settings_frame)
		saved_frame.grid(column=0, row=1, sticky=(S, N, W, E))
		ttk.Label(saved_frame, text='Saved', width=0).grid(column=0, row=0, sticky=(S, N, W, E))
		ttk.Button(saved_frame, text='Albums', command=self.update_saved_albums, width=0).grid(column=1, row=0, sticky=(S, N, W, E))
		ttk.Button(saved_frame, text='Playlists', command=self.update_saved_playlists, width=0).grid(column=2, row=0, sticky=(S, N, W, E))
		ttk.Button(saved_frame, text='Songs', command=self.update_saved_songs, width=0).grid(column=3, row=0, sticky=(S, N, W, E))
		ttk.Button(saved_frame, text='Artists', command=self.update_saved_artists, width=0).grid(column=4, row=0, sticky=(S, N, W, E))

	def save_dict(self):
		return {}
	
	def load_from(self, _: dict):
		pass

	def clear_cache(self):
		SpotifyWrapper.clear_cache()
	
	def update_saved_albums(self):
		spotify_wrapper.reload_saved_albums_cache()

	def update_saved_playlists(self):
		spotify_wrapper.reload_saved_playlists_cache()

	def update_saved_songs(self):
		spotify_wrapper.reload_saved_songs_cache()

	def update_saved_artists(self):
		spotify_wrapper.reload_saved_artists_cache()
