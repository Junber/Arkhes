from math import ceil
from functools import partial

import tkinter
from tkinter import N, W, S, E, ttk
from typing import Callable, Optional
from resources import ArkhesResource

from tooltip import CreateToolTip
from spotifyWrapper import spotify_wrapper
from arkhesPlaylists import ArkhesPlaylists

class ResourceList:
	name_length = 50

	def __init__(self, parent: ttk.Widget, owner, title: str, default_item_number: int,
		album_clicked_callback: Callable, extra_callbacks:Optional[list] = None,
		enabled_lambda:Callable = None) -> None:

		self.album_clicked_callback = album_clicked_callback
		self.extra_callbacks = extra_callbacks
		self.owner = owner
		self.items = []
		self.unsorted_items = []
		self.enabled_lambda = enabled_lambda
		self.page = 0
		self.old_buttons = []

		self.default_sort_name = 'Default'
		self.ascending_sort_name = 'Asc'
		self.sorts = {
			'Release Date': ArkhesResource.release_date,
			'Name' : ArkhesResource.name,
			'Popularity' : ArkhesResource.popularity,
			'Rating' : ArkhesResource.rating}

		self.build_frames(parent, title)
		self.build_sort(self.sort_frame)
		self.build_page_navigation(self.navigation_frame, default_item_number)

	def build_frames(self, parent: ttk.Widget, title: str) -> None:
		if len(title) == 0:
			self.outer_frame = ttk.Frame(parent)
		else:
			self.outer_frame = ttk.Labelframe(parent, text=title, padding='4 5 4 5')

		self.sort_frame = ttk.Frame(self.outer_frame, padding='0 0 0 5')
		self.sort_frame.grid(column=0, row=0, sticky=(N, S, W, E))
		self.albums_frame = ttk.Frame(self.outer_frame, padding='0 0 0 10')
		self.albums_frame.grid(column=0, row=1, sticky=(N, S, W, E))
		self.navigation_frame = ttk.Frame(self.outer_frame, padding='0 0 0 0')
		self.navigation_frame.grid(column=0, row=2, sticky=(N, S, W, E))

		self.albums_frame.columnconfigure(0, weight=1)
		self.outer_frame.columnconfigure(0, weight=1)
		self.outer_frame.rowconfigure(1, weight=1)

	def build_sort(self, parent: ttk.Widget) -> None:
		ttk.Label(parent, text='Sort:').grid(column=0, row=0, sticky=(N, S, W, E))

		self.current_sort = tkinter.StringVar(value=self.default_sort_name)
		self.current_sort.trace_add('write', self.sort_changed)

		sort_names = [self.default_sort_name] + [sort_name for sort_name in self.sorts]
		self.sort_box = ttk.Combobox(parent, state='readonly',
			textvariable=self.current_sort, values=sort_names)
		self.sort_box.grid(column=1, row=0, sticky=(N, S, W, E))

		self.current_sort_direction = tkinter.StringVar(value=self.ascending_sort_name)
		self.current_sort_direction.trace_add('write', self.sort_changed)
		self.sort_direction_box = ttk.Combobox(parent, state='readonly',
			textvariable=self.current_sort_direction, values=[self.ascending_sort_name, 'Desc'])
		self.sort_direction_box.grid(column=2, row=0, sticky=(N, S, W, E))

	def build_page_navigation(self, parent: ttk.Widget, default_item_number: int) -> None:
		self.page = 0
		self.prev_button = ttk.Button(parent, text='Prev', command=lambda: self.change_page(-1))
		self.prev_button.grid(column=0, row=0, sticky=(N, S, W, E))
		self.page_string = tkinter.StringVar(value='[Page]')
		self.page_label = ttk.Label(parent, textvariable=self.page_string, anchor='center')
		self.page_label.grid(column=1, row=0, sticky=(N, S, W, E))
		self.next_button = ttk.Button(parent, text='Next', command=lambda: self.change_page(+1))
		self.next_button.grid(column=2, row=0, sticky=(N, S, W, E))

		self.max_items_per_page_string = tkinter.StringVar(value=str(default_item_number))
		self.max_items_per_page_string.trace_add('write', self.max_items_per_page_changed)
		self.max_items_per_page_input = ttk.Entry(parent, width=3,
			textvariable=self.max_items_per_page_string)
		self.max_items_per_page_input.grid(column=3, row=0, sticky=(N, S, W, E))
		CreateToolTip(self.max_items_per_page_input, 'Number of items per page')

		parent.columnconfigure(0, weight=1)
		parent.columnconfigure(1, weight=1)
		parent.columnconfigure(2, weight=1)

	def save_dict(self) -> None:
		return {'page' : self.page, 'max_items_per_page' : self.max_items_per_page()}

	def load_from(self, dct: dict) -> None:
		self.page = dct['page']
		self.max_items_per_page_string.set(str(dct['max_items_per_page']))

	def grid(self, **args) -> None:
		self.outer_frame.grid(args)

	def change_page(self, diff: int) -> None:
		self.page += diff

		items_per_page = self.max_items_per_page()
		if items_per_page == 0:
			return

		max_page = ceil(len(self.items) / items_per_page) - 1

		if self.page <= 0:
			self.page = 0
			self.prev_button.state(['disabled'])
		else:
			self.prev_button.state(['!disabled'])

		if self.page >= max_page:
			self.page = max_page
			self.next_button.state(['disabled'])
		else:
			self.next_button.state(['!disabled'])

		self.page_string.set(str(self.page + 1) + ' / ' + str(max_page + 1))

		self.update_with_albums(self.items[self.page*items_per_page : (self.page + 1)*items_per_page])

	def clamp_name(self, album_name: str) -> str:
		if len(album_name) > self.name_length:
			return album_name[:self.name_length-3] + '...'
		return album_name

	def add_button(self, resource: ArkhesResource, x: int, y: int, text: str, width: int,
		command: callable, tooltip_text: str, disabled: bool) -> None:

		button = ttk.Button(self.albums_frame, text=text, style=resource.type()+'.TButton', width = width)
		button.configure(command = command)
		button.grid(column = x, row = y, sticky = (W, E))
		button.grid_configure(padx=1, pady=1)

		if len(tooltip_text) > 0:
			CreateToolTip(button, tooltip_text)
		if disabled:
			button.state(['disabled'])

	def add_button_row(self, resource: ArkhesResource, album_num: int, y: int) -> None:
		self.add_button(resource, 0, y, self.clamp_name(resource.name()), self.name_length + 2,
			partial(self.album_clicked_callback, resource),
			resource.description(),
			self.enabled_lambda is not None and not self.enabled_lambda(resource, album_num))

		if self.extra_callbacks:
			for extra_button_index, extra in enumerate(self.extra_callbacks):
				text = extra[0]
				if not isinstance(text, str):
					text = text(resource, album_num)
				self.add_button(resource, extra_button_index + 1, y, text, len(text) + 2,
					partial(extra[1], resource),
					'',
					len(extra) > 2 and not extra[2](resource, album_num))

	def add_buttons(self, albums: list) -> None:
		for i, album in enumerate(albums):
			self.add_button_row(album, len(albums), i)

	def destory_old_buttons(self) -> None:
		for child in self.old_buttons:
			child.destroy()
		self.old_buttons.clear()

	def clear_buttons(self) -> None:
		self.old_buttons = self.albums_frame.winfo_children()
		self.albums_frame.after(20, self.destory_old_buttons) # Delay reduces flickering somewhat

	def update_with_albums(self, albums: list) -> None:
		self.clear_buttons()
		self.add_buttons(albums)

	def perform_sort(self, items_to_be_sorted: list) -> None:
		if self.current_sort.get() != self.default_sort_name:
			items_to_be_sorted.sort(key = self.sorts[self.current_sort.get()],
									reverse = (self.current_sort_direction.get() != self.ascending_sort_name))
		elif self.current_sort_direction.get() != self.ascending_sort_name:
			items_to_be_sorted.reverse()

	def set_items(self, items: list) -> None:
		self.unsorted_items = items.copy()
		self.items = items.copy()
		self.perform_sort(self.items)

		self.change_page(0)

	def set_items_with_path(self, name: str) -> None:
		self.set_items(ArkhesPlaylists.get_playlist_items(name))

	def set_items_with_saved_albums(self, categorization_mode: bool) -> None:
		self.set_items(spotify_wrapper.saved_albums(categorization_mode))

	def set_items_with_saved_playlists(self, categorization_mode: bool) -> None:
		self.set_items(spotify_wrapper.saved_playlists(categorization_mode))

	def set_items_with_saved_songs(self, categorization_mode: bool) -> None:
		self.set_items(spotify_wrapper.saved_songs(categorization_mode))

	def set_items_with_saved_artists(self, categorization_mode: bool) -> None:
		self.set_items(spotify_wrapper.saved_artists(categorization_mode))

	def sort_changed(self, *_) -> None:
		self.set_items(self.unsorted_items)

	def max_items_per_page_changed(self, *_) -> None:
		self.change_page(0)

	def max_items_per_page(self) -> int:
		items_per_page = self.max_items_per_page_string.get()
		if items_per_page.isdigit():
			return int(items_per_page)
		else:
			return 0
