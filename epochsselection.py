#######################
### IMPORT -> Numpy ###
#######################
import numpy as np

#########################
### IMPORT -> TKINTER ###
#########################
import tkinter as tk
from tkinter import ttk

###########################
### IMPORT -> DarwinEye ###
###########################
import plots
import config

############################
### IMPORT -> Matplotlib ###
############################
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class Modal(tk.Tk):

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		self.progress = ttk.Progressbar(self, orient="horizontal",length=200, mode="determinate")
		self.progress.pack(expand=True)

	def start(self, data):
		self.maxepochs = 50000
		self.progress["value"] = 0
		self.progress["maximum"] = self.maxepochs
		self.build