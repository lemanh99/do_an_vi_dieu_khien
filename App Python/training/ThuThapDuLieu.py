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
		self.fields = ('Tổng lượng nước đã tưới', 'Nhiệt độ', 'Độ ẩm')
		self.entries = {}
		self.frame = None
		self.buttonFrame = None
		self.canvas = None
		self.view = None
		self.timenow = ''
		self.set_time = ''
		self.temperature = 0 #set default- update sau 
		self.humidity = 0  #set default- update sau 
		self.waterflow = 0 #set default- update sau 

		self.socketIO = None
		self.app_namespace = None
 

	def app(self):
		self.socketIO = SocketIO('192.168.77.1', 3484)
		# self.socketIO = SocketIO('192.168.1.226', 3484)
		self.app_namespace = self.socketIO.define(AppNamespace, '/webapp')
		self.GUI_model()
		self.root.mainloop()
		
	def GUI_model(self):
		self.root.title("Thu thập dữ liệu")
		self.root.rowconfigure(0, weight=1)
		self.root.columnconfigure(0, weight=1)

		self.view = Frame(self.root)
		self.view.grid(row=0, column=0, sticky=tkinter.constants.NS)
		ents = self.makeform(self.view, self.fields)
		self.view.bind('<Return>', (lambda event, e = ents: fetch(e)))

		self.sumWaterFlow(self.entries)
		self.tick()

		self.buttonFrame = Frame(self.root)
		self.buttonFrame.grid(row=3, column=0, sticky=tkinter.constants.NS)
		button1 = Button(self.buttonFrame, text='Get Value',
			command=(lambda e = ents: self.get_temp_and_humi(e)))
		button1.pack(side = LEFT, padx = 5, pady = 5)
		button2 = Button(self.buttonFrame, text='Lưu giá trị',
	        command=(lambda e = ents: self.save_value(e)))
		button2.pack(side = LEFT, padx = 5, pady = 5)
		button3 = Button(self.buttonFrame, text = 'Thoát', command = self.buttonFrame.quit)
		button3.pack(side = LEFT, padx = 5, pady = 5)


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
		lab = Label(row, width=22, text="Cài đặt lượng nước tưới"+": ", anchor='w')
		ent = Entry(row)
		ent.insert(0,"0")
		btn_set_time = Button(row, text = 'Set', command=(lambda : self.set_flow(self.entries)))
		row.pack(side = TOP, fill = X, padx = 5 , pady = 5)
		lab.pack(side = LEFT)
		btn_set_time.pack(side = RIGHT)
		ent.pack(side = RIGHT, expand = YES, fill = X)
		self.entries['Set water'] = ent

		row = Frame(window)
		label_notif = Label(row, width=22, text="", anchor='w')

		label_notif1 = Label(row, width=22, anchor='w', fg = 'red')
		label_notif1.config(text = self.set_time)
		lab.pack(side = LEFT)
		row.pack(side = TOP, fill = X, padx = 5 , pady = 5)
		label_notif1.pack(side = RIGHT, expand = YES, fill = X)
		label_notif.pack()

		self.entries['Label_notif'] = (label_notif,label_notif1)
		return self.entries

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

	def set_flow(self, entries):
		self.waterflow =entries['Set water'].get()
		water = int(self.waterflow)
		entries['Label_notif'][1].config(text='Đã thực hiện', fg = 'red')
		self.send_server({'val': water})

	def get_temp_and_humi(self, entries):
		test = 'model/test.sav'
		self.receiver_server()
		check_server = pickle.load(open(test, 'rb'))
		print('Kiem tra:', check_server)
		if check_server==True:
			print('Da thuc hien')
			filename = 'model/json.sav'
			json = pickle.load(open(filename, 'rb'))
			self.temperature = json['Temp']
			self.entries['Nhiệt độ'].delete(0,END)
			self.entries['Nhiệt độ'].insert(0, self.temperature)
			self.humidity = json['Humi']
			self.entries['Độ ẩm'].delete(0,END)
			self.entries['Độ ẩm'].insert(0, self.humidity)
			entries['Label_notif'][1].config(text='Thành công', fg = 'red')
		else:
			entries['Label_notif'][1].config(text='Lỗi kết nối', fg = 'red')
		name = pickle.dump(False, open(test, 'wb'))

	def save_value(self, entries):
		df = self.read_csv_file('data')
		columns = ['temperature', 'Humidity', 'Water flow' ,'Day','Time']
		day_now = datetime.datetime.today().strftime('%d/%m/%Y')
		time_now =  datetime.datetime.today().strftime('%H:%M:%S')
		df = df[['temperature', 'Humidity', 'Water flow' ,'Day', 'Time']].values
		new = np.array([[int(self.temperature), int(self.humidity), int(self.waterflow), day_now, time_now]])
		X = np.append(df, new, axis = 0)
		df = pd.DataFrame.from_records(X, columns = columns)
		# print(df.tail())
		df.to_csv('./data/Flow.csv')
		entries['Label_notif'][1].config(text='Đã lưu giá trị', fg = 'red')

	def receiver_server(self):
		# self.socketIO.on('minh', Namespace.on_aaa_response)
		self.app_namespace.emit('Flow', 1)
		self.app_namespace.on('FArdunio', AppNamespace.on_aaa_response)
		print('dagui')
		self.socketIO.wait(seconds=3)

	def send_server(self, data):
		print('Da Send', data)
		self.app_namespace.emit('send', data)
		self.socketIO.wait(seconds=0.5)

if __name__ == "__main__":
    test = App()
    test.app()

	  
