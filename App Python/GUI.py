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
import time as tm
from socketIO_client import SocketIO, BaseNamespace
import pickle

class AppNamespace(BaseNamespace):

    def on_connect(self):
        print('[Connected]')

    def on_reconnect(self):
        print('[Reconnected]')

    def on_aaa_response(self):
        filename = 'model/json.sav'
        pickle.dump(self, open(filename, 'wb'))

        test = 'model/test.sav'
        name = pickle.dump(True, open(test, 'wb'))
        print(self)

    def on_disconnect(self):
        print('[Disconnected]')

class App(object):

	def __init__(self):
		super(App, self).__init__()
		self.root = Tk()
		self.fields = ('Tổng lượng nước đã tưới', 'Nhiệt độ', 'Độ ẩm', 'Dự đoán')
		self.entries = {}
		self.frame = None
		self.buttonFrame = None
		self.buttonFigureFrame = None
		self.canvas = None
		self.view = None
		self.timenow = ''
		self.set_time = ''
		self.temperature = 0 #set default- update sau 
		self.humidity = 0  #set default- update sau 
		self.waterflow = 0 #set default- update sau 
		self.category_time = 0
		self.socketIO = None
		self.app_namespace = None
 

	def app(self):
		self.socketIO = SocketIO('172.20.10.11', 3484)
		self.app_namespace = self.socketIO.define(AppNamespace, '/webapp')
		self.GUI_model()
		self.root.mainloop()
		
	def GUI_model(self):
		self.root.title("Quan Ly")
		self.root.rowconfigure(0, weight=1)
		self.root.columnconfigure(0, weight=1)

		self.view = Frame(self.root)
		self.view.grid(row=0, column=0, sticky=tkinter.constants.NS)
		ents = self.makeform(self.view, self.fields)
		self.view.bind('<Return>', (lambda event, e = ents: fetch(e)))

		self.frame = Frame(self.root)
		self.frame.grid(column=0, row=1, sticky=tkinter.constants.NSEW)
		self.frame.rowconfigure(0, weight=1)
		self.frame.columnconfigure(0, weight=1)

		self.addFigure(self.figure(10), self.frame)
		self.sumWaterFlow(self.entries)
		self.tick()
		self.nhietDo()
		

		self.buttonFrame = Frame(self.root)
		self.buttonFrame.grid(row=3, column=0, sticky=tkinter.constants.NS)
		button1 = Button(self.buttonFrame, text = 'Tưới', 
			command=(lambda e = ents: self.btnTuoi(e)))
		button1.pack(side = LEFT, padx = 5, pady = 5)
		button2 = Button(self.buttonFrame, text='Dự đoán',
	        command=(lambda e = ents: self.btnPredict(e)))
		button2.pack(side = LEFT, padx = 5, pady = 5)
		button3 = Button(self.buttonFrame, text = 'Thoát', command = self.buttonFrame.quit)
		button3.pack(side = LEFT, padx = 5, pady = 5)

	def addFigure(self, fig, frame):

	    self.canvas = FigureCanvasTkAgg(fig, master=frame)  # A tk.DrawingArea.
	    self.canvas.draw()
	    self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

	    toolbar = NavigationToolbar2Tk(self.canvas, frame)
	    toolbar.update()
	    self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

	    self.buttonFigureFrame = Frame(frame)
	    self.buttonFigureFrame.pack(side=BOTTOM)
	    b1 = Button(self.buttonFigureFrame, text = '5 ngày trước', 
	        command=(lambda: self.figure_last(self.figure(5), frame)))
	    b1.pack(side = LEFT, padx = 5, pady = 5)

	    b2 = Button(self.buttonFigureFrame, text='1 tháng trước',
	        command=(lambda : self.figure_last(self.figure(30), frame)))
	    b2.pack(side = LEFT, padx = 5, pady = 5)

	def figure_last(self, fig,frame):
		self.canvas.get_tk_widget().destroy()
		self.canvas = FigureCanvasTkAgg(fig, master=frame)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

	# Ve Bieu Do
	def figure(self, number):
		try:
			df = self.read_csv_file('data')
			df = df.iloc[-number:]
			figure = plt.Figure(figsize=(8, 4), dpi=100, constrained_layout=True)
			ax = figure.add_subplot(111)
			df = df[['Day','Water flow']]
			df.plot(kind='line', legend=True, ax=ax, color='blue',marker='o', fontsize=10)
			ax.legend(['Lượng nước tưới'])
			ax.set_title('Biểu đồ lượng nước đã tưới')
			ax.set_ylabel('Lưu lượng nước (ml)')
			ax.set_xlabel('Ngày tưới')
			ax.set_xticklabels(df['Day'], rotation=30)
			ax.grid()

		except:
			print('Lỗi vẽ biểu đồ')
		return figure

	#tao frame
	def makeform(self, window, fields):
		for field in self.fields:
			row = Frame(window)
			lab = Label(row, width=22, text=field+": ", anchor='w')
			ent = Entry(row)
			ent.insert(0,"0")
			# ent.configure(state='disabled')
			row.pack(side = TOP, fill = X, padx = 5 , pady = 5)
			lab.pack(side = LEFT)
			ent.pack(side = RIGHT, expand = YES, fill = X)
			self.entries[field] = ent

		#Thêm thời gian
		row = Frame(window)
		lab = Label(row, width=22, text="Thời gian hiện tại"+": ", anchor='w')
		lab_time = Label(row, width=22, text='', anchor='w', fg = 'red')
		row.pack(side = TOP, fill = X, padx = 5 , pady = 5)
		lab.pack(side = LEFT)

		lab_time.pack(side = RIGHT, expand = YES, fill = X)
		self.entries['Time'] = lab_time


		row = Frame(window)
		lab = Label(row, width=22, text="Cài đặt thời gian tưới "+": ", anchor='w')
		ent = Entry(row)
		ent.insert(0,"")
		btn_set_time = Button(row, text = 'Set', command=(lambda : self.btnSetTime(self.entries)))
		row.pack(side = TOP, fill = X, padx = 5 , pady = 5)
		lab.pack(side = LEFT)
		btn_set_time.pack(side = RIGHT)
		ent.pack(side = RIGHT, expand = YES, fill = X)
		self.entries['Set Time'] = ent

		row = Frame(window)
		label_notif = Label(row, width=22, text="Thời gian tưới là: ", anchor='w')
		self.loadSetTime()
		label_notif1 = Label(row, width=22, anchor='w', fg = 'red')
		label_notif1.config(text = self.set_time)
		lab.pack(side = LEFT)
		row.pack(side = TOP, fill = X, padx = 5 , pady = 5)
		label_notif1.pack(side = RIGHT, expand = YES, fill = X)
		label_notif.pack()

		self.entries['Label_time'] = (label_notif,label_notif1)
		return self.entries



	#du doan luong nuoc
	def predict(self):
		try:
			filename = 'model/finalized_model.sav'
			reg = pickle.load(open(filename, 'rb'))
			y_pred = reg.predict([[1, self.temperature, self.humidity]])
		except:
			print("Lỗi tranning model")
		return y_pred

	def btnPredict(self, entries):
		self.waterflow = round(self.predict()[0], 2)
		self.send_server({'val': 3000})
		entries['Dự đoán'].delete(0,END)
		entries['Dự đoán'].insert(0, self.waterflow)

	def btnSetTime(self, entries):
		time = entries['Set Time'].get()
		if self.stringTime(time, entries):
			entries['Label_time'][0].config(text='Thời gian tưới mới là:', fg = 'black')
			entries['Label_time'][1].config(fg = 'black')
			if self.category == 1:
				self.set_time = time
				entries['Label_time'][1].config(text=self.set_time, fg = 'black')
			elif self.category == 2:
				self.set_time = time+":00"
				entries['Label_time'][1].config(text=self.set_time)
			else:
				self.set_time = time+":00:00"
				entries['Label_time'][1].config(text=self.set_time)
			self.saveSetTime()
		else:
			entries['Label_time'][0].config(text='Lỗi định dạng, mời thử lại', fg = 'red')

	def stringTime(self, time, entries):
		try:
			if time != datetime.datetime.strptime(time, '%H:%M:%S').strftime('%H:%M:%S'):
				raise ValueError
			self.category = 1
			return True
		except ValueError:
			try:
				if time != datetime.datetime.strptime(time, '%H:%M').strftime('%H:%M'):
					raise ValueError
				self.category = 2
				return True
			except ValueError:
				try:
					if time != datetime.datetime.strptime(time, '%H').strftime('%H'):
						raise ValueError
					self.category = 3
					return True
				except ValueError:
					return False
	#doc file csv
	def read_csv_file(self, root):
		csv_path = os.path.join(root, 'Flow.csv')
		df = pd.read_csv(csv_path)
		return df

	def sumWaterFlow(self, entries):
	  df = self.read_csv_file('data')
	  df = df.iloc[-10:]
	  self.entries['Tổng lượng nước đã tưới'].delete(0,END)
	  self.entries['Tổng lượng nước đã tưới'].insert(0, df['Water flow'].sum())

	#oclock
	def tick(self):
		newtime = tm.strftime('%H:%M:%S')
		newday = tm.strftime('%d/%m/%Y')
		if newtime != self.timenow:
			self.timenow = newtime +" - "+newday
			self.entries['Time'].config(text = self.timenow)
		self.entries['Time'].after(200, self.tick)

	def loadSetTime(self):
		filename = 'model/set_time.sav'
		self.set_time = pickle.load(open(filename, 'rb'))

	def saveSetTime(self):
		time = self.set_time
		filename = 'model/set_time.sav'
		pickle.dump(time, open(filename, 'wb'))

	def nhietDo(self):
		day = datetime.datetime.today().strftime('%H:%M:%S')
		if day == self.set_time:
			test = 'model/test.sav'
			# name = pickle.dump(True, open(test, 'wb'))
			self.receiver_server()
			name = pickle.load(open(test, 'rb'))
			print('Kiem tra:', name)
			if name==True:
				print('Da thuc hien')
				filename = 'model/json.sav'
				json = pickle.load(open(filename, 'rb'))
				self.temperature = json['Temp']
				self.entries['Nhiệt độ'].delete(0,END)
				self.entries['Nhiệt độ'].insert(0, self.temperature)
				self.humidity = json['Humi']
				self.entries['Độ ẩm'].delete(0,END)
				self.entries['Độ ẩm'].insert(0, self.humidity)
				self.btnPredict(self.entries)
				self.updateFile()
				self.figure_last(self.figure(10), self.frame)
			name = pickle.dump(False, open(test, 'wb'))
		self.root.after(1000, self.nhietDo) #set 1s reload

	def updateFile(self):
		df = self.read_csv_file('data')
		columns = ['temperature', 'Humidity', 'Water flow' ,'Day']
		newday = datetime.datetime.today().strftime('%d/%m/%Y')
		df = df[['temperature', 'Humidity', 'Water flow' ,'Day']].values
		new = np.array([[int(self.temperature), int(self.humidity), int(self.waterflow), newday]])
		X = np.append(df, new, axis = 0)
		df = pd.DataFrame.from_records(X, columns = columns)
		# print(df.tail())
		df.to_csv('./data/Flow.csv')

	def receiver_server(self):
		# self.socketIO.on('minh', Namespace.on_aaa_response)
		self.app_namespace.emit('Flow', 1)
		self.app_namespace.on('FArdunio', AppNamespace.on_aaa_response)
		print('dagui')
		self.socketIO.wait(seconds=3)

	def send_server(self, data):
		print('Da Send', data)
		self.app_namespace.emit('send', data)
		self.socketIO.wait(seconds=1)

if __name__ == "__main__":
    test = App()
    test.app()

	  
