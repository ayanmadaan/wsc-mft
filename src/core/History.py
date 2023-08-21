import logging
import pandas as pd
from core.Controller import Controller
from models.HistoricalData import HistoricalData
from core.mapping import instrumentToken

class History:
    @staticmethod
    def getHistoricalData(tradingSymbol, from_date, to_date, interval, isFnO=False):
        broker = Controller.getBrokerName()
        brokerHandle = Controller.getBrokerLogin().getBrokerHandle()
        
        if broker == "zerodha":
            # key = ('NFO:' + tradingSymbol) if isFnO else ('NSE:' + tradingSymbol)
            bHistoryResp = brokerHandle.historical_data(
                instrument_token=instrumentToken(tradingSymbol), 
                from_date=from_date, 
                to_date=to_date, 
                interval=interval
            )
            
            # historical_data_list = []
            
            # for data_point in bHistoryResp:
            #     hData = HistoricalData(tradingSymbol)
            #     hData.date = data_point['date']
            #     hData.open = data_point['open']
            #     hData.high = data_point['high']
            #     hData.low = data_point['low']
            #     hData.close = data_point['close']
            #     hData.volume = data_point['volume']
            #     hData.oi = data_point.get('oi', 0)  # OI might not be present for all instruments
            #     historical_data_list.append(hData)
                
            # return historical_data_list
            data = pd.DataFrame(bHistoryResp)
            return data
        else:
            # Logic for other brokers can be added here
            logging.warning(f"No historical data fetching logic for broker: {broker}")
            return None
