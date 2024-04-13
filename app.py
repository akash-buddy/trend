import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pandas_datareader import data as pdr
import yfinance as yf
import streamlit as st
from keras.models import load_model

yf.pdr_override()

st.title('Stock Trend Prediction')

# tab1,tab2= 

end = datetime.now()
start = datetime(end.year - 10, end.month, end.day)


user_input=st.text_input("Enter Stock Ticker","AAPL")
df= pdr.get_data_yahoo(user_input, start, end)

st.subheader("Data from 2013 - Till Now")
st.write(df.describe())

st.subheader("Closing Price vs Time chart")
fig=plt.figure(figsize=(12,6))
plt.plot(df.Close,'b')
st.pyplot(fig)


st.subheader("Closing Price vs Time chart with 100MA")
ma100 = df.Close.rolling(100).mean()
fig=plt.figure(figsize=(12,6))
plt.plot(ma100,'g')
plt.plot(df.Close,'b')
st.pyplot(fig)


st.subheader("Closing Price vs Time chart with 100MA & 200MA")
ma100=df.Close.rolling(100).mean()
ma200=df.Close.rolling(200).mean()
fig=plt.figure(figsize=(12,6))
plt.plot(ma100,'g')
plt.plot(ma200,'r')
plt.plot(df.Close,'b')
st.pyplot(fig)


data_training = pd.DataFrame(df['Close'][0:int(len(df)*0.70)])
data_testing = pd.DataFrame(df['Close'][int(len(df)*0.70):int(len(df))])

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))

data_training_array = scaler.fit_transform(data_training)


model = load_model("keras_model.h5")

past_100_days = data_training.tail(100)
final_df=past_100_days.append(data_testing,ignore_index=True)
input_data = scaler.fit_transform(final_df)

x_test = []
y_test = []

for i in range(100,input_data.shape[0]):
    x_test.append(input_data[i-100:i])
    y_test.append(input_data[i,0])

x_test,y_test = np.array(x_test),np.array(y_test)

y_predicted = model.predict(x_test)

scal=scaler.scale_

scale_factor = 1/scal[0]
y_predicted=y_predicted*scale_factor
y_test=y_test*scale_factor

st.subheader("Predictions vs Original")
fig2 = plt.figure(figsize=(12,6))
plt.plot(y_test,'b',label='Original Price')
plt.plot(y_predicted,'g',label='Predicted Price')
plt.xlabel('Time')
plt.ylabel('Price')
st.pyplot(fig2)
