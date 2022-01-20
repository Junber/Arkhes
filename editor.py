import tkinter
from tkinter import N, W, S, E, ttk, simpledialog
from typing import Callable
import currentPlaybackFrame

from currentPlaylistFrame import CurrentPlaylistFrame
from resources import ArkhesResource
from targetPlaylistFrame import TargetPlaylistFrame
from uriFrame import UriFrame
from addCurrentPlaybackFrame import AddCurrentPlaybackFrame
from playlistNameEntry import PlaylistNameEntry
from resourceList import ResourceList
from spotifyWrapper import SpotifyWrapper, spotify_wrapper
from arkhesPlaylists import ArkhesPlaylists

class Editor:
	def __init__(self, root: ttk.Widget) -> None:
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
		self.categorization_edit = tkinter.BooleanVar(value=True)
		ttk.Checkbutton(self.settings_frame, text='Edit categorization state', variable=self.categorization_edit).grid(column=0, columnspan=6, row=1, sticky=(S, N, W, E))
		self.categorization_view = tkinter.BooleanVar(value=True)
		self.categorization_view.trace_add('write', self.changed_categorization_view)
		ttk.Checkbutton(self.settings_frame, text='Show uncategorized items', variable=self.categorization_view).grid(column=0, columnspan=6, row=2, sticky=(S, N, W, E))

		self.album_list = ResourceList(root, self, 'Contents', 20, self.open_item,
			[
				[lambda item, _: str(item.rating()), self.set_rating],
				['Play', self.play],
				['Copy', self.copy_item],
				['↑', self.move_item_up, lambda album, _: album.line_number() > 0],
				['↓', self.move_item_down, lambda album, albumNum: album.line_number() < albumNum-1],
				['X', self.remove_item_from_list]
			],
			lambda item, _: not SpotifyWrapper.is_song_uri(item.uri()))
		self.album_list.grid(column=1, row=0, rowspan=2, sticky=(N, W, E, S))

		self.notebook = ttk.Notebook(root)
		self.notebook.grid(column=2, row=0, columnspan=3, sticky=(N, W, E, S))

		self.saved_album_list = self.add_saved_frame('Saved Albums', self.remove_saved_album)
		self.saved_playlists_list = self.add_saved_frame('Saved Playlists', self.remove_saved_playlist)
		self.saved_songs_list = self.add_saved_frame('Saved Songs', self.remove_saved_song)
		self.saved_artists_list = self.add_saved_frame('Saved Artists', self.remove_saved_artist)
		self.add_contents_frame()

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

		self.current_playback_frame = currentPlaybackFrame.CurrentPlaybackFrame(root, self, 160)
		self.show_playback(True)

		self.name_changed()
		self.update_saved_albums_list()
		self.update_saved_playlists_list()
		self.update_saved_songs_list()
		self.update_saved_artists_list()

	def add_saved_frame(self, name: str, remove_function: Callable) -> ResourceList:
		frame = ttk.Frame(self.notebook, padding='4 5 4 5')
		self.notebook.add(frame, text=name)

		saved_list = ResourceList(frame, self, '', 20, self.open_item,
			[
				['Play', self.play],
				['Add', self.add_item],
				['X', remove_function]
			],
			lambda item, _: not SpotifyWrapper.is_song_uri(item.uri()))
		saved_list.grid(column=0, row=0, sticky=(N, W, E, S))

		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)

		return saved_list

	def add_contents_frame(self) -> None:
		self.contents_frame = ttk.Frame(self.notebook, padding='4 5 4 5')
		self.notebook.add(self.contents_frame, text='Contents')

		self.contents_uri_name_entry = PlaylistNameEntry(self.contents_frame, self.open_album_contents_uri)
		self.contents_uri_name_entry.grid(column=0, row=0, sticky=(N, S, W, E))
		self.contents_list = ResourceList(self.contents_frame, self, '', 24, self.open_item,
			[
				['Play', self.play],
				['Add', self.add_item]
			],
			lambda *_: False)
		self.contents_list.grid(column=0, row=1, columnspan=4, sticky=(N, W, E, S))

		ttk.Button(self.contents_frame, command=self.play_contents, text='Play').grid(column=1, row=0, sticky=(N, W, E, S))
		ttk.Button(self.contents_frame, command=self.add_contents, text='Add').grid(column=2, row=0, sticky=(N, W, E, S))
		ttk.Button(self.contents_frame, command=self.toggle_saved_contents, text='Toggle Saved').grid(column=3, row=0, sticky=(N, W, E, S))

		self.contents_frame.columnconfigure(0, weight=1)
		self.contents_frame.rowconfigure(1, weight=1)

	def save_dict(self) -> None:
		return {
			'categorization_view' : self.categorization_view.get(),
			'categorization_edit' : self.categorization_edit.get(),
			'current' : self.current_playlist_frame.save_dict(),
			'target' : self.get_target_name(),
			'album_list' : self.album_list.save_dict(),
			'saved_album_list' : self.saved_album_list.save_dict(),
			'saved_playlists_list' : self.saved_playlists_list.save_dict(),
			'saved_songs_list' : self.saved_songs_list.save_dict(),
			'saved_artists_list' : self.saved_songs_list.save_dict(),
			'album_contents_list' : self.contents_list.save_dict()
			}

	def load_from(self, dct: dict) -> None:
		self.categorization_view.set(dct['categorization_view'])
		self.categorization_edit.set(dct['categorization_edit'])
		self.current_playlist_frame.load_from(dct['current'])
		self.set_target_name(dct['target'])
		self.album_list.load_from(dct['album_list'])
		self.saved_album_list.load_from(dct['saved_album_list'])
		self.saved_playlists_list.load_from(dct['saved_playlists_list'])
		self.saved_songs_list.load_from(dct['saved_songs_list'])
		self.saved_artists_list.load_from(dct['saved_artists_list'])
		self.contents_list.load_from(dct['album_contents_list'])

		self.name_changed()
		self.update_saved_albums_list()
		self.update_saved_playlists_list()
		self.update_saved_songs_list()
		self.update_saved_artists_list()

	def update_saved_albums_list(self) -> None:
		self.saved_album_list.set_items_with_saved_albums(self.categorization_view.get())

	def update_saved_playlists_list(self) -> None:
		self.saved_playlists_list.set_items_with_saved_playlists(self.categorization_view.get())

	def update_saved_songs_list(self) -> None:
		self.saved_songs_list.set_items_with_saved_songs(self.categorization_view.get())

	def update_saved_artists_list(self) -> None:
		self.saved_artists_list.set_items_with_saved_artists(self.categorization_view.get())

	def play(self, album: ArkhesResource) -> None:
		spotify_wrapper.shuffle(False)
		spotify_wrapper.play(album.uri())

	def uri_categorized(self, uri: str) -> None:
		self.name_changed()
		if self.categorization_edit.get():
			spotify_wrapper.add_categorized_uri(uri)
			self.update_saved_albums_list()
			self.update_saved_playlists_list()
			self.update_saved_songs_list()
			self.update_saved_artists_list()

	def uri_uncategorized(self, uri: str) -> None:
		self.name_changed()
		if self.categorization_edit.get():
			spotify_wrapper.remove_categorized_uri(uri)
			self.update_saved_albums_list()
			self.update_saved_playlists_list()
			self.update_saved_songs_list()
			self.update_saved_artists_list()

	def set_rating(self, item: ArkhesResource) -> None:
		result = simpledialog.askinteger('Rating', 'Enter your new rating for this album.')
		if result is not None:
			item.set_rating(result)
			ArkhesPlaylists.update_item_in_playlist(self.get_current_name(), item)
			self.name_changed()

	def remove_item_from_list(self, item: ArkhesResource) -> None:
		ArkhesPlaylists.remove_item_from_playlist(self.get_current_name(), item)
		self.uri_uncategorized(item.uri())

	def remove_saved_album(self, album: ArkhesResource) -> None:
		if album.unsave():
			self.update_saved_albums_list()

	def remove_saved_playlist(self, playlist: ArkhesResource) -> None:
		if playlist.unsave():
			self.update_saved_playlists_list()

	def remove_saved_song(self, song: ArkhesResource) -> None:
		if song.unsave():
			self.update_saved_songs_list()

	def remove_saved_artist(self, artist: ArkhesResource) -> None:
		if artist.unsave():
			self.update_saved_artists_list()

	def copy_item(self, item: ArkhesResource) -> None:
		ArkhesPlaylists.add_item_to_playlist(self.get_target_name(), item)
		self.uri_categorized(item.uri())

	def move_item_up(self, item: ArkhesResource) -> None:
		ArkhesPlaylists.move_item_up(self.get_current_name(), item)
		self.name_changed()

	def move_item_down(self, item: ArkhesResource) -> None:
		ArkhesPlaylists.move_item_down(self.get_current_name(), item)
		self.name_changed()

	def add_uri(self, uri: str) -> None:
		ArkhesPlaylists.add_item_to_playlist(self.get_current_name(), spotify_wrapper.get_resource(uri))
		self.uri_categorized(uri)

	def add_item(self, item: ArkhesResource) -> None:
		self.add_uri(item.uri())

	def open_item(self, resource: ArkhesResource) -> None:
		if SpotifyWrapper.is_arkhes_playlist_uri(resource.uri()):
			self.current_playlist_frame.save_current_position()
			self.set_current_name(resource.name())
		else:
			self.contents_uri_name_entry.set(resource.uri())

	def open_album_contents_uri(self, *_) -> None:
		self.notebook.select(4)
		self.contents_list.set_items(self.current_contents_resource().contents())

	def name_changed(self) -> None:
		self.album_list.set_items_with_path(self.get_current_name())

	def changed_categorization_view(self, *_) -> None:
		self.update_saved_albums_list()
		self.update_saved_playlists_list()
		self.update_saved_songs_list()
		self.update_saved_artists_list()


	def get_current_name(self) -> str:
		return self.current_playlist_frame.name_entry.get()

	def set_current_name(self, name: str) -> None:
		self.current_playlist_frame.name_entry.set(name)


	def get_target_name(self) -> str:
		return self.target_playlist_frame.name_entry.get()

	def set_target_name(self, name: str) -> None:
		self.target_playlist_frame.name_entry.set(name)

	def show_playback(self, value: bool) -> None:
		if value:
			self.current_playback_frame.grid(column=0, row=5, columnspan=5, sticky=(N, S, W, E))
		else:
			self.current_playback_frame.grid_forget()

	def update_playback_position(self, _: str) -> None:
		pass

	def current_contents_resource(self) -> ArkhesResource:
		return spotify_wrapper.get_resource(self.contents_uri_name_entry.get())

	def play_contents(self) -> None:
		self.play(self.current_contents_resource())

	def add_contents(self) -> None:
		self.add_item(self.current_contents_resource())

	def toggle_saved_contents(self) -> None:
		self.current_contents_resource().toggle_saved()
