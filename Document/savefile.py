import pandas as pd 
import os

root = 'data'
def read_csv_file(root):
   csv_path = os.path.join(root, 'headbrain.csv')
   df = pd.read_csv(csv_path)
   return df
df = read_csv_file(root)
print(df.columns)

row_df = pd.DataFrame([1, 1, 4563, 2345])
df = df.append({'Gender':1 , 'Age Range':1, 'Head Size(cm^3)':300,'Brain Weight(grams)':400} , ignore_index=True)
print(df.iloc[-1:])
df.to_csv('./data/headbrain.csv')
