from math import ceil
from pathlib import Path

import tkinter
from tkinter import N, W, S, E, ttk

from tooltip import CreateToolTip
from spotifyWrapper import spotify_wrapper
from utils import Utils

class AlbumList:
	name_length = 50

	def __init__(self, parent, owner, title, album_clicked_callback, extra_callbacks=[], enabled_lambda=None) -> None:
		self.album_clicked_callback = album_clicked_callback
		self.extra_callbacks = extra_callbacks
		self.owner = owner
		self.items = []
		self.enabled_lambda = enabled_lambda

		self.build_frames(parent, title)
		self.build_page_navigation(self.outer_frame)
	
	def build_frames(self, parent, title):
		if len(title) == 0:
			self.outer_frame = ttk.Frame(parent)
		else:
			self.outer_frame = ttk.Labelframe(parent, text=title, padding='4 5 4 5')
		self.albums_frame = ttk.Frame(self.outer_frame, padding='0 0 0 10')
		self.albums_frame.grid(column=0, row=0, columnspan=4, sticky=(N, S, W, E))

		self.albums_frame.columnconfigure(0, weight=1)
		self.outer_frame.columnconfigure(0, weight=1)
		self.outer_frame.columnconfigure(1, weight=1)
		self.outer_frame.columnconfigure(2, weight=1)
		self.outer_frame.rowconfigure(0, weight=1)
	
	def build_page_navigation(self, parent):
		self.page = 0
		self.prev_button = ttk.Button(parent, text='Prev', command=lambda: self.change_page(-1))
		self.prev_button.grid(column=0, row=1, sticky=(N, S, W, E))
		self.page_string = tkinter.StringVar(value="[Page]")
		self.page_label = ttk.Label(parent, textvariable=self.page_string, anchor='center')
		self.page_label.grid(column=1, row=1, sticky=(N, S, W, E))
		self.next_button = ttk.Button(parent, text='Next', command=lambda: self.change_page(+1))
		self.next_button.grid(column=2, row=1, sticky=(N, S, W, E))

		self.max_items_per_page_string = tkinter.StringVar(value="20")
		self.max_items_per_page_string.trace_add('write', self.max_items_per_page_changed)
		self.max_items_per_page_input = ttk.Entry(parent, width=3, textvariable=self.max_items_per_page_string)
		self.max_items_per_page_input.grid(column=3, row=1, sticky=(N, S, W, E))
		CreateToolTip(self.max_items_per_page_input, "Number of items per page")
	
	def save_dict(self):
		return {'page' : self.page, 'max_items_per_page' : self.max_items_per_page()}
	
	def load_from(self, dct):
		self.page = dct['page']
		self.max_items_per_page_string.set(str(dct['max_items_per_page']))

	def grid(self, **args):
		self.outer_frame.grid(args)
	
	def get_album(self, i, resource):
		album = spotify_wrapper.get_resource(resource)
		
		album['playlistLine'] = resource
		album['lineNumber'] = i
		return album
	
	def get_albums_from_file(self, filename):
		lines = Utils.get_lines_from_file(filename)
		
		spotify_wrapper.cache_uncached_albums(lines)
		uris = [self.get_album(i, line) for i, line in enumerate(lines)]

		return uris
	
	def change_page(self, diff):
		self.page += diff
		
		items_per_page = self.max_items_per_page()
		if items_per_page == 0:
			return

		maxPage = ceil(len(self.items) / items_per_page) - 1

		if self.page <= 0:
			self.page = 0
			self.prev_button.state(['disabled'])
		else:
			self.prev_button.state(['!disabled'])
		
		if self.page >= maxPage:
			self.page = maxPage
			self.next_button.state(['disabled'])
		else:
			self.next_button.state(['!disabled'])

		self.page_string.set(str(self.page + 1) + " / " + str(maxPage + 1))

		self.update_with_albums(self.items[self.page*items_per_page : (self.page + 1)*items_per_page])

	def clamp_name(self, album_name):
		if len(album_name) > self.name_length:
			return album_name[:self.name_length-3] + "..."
		return album_name

	def add_button(self, album, x, y, text, width, command, disabled):
		button = ttk.Button(self.albums_frame, text=text, style=album['type']+'.TButton', width = width)
		button.configure(command = command)
		button.grid(column = x, row = y, sticky = (W, E))
		button.grid_configure(padx=1, pady=1)
		if disabled:
			button.state(['disabled'])
	
	def add_button_row(self, album, albumNum, y):
		button = ttk.Button(self.albums_frame, text=self.clamp_name(album['name']), style=album['type']+'.TButton', width = self.name_length + 2)
		button.configure(command = lambda album=album: self.album_clicked_callback(album))
		button.grid(column = 0, row = y, sticky = (W, E))
		button.grid_configure(padx=1, pady=1)

		self.add_button(album, 0, y, self.clamp_name(album['name']), self.name_length + 2,
			lambda album=album: self.album_clicked_callback(album),
			self.enabled_lambda is not None and not self.enabled_lambda(album, albumNum))

		for extraButtonIndex, extra in enumerate(self.extra_callbacks):
			self.add_button(album, extraButtonIndex + 1, y, extra[0], len(extra[0]) + 2,
				(lambda callback : lambda album=album: callback(album))(extra[1]),
				len(extra) > 2 and not extra[2](album, albumNum))
	
	def add_buttons(self, albums):
		for i, album in enumerate(albums):
			self.add_button_row(album, len(albums), i)
	
	def destory_old_buttons(self):
		for child in self.old_buttons:
			child.destroy()
	
	def clear_buttons(self):
		self.old_buttons = self.albums_frame.winfo_children()
		self.albums_frame.after(20, self.destory_old_buttons) # Doing this with a delay reduces flickering somewhat
	
	def update_with_albums(self, albums):
		self.clear_buttons()
		self.add_buttons(albums)
	
	def set_items(self, items):
		self.items = items
		self.change_page(0)
	
	def set_items_with_path(self, path):
		if Path(path).is_file():
	 		self.set_items(self.get_albums_from_file(path))
		else:
			self.set_items([])
	
	def set_items_with_saved_albums(self, categorization_mode):
		self.set_items(spotify_wrapper.saved_albums(categorization_mode))
	
	def max_items_per_page_changed(self, *args):
		self.change_page(0)
	
	def max_items_per_page(self):
		items_per_page = self.max_items_per_page_string.get()
		if items_per_page.isdigit():
			return int(items_per_page)
		else:
			return 0