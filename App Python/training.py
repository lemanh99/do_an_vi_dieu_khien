import pandas as pd 
import os
import pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split 

root = 'data'
def read_csv_file(root):
	csv_path = os.path.join(root, 'Flow.csv')
	df = pd.read_csv(csv_path)
	return df
def extract_training_data(df):
	features = df[['temperature', 'humidity','capacity']]
	labels = df['water flow']
	X = features.values
	y = labels.values
	return X, y

def train(X, y):
	reg = LinearRegression()
	reg.fit(X, y)
	return reg 

def model_evaluation(X, y, reg):
	predict_test = reg.predict(X)
	# print(X[0], predict_test[0])
	print("Mean Square Error:", np.sqrt(mean_squared_error(y, predict_test)))

def save_training_data(data, path):
	with open(path, 'wb') as f:
		pickle.dump(data, f)

df = read_csv_file(root)

X, y =  extract_training_data(df)
X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.1, random_state=40)
reg = train(X_train, y_train)
# y_pred = reg.predict([[29, 44, 300]])
# print(y_pred)
filename = 'model/finalized_model.sav'
save_training_data(reg, filename)
model_evaluation(X_test, y_test, reg)