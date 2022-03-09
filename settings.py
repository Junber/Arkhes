from tkinter import N, W, S, E, ttk
import tkinter

from editor import Editor
from spotifyWrapper import SpotifyWrapper, spotify_wrapper


class Settings:
	def __init__(self, root: ttk.Widget, editor: Editor) -> None:
		self.editor = editor
		self.build_update_frame(root)
		self.build_editor_frame(root)

	def build_update_frame(self, root: ttk.Widget) -> None:
		self.update_frame = ttk.Labelframe(root, text='Update', padding='5 5 5 5')
		self.update_frame.grid(column=0, row=0, sticky=(N, S, W, E))

		ttk.Button(self.update_frame, text='Whole Cache', command=SpotifyWrapper.clear_cache, width=0).grid(column=0, row=0, sticky=(S, N, W, E))

		saved_frame = ttk.Frame(self.update_frame)
		saved_frame.grid(column=0, row=1, sticky=(S, N, W, E))
		ttk.Label(saved_frame, text='Saved', width=0).grid(column=0, row=0, sticky=(S, N, W, E))
		ttk.Button(saved_frame, text='Albums', command=self.update_saved_albums, width=0).grid(column=1, row=0, sticky=(S, N, W, E))
		ttk.Button(saved_frame, text='Playlists', command=self.update_saved_playlists, width=0).grid(column=2, row=0, sticky=(S, N, W, E))
		ttk.Button(saved_frame, text='Songs', command=self.update_saved_songs, width=0).grid(column=3, row=0, sticky=(S, N, W, E))
		ttk.Button(saved_frame, text='Artists', command=self.update_saved_artists, width=0).grid(column=4, row=0, sticky=(S, N, W, E))

	def build_editor_frame(self, root: ttk.Widget) -> None:
		self.editor_frame = ttk.Labelframe(root, text='Editor', padding='5 5 5 5')
		self.editor_frame.grid(column=0, row=1, sticky=(N, S, W, E))

		self.show_playback_in_editor = tkinter.BooleanVar(value=True)
		self.show_playback_in_editor.trace_add('write', lambda *_:self.editor.show_playback(self.show_playback_in_editor.get()))
		ttk.Checkbutton(self.editor_frame, text='Show Current Playback', width=0, variable=self.show_playback_in_editor).grid(column=0, row=0, sticky=(S, N, W, E))

		self.show_uri_in_editor = tkinter.BooleanVar(value=True)
		self.show_uri_in_editor.trace_add('write', lambda *_:self.editor.show_uri(self.show_uri_in_editor.get()))
		ttk.Checkbutton(self.editor_frame, text='Show Add URI', width=0, variable=self.show_uri_in_editor).grid(column=1, row=0, sticky=(S, N, W, E))


	def save_dict(self) -> dict:
		return {
			'show_playback_in_editor' : self.show_playback_in_editor.get(),
			'show_uri_in_editor' : self.show_uri_in_editor.get()
			}

	def load_from(self, dct: dict) -> None:
		self.show_playback_in_editor.set(dct['show_playback_in_editor'])
		self.show_uri_in_editor.set(dct['show_uri_in_editor'])

	def update_saved_albums(self) -> None:
		spotify_wrapper.reload_saved_albums_cache()

	def update_saved_playlists(self) -> None:
		spotify_wrapper.reload_saved_playlists_cache()

	def update_saved_songs(self) -> None:
		spotify_wrapper.reload_saved_songs_cache()

	def update_saved_artists(self) -> None:
		spotify_wrapper.reload_saved_artists_cache()
