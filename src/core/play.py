from History import History

data = History.getHistoricalData("RELIANCE", "2023-08-07", "2023-08-07", "minute")
for point in data:
    print(point.date, point.open, point.high, point.low, point.close, point.volume)
