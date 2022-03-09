# Modified from https://stackoverflow.com/a/36221216

import tkinter
from tkinter import ttk

class CreateToolTip():
	def __init__(self, widget: tkinter.Widget, text: str) -> None:
		self.wait_time = 200     #milliseconds
		self.wrap_length = 360   #pixels
		self.widget = widget
		self.text = text
		self.widget.bind('<Enter>', self.enter)
		self.widget.bind('<Leave>', self.leave)
		self.widget.bind('<ButtonPress>', self.leave)
		self.schedule_id = None
		self.toplevel = None
		self.motion_id = None
		self.x = 0
		self.y = 0

	def enter(self, event: tkinter.Event) -> None:
		self.schedule()
		self.motion(event)

	def leave(self, *_) -> None:
		self.unschedule()
		self.hidetip()

	def schedule(self) -> None:
		self.unschedule()
		self.motion_id = self.widget.bind('<Motion>', self.motion)
		self.schedule_id = self.widget.after(self.wait_time, self.showtip)

	def unschedule(self) -> None:
		if self.schedule_id:
			self.widget.after_cancel(self.schedule_id)
			self.schedule_id = None
		if self.motion_id:
			self.widget.unbind('<Motion>', self.motion_id)
			self.motion_id = None

	def showtip(self, *_) -> None:
		self.toplevel = tkinter.Toplevel(self.widget)
		self.toplevel.wm_overrideredirect(True)
		self.toplevel.wm_geometry(f'+{self.x}+{self.y}')
		label = ttk.Label(self.toplevel, text=self.text, justify='left',
					   background='#ffffff', relief='solid', borderwidth=1,
					   wraplength = self.wrap_length)
		label.grid(column=0, row=0)

	def motion(self, event: tkinter.Event) -> None:
		self.x = self.widget.winfo_rootx() + event.x + 10
		self.y = self.widget.winfo_rooty() + event.y + 10
		if self.toplevel:
			self.toplevel.wm_geometry(f'+{self.x}+{self.y}')

	def hidetip(self) -> None:
		if self.toplevel:
			self.toplevel.destroy()
			self.toplevel = None
