#!/anaconda3/bin/python python

import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import datetime
import robin_stocks as r
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.dates as mdates


# Log into robinhood
#login = r.login('USERNAME','PASSWORD')

ts = TimeSeries(key='MB5I6W5X4BYKZ7TA',output_format='pandas')

stock = 'SNAP'
data, meta_data = ts.get_intraday(symbol=stock,interval='1min', outputsize='full')
#print(data)
close = data['4. close']
ma_21 = data['4. close'].rolling(window=100).mean()
ma_7 = data['4. close'].rolling(window=25).mean()

# Pulling daily RSI data from StockTA 
page_link = "http://www.stockta.com/cgi-bin/analysis.pl?symb=aapl&table=rsi&mode=table"

page_response = requests.get(page_link,timeout=5)

page_content = BeautifulSoup(page_response.content, "html.parser")


rsi_box = page_content.find('td',attrs={'class':'borderTd'})

rsi1 = rsi_box.text.strip()

#print(rsi1) # Daily RSI

rsi = np.zeros_like(close)

#Creating own RSI Function
def rsiFunc(prices,n=14):
	deltas = np.diff(prices)
	seed = deltas[:n+1]
	up = seed[seed>=0].sum()/n
	down = -seed[seed<0].sum()/n
	rs = up/down
	
	rsi[:n] = 100. - 100./(1.+rs)

	for i in range(n,len(prices)):
		delta = deltas[i-1]
		if delta > 0:
			upval = delta
			downval = 0.
		else:
			upval = 0
			downval = -delta

		up = (up*(n-1)+upval)/n
		down = (down*(n-1)+downval)/n

		rs = up/down
		rsi[i] = 100. - 100./(1.+rs)
	return rsi

rsiFunc(close)


golden_chart = pd.DataFrame({ 'Close': close,
						'21_Hour_MA_Close': ma_21,
						'7_Hour_MA_Close': ma_7})

rsi_chart = pd.DataFrame({'close':close,
						'rsi':rsi})

#print(golden_chart) # Print Golden Data
#print(rsi_chart) # Print RSI Data

golden_chart.plot(title = 'Golden Chart ' + stock)

rsi_chart.plot(title='RSI Chart '+ stock)

close_str = str(close[-1])


### Took away Golden Cross for now to test RSI
# Did a Godlen cross occur
#if(ma_7[-1]<ma_21[-1] and ma_7[-2]<ma_21[-2]):
#	print("Slow MA above Fast MA")
#if(ma_7[-1]<ma_21[-1] and ma_7[-2]>ma_21[-2] and rsi > 70):
#	# SELL STOCK
#	#r.order_sell_market(stock,1) 
#	print('Sell Stock at golden:'+ close_str)
#	
#if(ma_7[-1] > ma_21[-1] and ma_7[-2]<ma_21[-2] and rsi < 30):
#	# BUY STOCK
#	#r.order_buy_market(stock,1) 
#	print("Buy Stock at golden:"+close_str)

#if(ma_7[-1]>ma_21[-1] and ma_7[-2]>ma_21[-2]):
#	print("Fast MA above Slow MA")

# Did a RSI cross occur
if(rsi[-1]>70 and rsi[-2]>70):
	print("RSI above 70")
if(rsi[-1]>70 and rsi[-2]<70):
	# SELL STOCK
	#r.order_sell_market(stock,1) 
	print('Sell Stock at RSI:'+close_str)

	
if(rsi[-1]<30 and rsi[-2]>30):
	# BUY STOCK
	#r.order_buy_market(stock,1) 
	print("Buy Stock at RSI:"+close_str)
	

if(rsi[-1]<30 and rsi[-2]<30):
	print("RSI Below 30")
if(rsi[-1]>=30 and rsi[-2]<70):
	print("RSI Inbetween 30 and 70")

dt = datetime.datetime.now()
#print(close_str)
#print(dt)
#plt.show()
#plt.xticks()
