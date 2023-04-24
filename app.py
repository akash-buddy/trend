import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pandas_datareader import data as pdr
import yfinance as yf
import streamlit as st
from keras.models import load_model
import requests
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title='Akku-TrendPrediction',
    page_icon="chart_with_upwards_trend",
#     layout="wide",
    initial_sidebar_state="expanded")
 
yf.pdr_override()




tab1,tab2,tab3=st.tabs(['OVERVIEW','OPTION-CHAIN','TREND-PREDICTION'])
 
with tab3:
    st.title('Stock Trend Prediction')
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



    model = load_model('keras_model.h5',compile=False)

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
    plt.plot(y_predicted,'r',label='Predicted Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    st.pyplot(fig2)

    
    
    
with tab2:
    st.title("Option Chain")

    col1,col2,col3=st.columns(3)
    with col1:
        nam=st.selectbox('Symbol',('NIFTY','BANKNIFTY','FINNIFTY'))
    with col2:
        date=st.text_input("ExpiryDate")
    with col3:
        sprice=st.number_input("Strike Price")
    if st.button("Get Chain"):
        sesi=requests.Session()
        headers={}
        headers['User-agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        a=sesi.get("https://www.nseindia.com/",headers=headers)

        indices=['BANKNIFTY','FINNIFTY','NIFTY']

        def Fetchoptionchain(scrip):
            if scrip in indices:
                url=f"https://www.nseindia.com/api/option-chain-indices?symbol={scrip}"
            a=sesi.get(url,headers=headers)
            return a.json()['records']

        q=Fetchoptionchain(nam)


        def getoptionchain(name,expiry):
            option_chain = pd.DataFrame()
            option_chain_record = name
            option_chain_data = option_chain_record["data"]

            optionchain_data_df = pd.DataFrame(option_chain_data)
            option_chain_data_df = optionchain_data_df[optionchain_data_df['expiryDate']==expiry]


            OptionChain_CE = pd.DataFrame()
            OptionChain_CE['CE'] = option_chain_data_df['CE']

            OptionChain_CE_expand = pd.concat([OptionChain_CE.drop(['CE'],axis=1),
                                                OptionChain_CE['CE'].apply(pd.Series)],axis=1)

            OptionChain_PE = pd.DataFrame()
            OptionChain_PE['PE'] = option_chain_data_df['PE']


            OptionChain_PE_expand = pd.concat([OptionChain_PE.drop(['PE'],axis=1),
                                                OptionChain_PE['PE'].apply(pd.Series)],axis=1)


            option_chain['CE_OI'] = OptionChain_CE_expand['openInterest']

            option_chain['CE_CHNG_IN_OI'] = OptionChain_CE_expand['changeinOpenInterest']

            option_chain['CE_VOLUME'] = OptionChain_CE_expand['totalTradedVolume']

            option_chain['CE_IV'] = OptionChain_CE_expand['impliedVolatility']

            option_chain['CE_LTP'] = OptionChain_CE_expand['lastPrice']

            option_chain['CE_CHNG'] = OptionChain_CE_expand['change'] 

            option_chain['CE_BID_QTY'] = OptionChain_CE_expand['bidQty']

            option_chain['strikePrice'] = option_chain_data_df['strikePrice']

            option_chain['PE_BID_OTY'] = OptionChain_PE_expand['bidQty']

            option_chain['EPE_CHING'] = OptionChain_PE_expand['change']

            option_chain['PE_LTP'] = OptionChain_PE_expand['lastPrice']

            option_chain['PE_IV'] = OptionChain_PE_expand['impliedVolatility'] 

            option_chain['PE_VOLUME'] = OptionChain_PE_expand['totalTradedVolume']

            option_chain['PE_CHNG_IN_OI'] = OptionChain_PE_expand['changeinOpenInterest']

            option_chain['PE_OI'] = OptionChain_PE_expand['openInterest']

            return option_chain


        option_chain1 = getoptionchain(q,date)


        option_chain1.reset_index(inplace = True)

        a=list(option_chain1['strikePrice'])
        b=pd.DataFrame(columns=['index','CE_OI','CE_CHNG_IN_OI','CE_VOLUME','CE_IV','CE_LTP','CE_CHNG','CE_BID_QTY','strikePrice','PE_BID_OTY',
                            'EPE_CHING','PE_LTP','PE_IV','PE_VOLUME','PE_CHNG_IN_OI','PE_OI'])
        if nam=='BANKNIFTY':
            for i in a:
                if (i % 500) == 0:
                    dff = int(option_chain1[option_chain1['strikePrice']==i].index[0])
                    c=option_chain1.iloc[dff,]
                    b = b.append(c,ignore_index = True)
        else:
            for i in a:
                if (i % 100) == 0:
                    dff = int(option_chain1[option_chain1['strikePrice']==i].index[0])
                    c=option_chain1.iloc[dff,]
                    b = b.append(c,ignore_index = True)


        sp=sprice
        if nam=='BANKNIFTY':
            
            ste=str(sp)
            strin=ste[2:5]
            if strin=='100':
                sp=sp-100
            elif strin=='200':
                sp=sp-200
            elif strin=='300':
                sp=sp-300
            elif strin=='400':
                sp=sp-400
            elif strin=='600':
                sp=sp-100
            elif strin=='700':
                sp=sp-200
            elif strin=='800':
                sp=sp-300
            elif strin=='900':
                sp=sp-400

        ind_lower= int(b[b['strikePrice']==sp].index[0])
        q=b.iloc[ind_lower-6:ind_lower-1]

        df = int(option_chain1[option_chain1['strikePrice']==sp].index[0])
        r=option_chain1.iloc[df-5:df+6]

        ind_upper= int(b[b['strikePrice']==sp].index[0])
        s=b.iloc[ind_upper+2:ind_upper+7]

        t=q.append(r,ignore_index = True)
        Final_chain=t.append(s,ignore_index = True)
        
        Final_chain1=Final_chain.drop(['CE_CHNG','CE_BID_QTY','PE_BID_OTY','EPE_CHING'],axis=1)
        Final_chain1=Final_chain1.rename(columns={"CE_OI":"Open Interest","CE_CHNG_IN_OI":"CHNG Open Interest","CE_VOLUME":"Volume",
                      "CE_LTP":"Last Traded Price","PE_OI":"Open Interest","PE_CHNG_IN_OI":"CHNG Open Interest","PE_VOLUME":"Volume","PE_LTP":"Last Traded Price"})
        pd.set_option('display.max_rows', None)
        # st.write(Final_chain,200,800,)
        st.dataframe(Final_chain1,12000,800)   
    
