class HistoricalData:
    def __init__(self, tradingSymbol):
        self.tradingSymbol = tradingSymbol
        self.date = None
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.volume = 0
        self.oi = 0
