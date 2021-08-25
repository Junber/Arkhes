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
		ttk.Button(self.settings_frame, text='Clear Cache', command=self.clear_cache).grid(column=0, row=0, sticky=(S, N, W, E))
		ttk.Button(self.settings_frame, text='Update Saved Albums', command=self.update_saved_albums).grid(column=1, row=0, sticky=(S, N, W, E))
		self.categorization_edit = tkinter.BooleanVar(value=True)
		ttk.Checkbutton(self.settings_frame, text='Edit categorization state', variable=self.categorization_edit).grid(column=0, columnspan=2, row=1, sticky=(S, N, W, E))
		self.categorization_view = tkinter.BooleanVar(value=True)
		self.categorization_view.trace_add('write', self.changed_categorization_view)
		ttk.Checkbutton(self.settings_frame, text='Show uncategorized albums', variable=self.categorization_view).grid(column=0, columnspan=2, row=2, sticky=(S, N, W, E))

		self.album_list = AlbumList(root, self, 'Contents', 24, self.open_album,
			[
				["Play", self.play],
				["Copy", self.copy_album],
				["↑", self.move_album_up, lambda album, _: album['lineNumber'] > 0],
				["↓", self.move_album_down, lambda album, albumNum: album['lineNumber'] < albumNum-1],
				["X", self.remove_album_from_list]
			],
			lambda album, _: not SpotifyWrapper.is_song(album['uri']))
		self.album_list.grid(column=1, row=0, rowspan=2, sticky=(N, W, E, S))

		self.notebook = ttk.Notebook(root)
		self.saved_albums_frame = ttk.Frame(self.notebook, padding='4 5 4 5')
		self.album_contents_frame = ttk.Frame(self.notebook, padding='4 5 4 5')
		self.notebook.add(self.saved_albums_frame, text='Saved Albums')
		self.notebook.add(self.album_contents_frame, text='Album Contents')
		self.notebook.grid(column=2, row=0, columnspan=3, sticky=(N, W, E, S))

		self.saved_album_list = AlbumList(self.saved_albums_frame, self, '', 24, self.open_album, 
			[
				["Play", self.play],
				["Add", self.add_album],
				["X", self.remove_saved_album]
			])
		self.saved_album_list.grid(column=0, row=0, sticky=(N, W, E, S))

		self.album_contents_uri_name_entry = PlaylistNameEntry(self.album_contents_frame, self.open_album_contents_uri)
		self.album_contents_uri_name_entry.grid(column=0, row=0, sticky=(N, S, W, E))
		self.album_contents_list = AlbumList(self.album_contents_frame, self, '', 24, self.play, [["Add", self.add_album]])
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
		self.album_contents_frame.columnconfigure(0, weight=1)
		self.album_contents_frame.rowconfigure(1, weight=1)

		self.name_changed()
		self.update_saved_album_list()
	
	def save_dict(self):
		return {
			'categorization_view' : self.categorization_view.get(),
			'categorization_edit' : self.categorization_edit.get(),
			'current' : self.current_playlist_frame.save_dict(),
			'target' : self.get_target_name(),
			'album_list' : self.album_list.save_dict(),
			'saved_album_list' : self.saved_album_list.save_dict(),
			'album_contents_list' : self.album_contents_list.save_dict()
			}
	
	def load_from(self, dct):
		self.categorization_view.set(dct['categorization_view'])
		self.categorization_edit.set(dct['categorization_edit'])
		self.current_playlist_frame.load_from(dct['current'])
		self.set_target_name(dct['target'])
		self.album_list.load_from(dct['album_list'])
		self.saved_album_list.load_from(dct['saved_album_list'])
		self.album_contents_list.load_from(dct['album_contents_list'])
		
		self.name_changed()
		self.saved_album_list.set_items_with_saved_albums(self.categorization_view.get())
	
	def update_saved_album_list(self):
		self.saved_album_list.set_items_with_saved_albums(self.categorization_view.get())
		
	def play(self, album):
		spotify_wrapper.shuffle(False)
		spotify_wrapper.play(album['uri'])
	
	def uri_categorized(self, uri):
		self.name_changed()
		if self.categorization_edit.get():
			spotify_wrapper.add_categorized_album(uri)
			self.update_saved_album_list()
	
	def album_uncategorized(self, album):
		self.name_changed()
		if self.categorization_edit.get():
			spotify_wrapper.remove_categorized_album(album)
			self.update_saved_album_list()
	
	def remove_album_from_list(self, album):
		Utils.remove_line_from_file(self.get_current_path(), album['lineNumber'])
		self.album_uncategorized(album)
	
	def remove_saved_album(self, album):
		result = messagebox.askyesno('Delete', 'Do you really want to remove %s from your saved albums on Spotify?' % album['name'])
		if result:
			spotify_wrapper.remove_saved_album(album['uri'])
			self.update_saved_album_list()

	def copy_album(self, album):
		Utils.add_line_to_file(self.get_target_path(), album['uri'])
		self.uri_categorized(album['uri'])
	
	def move_album_up(self, album):
		Utils.remove_line_down(self.get_current_path(), album['lineNumber'] - 1)
		self.name_changed()
	
	def move_album_down(self, album):
		Utils.remove_line_down(self.get_current_path(), album['lineNumber'])
		self.name_changed()
	
	def add_uri(self, uri):
		Utils.add_line_to_file(self.get_current_path(), uri)
		self.uri_categorized(uri)

	def add_album(self, album):
		self.add_uri(album['uri'])
	
	def open_album(self, album):
		if SpotifyWrapper.is_arkhes_playlist(album['uri']):
			self.current_playlist_frame.save_current_position()
			self.set_current_name(album['name'])
		else:
			self.album_contents_uri_name_entry.set(album['uri'])

	def open_album_contents_uri(self, *_):
		self.notebook.select(1)
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
	
	def update_saved_albums(self):
		spotify_wrapper.reload_saved_album_cache()
		self.update_saved_album_list()

	def changed_categorization_view(self, *_):
		self.update_saved_album_list()


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