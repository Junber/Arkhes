from tkinter import N, W, S, E, ttk
import tkinter
from pathlib import Path
import json

from spotifyWrapper import spotify_wrapper
from editor import Editor
from player import Player


class Window:
	save_file_name = 'save.json'

	def __init__(self):
		self.root = tkinter.Tk()
		self.root.title('Cool Spotify Controller')
		self.root.protocol('WM_DELETE_WINDOW', self.close)

		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		style = ttk.Style()
		style.configure('album.TButton', background='green')
		style.configure(spotify_wrapper.resource_type + '.TButton', background='blue')

		notebook = ttk.Notebook(self.root)
		frame1 = ttk.Frame(notebook)
		frame2 = ttk.Frame(notebook)
		notebook.add(frame1, text='Play')
		notebook.add(frame2, text='Edit')
		notebook.grid(column=0, row=0, sticky=(N, W, E, S))

		self.player = Player(self.add_mainframe(frame1))
		self.editor = Editor(self.add_mainframe(frame2))
		
		notebook.bind('<<NotebookTabChanged>>', self.tab_changed)

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
	
	def tab_changed(self, event):
		self.player.name_changed()
		self.editor.name_changed()
	
	def add_mainframe(self, root):
		mainframe = ttk.Frame(root, padding='3 3 12 12')
		mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)
		return mainframe

if __name__ == '__main__':
	Window()