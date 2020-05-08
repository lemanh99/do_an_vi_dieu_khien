import pandas as pd 
import os
import pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# # clf = tree.DecisionTreeClassifier()
root = 'data'
def read_csv_file(root):
	csv_path = os.path.join(root, 'Flow.csv')
	df = pd.read_csv(csv_path)
	return df
def extract_training_data(df):
	features = df[['temperature', 'Humidity']]
	labels = df['Water flow']
	return features, labels

def train(features, labels):
	X = features.values
	Y = labels.values
	ones = np.ones((X.shape[0], 1))
	X_bar = np.concatenate((ones, X), axis = 1)
	reg = LinearRegression()
	reg.fit(X_bar, Y)
	return reg 

def model_evaluation(X, y, reg):
	predict_test = reg.predict(X)
	print("Mean Square Error:", np.sqrt(mean_squared_error(Y, predict_test)))


	# features = features.values
	# labels = labels.values
	# clf.fit(features, labels)
	# return clf
df = read_csv_file(root)
features, labels =  extract_training_data(df)
reg = train(features, labels)
filename = 'model/finalized_model.sav'
pickle.dump(reg, open(filename, 'wb'))