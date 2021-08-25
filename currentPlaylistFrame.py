from tkinter import N, W, S, E, ttk

from playlistNameEntry import PlaylistNameEntry

class CurrentPlaylistFrame:
	def __init__(self, root, editor):
		self.editor = editor

		self.frame = ttk.Labelframe(root, text='Current', padding='5 5 5 5')
		self.frame.columnconfigure(0, weight=1)
		self.frame.columnconfigure(1, weight=1)

		self.name_entry = PlaylistNameEntry(self.frame, self.name_changed)
		self.name_entry.grid(column=0, row=0, columnspan = 2, sticky=(N, S, W, E))
		self.back_button = ttk.Button(self.frame, text='<', command=self.go_back)
		self.back_button.grid(column=0, row=1, sticky=(S, N, W, E))
		self.forward_button = ttk.Button(self.frame, text='>', command=self.go_forward)
		self.forward_button.grid(column=1, row=1, sticky=(S, N, W, E))
		self.undo_stack = []
		self.redo_stack = []
		self.set_undo_redo_button_state()

	def grid(self, **args):
		self.frame.grid(args)
	
	def save_dict(self):
		return {'name' : self.name_entry.get(), 'undo_stack' : self.undo_stack, 'redo_stack' : self.redo_stack}

	def load_from(self, dct):
		self.name_entry.set(dct['name'])
		self.undo_stack = dct['undo_stack']
		self.redo_stack = dct['redo_stack']
		self.set_undo_redo_button_state()

	def name_changed(self, *_):
		self.editor.name_changed()
	
	def save_current_position(self):
		self.undo_stack.append(self.name_entry.get())
		if len(self.undo_stack) > 50:
			self.undo_stack = self.undo_stack[-50:]
		self.redo_stack = []
		self.set_undo_redo_button_state()
	
	def set_button_state(self, button, list):
		if len(list):
			button.state(['!disabled'])
		else:
			button.state(['disabled'])
	
	def set_undo_redo_button_state(self):
		self.set_button_state(self.back_button, self.undo_stack)
		self.set_button_state(self.forward_button, self.redo_stack)
	
	def go_back(self):
		self.redo_stack.append(self.name_entry.get())
		new_playlist = self.undo_stack.pop()
		self.name_entry.set(new_playlist)
		self.set_undo_redo_button_state()

	def go_forward(self):
		self.undo_stack.append(self.name_entry.get())
		new_playlist = self.redo_stack.pop()
		self.name_entry.set(new_playlist)
		self.set_undo_redo_button_state()