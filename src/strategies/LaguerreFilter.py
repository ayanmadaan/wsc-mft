import logging
import datetime
from strategies.BaseStrategy import BaseStrategy
from models.Direction import Direction
from instruments.Instruments import Instruments
from models.ProductType import ProductType
from utils.Utils import Utils
from trademgmt.Trade import Trade
from ordermgmt.OrderInputParams import OrderInputParams
from trademgmt.TradeManager import TradeManager
from core.History import History
import pandas as pd
from core.mapping import instrumentToken
import numpy as np
import time


class LaguerreFilter(BaseStrategy):

    __instance = None

    @staticmethod
    def getInstance(): # singleton class
        if LaguerreFilter.__instance == None:
            LaguerreFilter()
        return LaguerreFilter.__instance
    
    def __init__(self):
        if LaguerreFilter.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            LaguerreFilter.__instance = self
        # Call Base class constructor
        super().__init__("LAGUERRE_FILTER")
        # Initialize all the properties specific to this strategy
        self.productType = ProductType.MIS
        self.symbols = ["NIFTY"]
        self.slPercentage = 0
        self.targetPercentage = 0
        self.startTimestamp = Utils.getTimeOfToDay(9, 30, 0) # When to start the strategy. Default is Market start time
        self.stopTimestamp = Utils.getTimeOfToDay(15, 20, 0) # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.squareOffTimestamp = Utils.getTimeOfToDay(15, 25, 0) # Square off time
        self.capital = 500 # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.leverage = 1 # 2x, 3x Etc
        self.maxTradesPerDay = 7 # Max number of trades per day under this strategy
        self.isFnO = True # Does this strategy trade in FnO or not
        self.capitalPerSet = 1 # Applicable if isFnO is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
        self.low_gamma_value = 0.3
        self.high_gamma_value = 0.6
        self.futureSymbol = "NIFTY23AUGFUT"
        self.prev_status = "TBD" #to be decided/started


    def canTradeToday(self):
        return True
    
    
    
    def process(self):
        # now = datetime.datetime.now()
        # if now < self.startTimestamp:
        #     return
        # if len(self.trades) >= self.maxTradesPerDay:
        #     return

        # futureSymbol = Utils.prepareMonthlyExpiryFuturesSymbol('NIFTY')
        # prev_status = "TBD" #to be decided/started

        # Fetch historical data
        from_date = datetime.datetime.now().strftime('%Y-%m-%d')
        to_date = datetime.datetime.now().strftime('%Y-%m-%d')
        data = History.getHistoricalData(self.futureSymbol, to_date, from_date, "minute")
        # for point in historical_data:
        #     print(point.date, point.open, point.high, point.low, point.close, point.volume)
        # print(historical_data)
        # # Convert historical data to a DataFrame
        # data = {
        #     'Date': [point.date for point in historical_data],
        #     'Open': [point.open for point in historical_data],
        #     'High': [point.high for point in historical_data],
        #     'Low': [point.low for point in historical_data],
        #     'Close': [point.close for point in historical_data],
        #     # 'Volume': [point.volume for point in historical_data],
        #     # 'OI': [point.oi for point in historical_data]
        # }
        # # print(data)
        df = pd.DataFrame(data)
        
        low_gamma = self.laguerre_rsi(df, self.low_gamma_value)
        high_gamma = self.laguerre_rsi(df, self.high_gamma_value)

        df_new = pd.DataFrame()
        df_new['low_gamma'] = low_gamma
        df_new['high_gamma'] = high_gamma

        latest_signal = self.check_signal(df_new)

        print(f'latest signal is {latest_signal} @ {datetime.datetime.now()}')

        if latest_signal == "LONG":

            if self.prev_status == "TBD":
                orderStatus = self.buyCall()
                if orderStatus == True:
                    print('bought fresh call')
                    self.prev_status = "LONG"
                else:
                    pass

            if self.prev_status == "SHORT":

                orderStatus = self.sellPut()
                if orderStatus == True:
                    print('we had a put option, sold now, taking new position')
                    newOrder = self.buyCall()
                    if newOrder == True:
                        print('took a new position, bought a call now')
                        self.prev_status = "LONG"
                else:
                    print('could not sell put')

            if self.prev_status == "LONG":
                pass

        if latest_signal == "SHORT":

            if self.prev_status == "TBD":
                orderStatus = self.buyPut()
                if orderStatus:
                    print('bought fresh put')
                    self.prev_status = "SHORT"
                else:
                    pass

            if self.prev_status == "LONG":

                orderStatus = self.sellCall()
                if orderStatus == True:
                    print('we had a call option, sold now, taking new position')
                    newOrder = self.buyPut()
                    if newOrder:
                        print('took a new position, bought a put now') 
                        self.prev_status = "SHORT"  

        if latest_signal == "KEEP":
            print('no signal, keeping the position as it is')
            pass      

        time.sleep(60)



    def laguerre_rsi(self, stock, GAMMA = 0.4) -> pd.DataFrame:
        stock_data = (stock)
        n = len(stock_data)

        l0, l1, l2, l3, cu, cd, rsi = [0] * n, [0] * n, [0] * n, [0] * n, [0] * n, [0] * n, [0] * n

        close = stock_data["close"].values
        high = stock_data["high"].values
        low = stock_data["low"].values

        p = (close + high + low) / 3

        for i in range(1, n):
            l0[i] = (1 - GAMMA) * p[i] + GAMMA * l0[i - 1]
            l1[i] = -GAMMA * l0[i] + l0[i - 1] + GAMMA * l1[i - 1]
            l2[i] = -GAMMA * l1[i] + l1[i - 1] + GAMMA * l2[i - 1]
            l3[i] = -GAMMA * l2[i] + l2[i - 1] + GAMMA * l3[i - 1]

            if l0[i] > l1[i]:
                cu[i] = l0[i] - l1[i]
            else:
                cd[i] = l1[i] - l0[i]

            if l1[i] > l2[i]:
                cu[i] += l1[i] - l2[i]
            else:
                cd[i] += l2[i] - l1[i]

            if l2[i] > l3[i]:
                cu[i] += l2[i] - l3[i]
            else:
                cd[i] += l3[i] - l2[i]

            if cu[i] + cd[i] != 0:
                rsi[i] = (cu[i] / (cu[i] + cd[i])) * 100

        stock_data[f"RSI"] = rsi
        stock_data = stock_data[10:]

        return stock_data["RSI"]
    

    def check_signal(self, df):

        # df = df.tail(5)

        # low_gamma = df['low_gamma']
        # high_gamma = df['high_gamma']

        signal = pd.DataFrame()
        signal.index = df.index

        signal['signal_gen'] = [0]*len(signal)

        signal['signal_gen'] = np.where(((df['low_gamma'].shift(2) <= df['high_gamma'].shift(2)) & (df['high_gamma'].shift(1) < df['low_gamma'].shift(1))), 1, np.where(((df['low_gamma'].shift(2) >= df['high_gamma'].shift(2)) & (df['high_gamma'].shift(1) > df['low_gamma'].shift(1))), -1, 0))

        #value of signal_gen column in last row of signal dataframe
        latest_signal = signal['signal_gen'].iloc[-1]

        if latest_signal == 1:
            return "LONG"

        if latest_signal == -1:
            return "SHORT"
        
        if latest_signal == 0:
            return "KEEP"
        

    def placeBuyOrder(self, tradingSymbol, qty=1):

        trade = Trade(tradingSymbol)
        trade.strategy = self.getName()
        trade.direction = Direction.LONG
        trade.productType = self.productType
        trade.placeMarketOrder = True
        
        isd = Instruments.getInstrumentDataBySymbol(tradingSymbol)

        trade.qty = isd['lot_size']*qty
        trade.stopLoss = 0
        trade.target = 0

        trade.intradaySquareOffTimestamp = Utils.getEpoch(self.squareOffTimestamp)

        # TradeManager.addNewTrade(trade)

        status = TradeManager.executeTrade(trade)

        return status

        # return True



    def placeSellOrder(self, tradingSymbol, qty=1):

        trade = Trade(tradingSymbol)
        trade.strategy = self.getName()
        trade.direction = Direction.SHORT   
        trade.productType = self.productType
        trade.placeMarketOrder = True
        
        isd = Instruments.getInstrumentDataBySymbol(tradingSymbol)

        trade.qty = isd['lot_size']*qty
        trade.stopLoss = 0
        trade.target = 0

        trade.intradaySquareOffTimestamp = Utils.getEpoch(self.squareOffTimestamp)

        status = TradeManager.addNewTrade(trade)

        return status
        # return True

    def buyPut(self, tradingSymbol="NIFTY23AUG19100PE"):

        orderStatus = self.placeBuyOrder(tradingSymbol,2)

        return orderStatus


    def sellPut(self, tradingSymbol="NIFTY23AUG19100PE"):

        orderStatus = self.placeSellOrder(tradingSymbol,2)

        return orderStatus
    
    def buyCall(self, tradingSymbol="NIFTY23AUG19650CE"):
        
        orderStatus = self.placeBuyOrder(tradingSymbol,2)

        return orderStatus
    
    def sellCall(self, tradingSymbol="NIFTY23AUG19650CE"):
        
        orderStatus = self.placeSellOrder(tradingSymbol,2)

        return orderStatus
    
    def shouldPlaceTrade(self, trade, tick):
        
        if super().shouldPlaceTrade(trade, tick) == False:
            return False
        return True
    
    

