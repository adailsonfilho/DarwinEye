from tkinter import ttk

class Process():

	def __init__(self, progressbar, length, start, end, label, stringvar):
		self.progressbar = progressbar
		self.length = length
		self.start = start
		self.end = end
		self.label = label
		self.stringvar = stringvar

	def __enter__(self):
		self.progressbar['length'] = 200
		self.progressbar['value'] = self.start
		self.progressbar['maximum'] = self.end
		self.stringvar.set(self.label)

	def __exit__(self, type, value, traceback):
		self.progressbar['length'] = 0
		self.stringvar.set("")