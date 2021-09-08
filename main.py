import os
from tkinter import N, W, S, E, ttk
import tkinter
from pathlib import Path
import json
from utils import Utils

from spotifyWrapper import spotify_wrapper
from editor import Editor
from player import Player


class Window:
	save_file_name = 'save.json'

	def __init__(self):
		os.makedirs(Utils.playlist_location, exist_ok=True)
		os.makedirs(spotify_wrapper.cover_cache_location, exist_ok=True)
		
		self.root = tkinter.Tk()
		self.root.title('Arkhes')
		self.root.protocol('WM_DELETE_WINDOW', self.close)

		self.focused = True

		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		style = ttk.Style()
		style.configure('album.TButton', foreground='green')
		style.configure('playlist.TButton', foreground='red')
		style.configure(spotify_wrapper.resource_type + '.TButton', foreground='blue')

		self.notebook = ttk.Notebook(self.root)
		frame1 = ttk.Frame(self.notebook)
		frame2 = ttk.Frame(self.notebook)
		self.notebook.add(frame1, text='Play')
		self.notebook.add(frame2, text='Edit')
		self.notebook.grid(column=0, row=0, sticky=(N, W, E, S))

		self.player = Player(self.add_mainframe(frame1))
		self.editor = Editor(self.add_mainframe(frame2))
		
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
			with open(self.save_file_name, 'r') as f:
				dct = json.loads(f.readline())
			
			spotify_wrapper.load_from(dct['spotify'])
			self.player.load_from(dct['player'])
			self.editor.load_from(dct['editor'])
	
	def save(self):
		save_string = json.dumps({'player' : self.player.save_dict(), 'editor' : self.editor.save_dict(), 'spotify' : spotify_wrapper.save_dict()})
		with open(self.save_file_name, 'w') as f:
			f.write(save_string)
	
	def set_player_active_flag(self):
		self.player.set_active(self.focused and (self.notebook.index("current") == 0))
	
	def tab_changed(self, event):
		self.player.name_changed()
		self.editor.name_changed()
		self.set_player_active_flag()
	
	def focus_changed(self, new_focus):
		self.focused = new_focus
		self.set_player_active_flag()
	
	def add_mainframe(self, root):
		mainframe = ttk.Frame(root, padding='3 3 12 12')
		mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)
		return mainframe

if __name__ == '__main__':
	Window()