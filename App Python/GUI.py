import math
from tkinter import *
import tkinter.constants
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import pandas as pd
import os
import pickle
import numpy as np
import datetime

class App(object):
	"""docstring for App"""

	def __init__(self):
		super(App, self).__init__()
		self.root = Tk()
		self.fields = ('Tổng lượng nước đã tưới', 'Nhiệt độ', 'Độ ẩm', 'Ngày', 'Dự đoán')
		self.entries = {}
		self.frame1 = None
		self.canvas = None


	def app(self):
		self.setWin()
		self.root.mainloop()
	def setWin(self):
		self.root.title("Quan Ly")
		self.root.rowconfigure(0, weight=1)
		self.root.columnconfigure(0, weight=1)

		view = Frame(self.root)
		view.grid(row=0, column=0, sticky=tkinter.constants.NS)
		ents = self.makeform(view, self.fields)
		view.bind('<Return>', (lambda event, e = ents: fetch(e)))
		frame = Frame(self.root)
		frame.grid(column=0, row=1, sticky=tkinter.constants.NSEW)
		frame.rowconfigure(0, weight=1)
		frame.columnconfigure(0, weight=1)

		self.addFigure(self.figure(10), frame)
		self.get_value_arduino(self.entries)


		buttonFrame = Frame(self.root)
		buttonFrame.grid(row=3, column=0, sticky=tkinter.constants.NS)
		button1 = Button(buttonFrame, text = 'Tưới', 
			command=(lambda e = ents: self.btnTuoi(e)))
		button1.pack(side = LEFT, padx = 5, pady = 5)
		button2 = Button(buttonFrame, text='Dự đoán',
	        command=(lambda e = ents: self.btnPredict(e)))
		button2.pack(side = LEFT, padx = 5, pady = 5)
		button3 = Button(buttonFrame, text = 'Thoát', command = buttonFrame.quit)
		button3.pack(side = LEFT, padx = 5, pady = 5)

	def addFigure(self, fig, frame):

	    self.canvas = FigureCanvasTkAgg(fig, master=frame)  # A tk.DrawingArea.
	    self.canvas.draw()
	    self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

	    toolbar = NavigationToolbar2Tk(self.canvas, frame)
	    toolbar.update()
	    self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

	    self.frame1 = Frame(frame)
	    self.frame1.pack(side=BOTTOM)
	    b1 = Button(self.frame1, text = '5 ngày trước', 
	        command=(lambda: self.last_5(self.figure(5), frame)))
	    b1.pack(side = LEFT, padx = 5, pady = 5)

	    b2 = Button(self.frame1, text='1 tháng trước',
	        command=(lambda : self.last_5(self.figure(30), frame)))
	    b2.pack(side = LEFT, padx = 5, pady = 5)

	def last_5(self, fig,frame):
		self.canvas.get_tk_widget().destroy()
		self.canvas = FigureCanvasTkAgg(fig, master=frame)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

	def figure(self, number):
		df = self.read_csv_file('data')
		df = df.iloc[-number:]
		figure = plt.Figure(figsize=(5, 4), dpi=100)
		ax = figure.add_subplot(111)
		df = df[['Head Size(cm^3)','Brain Weight(grams)']].groupby('Head Size(cm^3)').sum()
		df.plot(kind='line', legend=True, ax=ax, color='blue',marker='o', fontsize=10)
		
		ax.set_title('Biểu đồ thống kê lượng nước')
		return figure

	#tao frame
	def makeform(self, window, fields):
		for field in self.fields:
			row = Frame(window)
			lab = Label(row, width=22, text=field+": ", anchor='w')
			ent = Entry(row)
			ent.insert(0,"0")
			row.pack(side = TOP, fill = X, padx = 5 , pady = 5)
			lab.pack(side = LEFT)
			ent.pack(side = RIGHT, expand = YES, fill = X)
			self.entries[field] = ent
		return self.entries

	#du doan luong nuoc
	def predict(self):
		filename = 'model/finalized_model.sav'
		reg = pickle.load(open(filename, 'rb'))
		y_pred = reg.predict([[2000]])
		return y_pred
	def btnPredict(self, entries):
		pred = round(self.predict()[0], 2)
		entries['Dự đoán'].delete(0,END)
		entries['Dự đoán'].insert(0, pred)

	def btnTuoi(self, entries):
	  pass

	#doc file csv
	def read_csv_file(self, root):
		csv_path = os.path.join(root, 'headbrain.csv')
		df = pd.read_csv(csv_path)
		return df

	def get_value_arduino(self, entries):
	  day = datetime.datetime.today().strftime('%d/%m/%Y')
	  self.entries['Ngày'].delete(0,END)
	  self.entries['Ngày'].insert(0, day)

	  df = self.read_csv_file('data')
	  df = df.iloc[-10:]

	  self.entries['Tổng lượng nước đã tưới'].delete(0,END)
	  self.entries['Tổng lượng nước đã tưới'].insert(0, df['Brain Weight(grams)'].sum())

if __name__ == "__main__":
    test = App()
    test.app()
	  
