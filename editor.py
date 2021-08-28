import tkinter
from tkinter import N, W, S, E, ttk, messagebox

from currentPlaylistFrame import CurrentPlaylistFrame
from targetPlaylistFrame import TargetPlaylistFrame
from uriFrame import UriFrame
from addCurrentPlaybackFrame import AddCurrentPlaybackFrame
from playlistNameEntry import PlaylistNameEntry
from albumList import AlbumList
from spotifyWrapper import SpotifyWrapper, spotify_wrapper
from utils import Utils

class Editor:
	def __init__(self, root):
		self.left_frame = ttk.Frame(root)
		self.left_frame.grid(column=0, row=0, rowspan=2, sticky=(N, S, W, E))

		self.current_playlist_frame = CurrentPlaylistFrame(self.left_frame, self)		
		self.current_playlist_frame.grid(column=0, row=0, sticky=(N, W, E))
		self.target_playlist_frame = TargetPlaylistFrame(self.left_frame, self)
		self.target_playlist_frame.grid(column=0, row=1, sticky=(W, E))
		self.uri_frame = UriFrame(self.left_frame, self)
		self.uri_frame.grid(column=0, row=2, sticky=(W, E))
		self.uri_frame = AddCurrentPlaybackFrame(self.left_frame, self)
		self.uri_frame.grid(column=0, row=3, sticky=(W, E))
		
		self.settings_frame = ttk.Labelframe(self.left_frame, text='Settings', padding='5 5 5 5')
		self.settings_frame.grid(column=0, row=4, sticky=(S, W, E))
		ttk.Label(self.settings_frame, text='Update', width=0).grid(column=0, row=0, sticky=(S, N, W, E))
		ttk.Button(self.settings_frame, text='Cache', command=self.clear_cache, width=0).grid(column=1, row=0, sticky=(S, N, W, E))
		ttk.Button(self.settings_frame, text='Albums', command=self.update_saved_albums, width=0).grid(column=2, row=0, sticky=(S, N, W, E))
		ttk.Button(self.settings_frame, text='Playlists', command=self.update_saved_playlists, width=0).grid(column=3, row=0, sticky=(S, N, W, E))
		ttk.Button(self.settings_frame, text='Songs', command=self.update_saved_songs, width=0).grid(column=4, row=0, sticky=(S, N, W, E))
		self.categorization_edit = tkinter.BooleanVar(value=True)
		ttk.Checkbutton(self.settings_frame, text='Edit categorization state', variable=self.categorization_edit).grid(column=0, columnspan=5, row=1, sticky=(S, N, W, E))
		self.categorization_view = tkinter.BooleanVar(value=True)
		self.categorization_view.trace_add('write', self.changed_categorization_view)
		ttk.Checkbutton(self.settings_frame, text='Show uncategorized items', variable=self.categorization_view).grid(column=0, columnspan=5, row=2, sticky=(S, N, W, E))

		self.album_list = AlbumList(root, self, 'Contents', 24, self.open_album,
			[
				["Play", self.play],
				["Copy", self.copy_item],
				["↑", self.move_item_up, lambda album, _: album['lineNumber'] > 0],
				["↓", self.move_item_down, lambda album, albumNum: album['lineNumber'] < albumNum-1],
				["X", self.remove_item_from_list]
			],
			lambda album, _: not SpotifyWrapper.is_song(album['uri']))
		self.album_list.grid(column=1, row=0, rowspan=2, sticky=(N, W, E, S))

		self.notebook = ttk.Notebook(root)
		self.saved_albums_frame = ttk.Frame(self.notebook, padding='4 5 4 5')
		self.saved_playlists_frame = ttk.Frame(self.notebook, padding='4 5 4 5')
		self.saved_songs_frame = ttk.Frame(self.notebook, padding='4 5 4 5')
		self.album_contents_frame = ttk.Frame(self.notebook, padding='4 5 4 5')
		self.notebook.add(self.saved_albums_frame, text='Saved Albums')
		self.notebook.add(self.saved_playlists_frame, text='Saved Playlists')
		self.notebook.add(self.saved_songs_frame, text='Saved Songs')
		self.notebook.add(self.album_contents_frame, text='Contents')
		self.notebook.grid(column=2, row=0, columnspan=3, sticky=(N, W, E, S))

		self.saved_album_list = AlbumList(self.saved_albums_frame, self, '', 24, self.open_album, 
			[
				["Play", self.play],
				["Add", self.add_item],
				["X", self.remove_saved_album]
			])
		self.saved_album_list.grid(column=0, row=0, sticky=(N, W, E, S))

		self.saved_playlists_list = AlbumList(self.saved_playlists_frame, self, '', 24, self.open_album, 
			[
				["Play", self.play],
				["Add", self.add_item],
				["X", self.remove_saved_playlist]
			])
		self.saved_playlists_list.grid(column=0, row=0, sticky=(N, W, E, S))

		self.saved_songs_list = AlbumList(self.saved_songs_frame, self, '', 24, self.open_album, 
			[
				["Play", self.play],
				["Add", self.add_item],
				["X", self.remove_saved_song]
			], lambda *_: False)
		self.saved_songs_list.grid(column=0, row=0, sticky=(N, W, E, S))

		self.album_contents_uri_name_entry = PlaylistNameEntry(self.album_contents_frame, self.open_album_contents_uri)
		self.album_contents_uri_name_entry.grid(column=0, row=0, sticky=(N, S, W, E))
		self.album_contents_list = AlbumList(self.album_contents_frame, self, '', 24, self.open_album,
			[
				["Play", self.play],
				["Add", self.add_item]
			],
			lambda *_: False)
		self.album_contents_list.grid(column=0, row=1, sticky=(N, W, E, S))

		for child in root.winfo_children(): 
			child.grid_configure(padx=5, pady=5)
		
		root.columnconfigure(0, weight=1)
		root.columnconfigure(1, weight=2, minsize=500)
		root.columnconfigure(2, weight=2, minsize=500/3)
		root.columnconfigure(3, weight=2, minsize=500/3)
		root.columnconfigure(4, weight=2, minsize=500/3)
		root.rowconfigure(0, weight=1)

		self.left_frame.rowconfigure(0, weight=2)
		self.left_frame.rowconfigure(1, weight=3)
		self.left_frame.rowconfigure(2, weight=3)
		self.left_frame.rowconfigure(3, weight=3)
		self.left_frame.rowconfigure(4, weight=2)

		self.saved_albums_frame.columnconfigure(0, weight=1)
		self.saved_albums_frame.rowconfigure(0, weight=1)
		self.saved_playlists_frame.columnconfigure(0, weight=1)
		self.saved_playlists_frame.rowconfigure(0, weight=1)
		self.saved_songs_frame.columnconfigure(0, weight=1)
		self.saved_songs_frame.rowconfigure(0, weight=1)
		self.album_contents_frame.columnconfigure(0, weight=1)
		self.album_contents_frame.rowconfigure(1, weight=1)

		self.name_changed()
		self.update_saved_album_list()
		self.update_saved_playlists_list()
		self.update_saved_songs_list()
	
	def save_dict(self):
		return {
			'categorization_view' : self.categorization_view.get(),
			'categorization_edit' : self.categorization_edit.get(),
			'current' : self.current_playlist_frame.save_dict(),
			'target' : self.get_target_name(),
			'album_list' : self.album_list.save_dict(),
			'saved_album_list' : self.saved_album_list.save_dict(),
			'saved_playlists_list' : self.saved_playlists_list.save_dict(),
			'saved_songs_list' : self.saved_songs_list.save_dict(),
			'album_contents_list' : self.album_contents_list.save_dict()
			}
	
	def load_from(self, dct):
		self.categorization_view.set(dct['categorization_view'])
		self.categorization_edit.set(dct['categorization_edit'])
		self.current_playlist_frame.load_from(dct['current'])
		self.set_target_name(dct['target'])
		self.album_list.load_from(dct['album_list'])
		self.saved_album_list.load_from(dct['saved_album_list'])
		self.saved_playlists_list.load_from(dct['saved_playlists_list'])
		self.saved_songs_list.load_from(dct['saved_songs_list'])
		self.album_contents_list.load_from(dct['album_contents_list'])
		
		self.name_changed()
		self.update_saved_album_list()
		self.update_saved_playlists_list()
		self.update_saved_songs_list()
	
	def update_saved_album_list(self):
		self.saved_album_list.set_items_with_saved_albums(self.categorization_view.get())

	def update_saved_playlists_list(self):
		self.saved_playlists_list.set_items_with_saved_playlists(self.categorization_view.get())
		
	def update_saved_songs_list(self):
		self.saved_songs_list.set_items_with_saved_songs(self.categorization_view.get())
		
	def play(self, album):
		spotify_wrapper.shuffle(False)
		spotify_wrapper.play(album['uri'])
	
	def uri_categorized(self, uri):
		self.name_changed()
		if self.categorization_edit.get():
			spotify_wrapper.add_categorized_uri(uri)
			self.update_saved_album_list()
			self.update_saved_playlists_list()
			self.update_saved_songs_list()
	
	def uri_uncategorized(self, uri):
		self.name_changed()
		if self.categorization_edit.get():
			spotify_wrapper.remove_categorized_uri(uri)
			self.update_saved_album_list()
			self.update_saved_playlists_list()
			self.update_saved_songs_list()
	
	def remove_item_from_list(self, item):
		Utils.remove_line_from_file(self.get_current_path(), item['lineNumber'])
		self.uri_uncategorized(item['uri'])
	
	def remove_saved_album(self, album):
		result = messagebox.askyesno('Delete', 'Do you really want to remove %s from your saved albums on Spotify?' % album['name'])
		if result:
			spotify_wrapper.remove_saved_album(album['uri'])
			self.update_saved_album_list()
	
	def remove_saved_playlist(self, playlist):
		result = messagebox.askyesno('Delete', 'Do you really want to remove %s from your saved playlists on Spotify?' % playlist['name'])
		if result:
			spotify_wrapper.remove_saved_playlist(playlist['uri'])
			self.update_saved_playlists_list()
	
	def remove_saved_song(self, song):
		result = messagebox.askyesno('Delete', 'Do you really want to remove %s from your saved songs on Spotify?' % song['name'])
		if result:
			spotify_wrapper.remove_saved_song(song['uri'])
			self.update_saved_songs_list()

	def copy_item(self, item):
		Utils.add_line_to_file(self.get_target_path(), item['uri'])
		self.uri_categorized(item['uri'])
	
	def move_item_up(self, item):
		Utils.remove_line_down(self.get_current_path(), item['lineNumber'] - 1)
		self.name_changed()
	
	def move_item_down(self, item):
		Utils.remove_line_down(self.get_current_path(), item['lineNumber'])
		self.name_changed()
	
	def add_uri(self, uri):
		Utils.add_line_to_file(self.get_current_path(), uri)
		self.uri_categorized(uri)

	def add_item(self, item):
		self.add_uri(item['uri'])
	
	def open_album(self, album):
		if SpotifyWrapper.is_arkhes_playlist(album['uri']):
			self.current_playlist_frame.save_current_position()
			self.set_current_name(album['name'])
		else:
			self.album_contents_uri_name_entry.set(album['uri'])

	def open_album_contents_uri(self, *_):
		self.notebook.select(3)
		uri = self.album_contents_uri_name_entry.get()
		album = spotify_wrapper.get_resource(uri)
		if len(album) == 0:
			self.album_contents_list.set_items([])
		elif SpotifyWrapper.is_album(uri):
			self.album_contents_list.set_items(album['tracks']['items'])
		elif SpotifyWrapper.is_spotify_playlist(uri):
			self.album_contents_list.set_items([track['track'] for track in album['tracks']['items']])
		else:
			self.album_contents_list.set_items([])

	def name_changed(self):
		self.album_list.set_items_with_path(self.get_current_path())

	def clear_cache(self):
		spotify_wrapper.clear_cache()
		self.update_saved_album_list()
		self.update_saved_playlists_list()
		self.update_saved_songs_list()
	
	def update_saved_albums(self):
		spotify_wrapper.reload_saved_albums_cache()
		self.update_saved_album_list()

	def update_saved_playlists(self):
		spotify_wrapper.reload_saved_playlists_cache()
		self.update_saved_playlists_list()

	def update_saved_songs(self):
		spotify_wrapper.reload_saved_songs_cache()
		self.update_saved_songs_list()

	def changed_categorization_view(self, *_):
		self.update_saved_album_list()
		self.update_saved_playlists_list()
		self.update_saved_songs_list()


	def get_current_path(self):
		return self.current_playlist_frame.name_entry.get_path()

	def get_current_name(self):
		return self.current_playlist_frame.name_entry.get()
	
	def set_current_name(self, name):
		self.current_playlist_frame.name_entry.set(name)


	def get_target_path(self):
		return self.target_playlist_frame.name_entry.get_path()

	def get_target_name(self):
		return self.target_playlist_frame.name_entry.get()
	
	def set_target_name(self, name):
		self.target_playlist_frame.name_entry.set(name)