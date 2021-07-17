import tkinter
from tkinter import N, W, S, E, ttk, messagebox

from currentPlaylistFrame import CurrentPlaylistFrame
from targetPlaylistFrame import TargetPlaylistFrame
from uriFrame import UriFrame
from albumList import AlbumList
from spotifyWrapper import spotify_wrapper
from utils import Utils

class Editor:
	def __init__(self, root):
		self.current_playlist_frame = CurrentPlaylistFrame(root, self)		
		self.current_playlist_frame.grid(column=0, row=0, sticky=(N, W, E))
		self.target_playlist_frame = TargetPlaylistFrame(root, self)
		self.target_playlist_frame.grid(column=0, row=1, sticky=(N, W, E))
		self.uri_frame = UriFrame(root, self)
		self.uri_frame.grid(column=0, row=2, sticky=(N, W, E))
		
		self.settings_frame = ttk.Labelframe(root, text='Settings', padding='5 5 5 5')
		self.settings_frame.grid(column=0, row=3, rowspan=2, sticky=(S, W, E))
		ttk.Button(self.settings_frame, text='Clear Cache', command=self.clear_cache).grid(column=0, row=0, sticky=(S, N, W, E))
		ttk.Button(self.settings_frame, text='Update Saved Albums', command=self.update_saved_albums).grid(column=1, row=0, sticky=(S, N, W, E))
		self.categorization_mode = tkinter.BooleanVar(value=True)
		self.categorization_mode.trace_add('write', self.changed_categorization_mode)
		ttk.Checkbutton(self.settings_frame, text='Categorization Mode', variable=self.categorization_mode).grid(column=0, columnspan=2, row=1, sticky=(S, N, W, E))

		self.album_list = AlbumList(root, self, 'Contents', self.clicked_playlist_album, [["Copy", self.copy_album], ["X", self.remove_album_from_list]])
		self.album_list.grid(column=1, row=0, rowspan=5, sticky=(N, W, E, S))

		self.saved_album_list = AlbumList(root, self, 'Saved Albums', self.play, [["Add", self.clicked_saved_album], ["X", self.remove_saved_album]])
		self.saved_album_list.grid(column=2, row=0, rowspan=4, columnspan=2, sticky=(N, W, E, S))

		self.page = 0
		self.prev_button = ttk.Button(root, text='Prev', command=lambda: self.change_page(-1))
		self.prev_button.grid(column=2, row=4, sticky=(N, W, E))
		self.next_button = ttk.Button(root, text='Next', command=lambda: self.change_page(+1))
		self.next_button.grid(column=3, row=4, sticky=(N, W, E))

		for child in root.winfo_children(): 
			child.grid_configure(padx=5, pady=5)
		
		root.columnconfigure(0, weight=1)
		root.columnconfigure(1, weight=2, minsize=500)
		root.columnconfigure(2, weight=2, minsize=250)
		root.columnconfigure(3, weight=2, minsize=250)

		self.name_changed()
		self.change_page(0)
	
	def save_dict(self):
		return {'categorization_mode' : self.categorization_mode.get(), 'current' : self.current_playlist_frame.save_dict(),
				'target' : self.get_target_name(), 'page' : self.page}
	
	def load_from(self, dct):
		self.categorization_mode.set(dct['categorization_mode'])
		self.current_playlist_frame.load_from(dct['current'])
		self.set_target_name(dct['target'])
		self.page = dct['page']
		
		self.name_changed()
		self.change_page(0)
	
	def change_page(self, diff):
		self.page += diff

		if self.page == 0:
			self.prev_button.state(['disabled'])
		else:
			self.prev_button.state(['!disabled'])
		
		if self.page >= spotify_wrapper.saved_album_pages(self.categorization_mode.get()) - 1:
			self.page = spotify_wrapper.saved_album_pages(self.categorization_mode.get()) - 1
			self.next_button.state(['disabled'])
		else:
			self.next_button.state(['!disabled'])

		self.saved_album_list.update_with_saved_albums(self.page, self.categorization_mode.get())
		
	def play(self, album):
		spotify_wrapper.shuffle(False)
		spotify_wrapper.play(album['uri'])
	
	def album_categorized(self, album):
		self.name_changed()
		if self.categorization_mode.get():
			spotify_wrapper.add_categorized_album(album)
			self.change_page(0)
	
	def album_uncategorized(self, album):
		self.name_changed()
		if self.categorization_mode.get():
			spotify_wrapper.remove_categorized_album(album)
			self.change_page(0)
	
	def remove_album_from_list(self, album):
		Utils.remove_line_from_file(self.get_current_path(), album['lineNumber'])
		self.album_uncategorized(album)
	
	def remove_saved_album(self, album):
		result = messagebox.askyesno('Delete', 'Do you really want to remove this from your saved albums on Spotify?')
		if result:
			spotify_wrapper.remove_saved_album(album['uri'])
			self.change_page(0)

	def copy_album(self, album):
		Utils.add_line_to_file(self.get_target_path(), album['uri'])
		self.album_categorized(album)

	def clicked_saved_album(self, album):
		Utils.add_line_to_file(self.get_current_path(), album['uri'])
		self.album_categorized(album)

	def clicked_playlist_album(self, album):
		if album['type'] == spotify_wrapper.resource_type:
			self.current_playlist_frame.save_current_position()
			self.set_current_name(album['name'])
		else:
			self.play(album)

	def name_changed(self):
		self.album_list.update(self.get_current_path())

	def clear_cache(self):
		spotify_wrapper.clear_cache()
		self.change_page(0)
	
	def update_saved_albums(self):
		spotify_wrapper.reload_saved_album_cache()
		self.change_page(0)

	def changed_categorization_mode(self, *args):
		self.change_page(0)


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