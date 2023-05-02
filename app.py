import pandas as pd
import numpy as np
import altair as alt
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
    layout="wide",
    initial_sidebar_state="expanded")
 
yf.pdr_override()




tab1,tab2=st.tabs(['OPTION-CHAIN','TREND-PREDICTION'])
 

    
    
with tab1:
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
        Final_chain2=Final_chain1.rename(columns={"CE_OI":"CE Open Interest","CE_CHNG_IN_OI":"CE CHNG Open Interest","CE_VOLUME":"CE Volume","CE_LTP":"CE Last Traded Price",
                                                  "PE_OI":"PE Open Interest","PE_CHNG_IN_OI":"PE CHNG Open Interest","PE_VOLUME":"PE Volume","PE_LTP":"PE Last Traded Price"})
        ce_total_OI=Final_chain2['CE Open Interest'].values.sum()
        pe_total_OI=Final_chain2['PE Open Interest'].values.sum()
        ce_sp_OI=Final_chain2[Final_chain2['strikePrice']==sprice].values[0,1]
        pe_sp_OI=Final_chain2[Final_chain2['strikePrice']==sprice].values[0,11]
        
        maxce_OI=Final_chain2['CE Open Interest'].values.max()
        maxpe_OI=Final_chain2['PE Open Interest'].values.max()
        cestrik_OI=Final_chain2[Final_chain2['CE Open Interest']==maxce_OI].values[0,6]
        pestrik_OI=Final_chain2[Final_chain2['PE Open Interest']==maxpe_OI].values[0,6]
        
        col1, col2, col3,col4,col5,col6,col7 = st.columns(7)
        col2.metric("Max-CE Open interest",maxce_OI, delta=cestrik_OI)
        col6.metric("Max-PE Open interest",maxpe_OI, delta=pestrik_OI)
        col1.metric("Call Total Open Interest", ce_total_OI)
        col7.metric("Put Total Open Interest",pe_total_OI)
        col4.metric("Strike Price", sprice)
        col3.metric("Call Open Interest", ce_sp_OI)
        col5.metric("Put Open Interest", pe_sp_OI)

#         pd.set_option('display.max_rows', None)
        # st.write(Final_chain,200,800,)
        st.dataframe(Final_chain2,1400,800) 


        # x=Final_chain2['strikePrice']  
        # y=Final_chain2['CE Open Interest']
        # st.bar_chart(Final_chain2, x='strikePrice', y='CE Open Interest',use_container_width= True)
        # st.bar_chart(Final_chain2, x='strikePrice', y='PE Open Interest',use_container_width= True)
        coll1,coll2=st.columns(2)
        with coll1:
            fig, ax = plt.subplots()
            Final_chain2.plot.bar(x = 'strikePrice', y=['PE Open Interest','CE Open Interest'],ax=ax)
            st.pyplot(fig)

        with coll2:
            fig, ax = plt.subplots()
            Final_chain2.plot.bar(x = 'strikePrice', y=['PE Volume','CE Volume'],ax=ax)
            st.pyplot(fig)

         
