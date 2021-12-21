import os
from tkinter import N, W, S, E, ttk
import tkinter
from pathlib import Path
import json
from arkhesPlaylists import ArkhesPlaylists

from spotifyWrapper import spotify_wrapper
from editor import Editor
from player import Player
from settings import Settings


class Window:
	save_file_name = 'save.json'

	def __init__(self):
		os.makedirs(ArkhesPlaylists.playlist_location, exist_ok=True)
		os.makedirs(spotify_wrapper.cover_cache_location, exist_ok=True)

		self.root = tkinter.Tk()
		self.root.title('Arkhes')
		self.root.protocol('WM_DELETE_WINDOW', self.close)

		self.root.tk.call("source", "theme/azure.tcl")
		self.root.tk.call("set_theme", "dark")

		self.focused = True

		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		style = ttk.Style()
		for widget_type in ['TButton', 'TCombobox', 'TLabel', 'TEntry']:
			style.configure(widget_type, font=('', 5))
		style.configure('album.TButton', foreground='green')
		style.configure('playlist.TButton', foreground='red')
		style.configure(spotify_wrapper.resource_type + '.TButton', foreground='blue')

		self.notebook = ttk.Notebook(self.root)
		self.notebook.grid(column=0, row=0, sticky=(N, W, E, S))

		self.player = Player(self.add_mainframe('Play'))
		self.editor = Editor(self.add_mainframe('Edit'))
		self.settings = Settings(self.add_mainframe('Settings'))

		self.notebook.bind('<<NotebookTabChanged>>', self.tab_changed)
		self.root.bind('<FocusIn>', lambda _: self.focus_changed(True))
		self.root.bind('<FocusOut>', lambda _: self.focus_changed(False))

		self.load()
		self.root.mainloop()

	def close(self):
		self.save()
		spotify_wrapper.save_cache()
		self.root.destroy()

	def load(self):
		if Path(self.save_file_name).is_file():
			dct = None
			with open(self.save_file_name, 'r', encoding='utf8') as file:
				dct = json.loads(file.readline())

			spotify_wrapper.load_from(dct['spotify'])
			self.player.load_from(dct['player'])
			self.editor.load_from(dct['editor'])
			self.settings.load_from(dct['settings'])

	def save(self):
		save_string = json.dumps(
			{
				'player' : self.player.save_dict(),
				'editor' : self.editor.save_dict(),
				'settings' : self.settings.save_dict(),
				'spotify' : spotify_wrapper.save_dict()
			})

		with open(self.save_file_name, 'w', encoding='utf8') as file:
			file.write(save_string)

	def set_player_active_flag(self):
		self.player.set_active(self.focused and (self.notebook.index("current") == 0))

	def tab_changed(self, _):
		self.player.name_changed()
		self.editor.name_changed()
		self.set_player_active_flag()

	def focus_changed(self, new_focus: bool):
		self.focused = new_focus
		self.set_player_active_flag()

	def add_mainframe(self, name):
		mainframe = ttk.Frame(self.notebook, padding='3 3 12 12')
		self.notebook.add(mainframe, text=name)
		mainframe.columnconfigure(0, weight=1)
		mainframe.rowconfigure(0, weight=1)
		return mainframe

if __name__ == '__main__':
	Window()
