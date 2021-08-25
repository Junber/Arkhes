# Modified from https://stackoverflow.com/a/36221216

import tkinter
from tkinter import ttk

class CreateToolTip():
	def __init__(self, widget, text):
		self.wait_time = 500     #milliseconds
		self.wrap_length = 180   #pixels
		self.widget = widget
		self.text = text
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		self.widget.bind("<ButtonPress>", self.leave)
		self.id = None
		self.toplevel = None

	def enter(self, *_):
		self.schedule()

	def leave(self, *_):
		self.unschedule()
		self.hidetip()

	def schedule(self):
		self.unschedule()
		self.id = self.widget.after(self.wait_time, self.showtip)

	def unschedule(self):
		if self.id:
			self.widget.after_cancel(self.id)
			self.id = None

	def showtip(self, *_):
		x = self.widget.winfo_rootx() + self.widget.winfo_width()
		y = self.widget.winfo_rooty() + self.widget.winfo_height()

		self.toplevel = tkinter.Toplevel(self.widget)
		self.toplevel.wm_overrideredirect(True)
		self.toplevel.wm_geometry("+%d+%d" % (x, y))
		label = ttk.Label(self.toplevel, text=self.text, justify='left',
					   background="#ffffff", relief='solid', borderwidth=1,
					   wraplength = self.wrap_length)
		label.grid(column=0, row=0)

	def hidetip(self):
		if self.toplevel:
			self.toplevel.destroy()
			self.toplevel = None