import pandas as pd 
import os
import pickle
import numpy as np
from sklearn.linear_model import LinearRegression

# clf = tree.DecisionTreeClassifier()
root = 'data'
def read_csv_file(root):
	csv_path = os.path.join(root, 'headbrain.csv')
	df = pd.read_csv(csv_path)
	return df
def extract_training_data(df):
	labels = df['Head Size(cm^3)']
	features = df['Brain Weight(grams)']
	return features, labels

def train(features, labels):
	X = features.values
	Y = labels.values
	n = len(X)
	X = X.reshape((n, 1))
	reg = LinearRegression()
	reg.fit(X, Y)
	return reg 

	# features = features.values
	# labels = labels.values
	# clf.fit(features, labels)
	# return clf

df = read_csv_file(root)
features, labels =  extract_training_data(df)
reg = train(features, labels)
filename = 'model/finalized_model.sav'
pickle.dump(reg, open(filename, 'wb'))