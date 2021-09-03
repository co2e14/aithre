import tkinter as tk
from tkinter import ttk
import sys
import time
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

window = tk.Tk()
window.title("DLS Laser Shaping System")

xz_frame = tk.LabelFrame(master=window, text="X Z Position", borderwidth=5)
x_label = tk.Label(master=xz_frame, text="X").grid(row=1, column=1)
z_label = tk.Label(master=xz_frame, text="Z").grid(row=1, column=3)


xz_frame.grid(row=1, column=1)
ttk.Separator(master=window).grid(row=2, column=1, pady=10, sticky="ew")


window.mainloop()
