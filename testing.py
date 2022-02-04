import os
from numpy import char
import requests
from trailingbot import trading
from datetime import datetime

## Bot settings
buySide = True
currentOrder = None
botMoney = 1000

hour = 3600 ## Seconds in an hour
day = 86400 ## Seconds in a days

start = int(datetime.now().timestamp()) - (day * 365) ## amount days ago for today
end = int(datetime.now().timestamp()) ## Today
interval = '15m' ## Timestamp to trade on
markets = ["ETHUSDT"]

maxStopLimit = 5
stepsStopLimit = 1
priceFixed = False

# maxStopLimit = float(os.environ['MSL'])
# stepsStopLimit = float(os.environ['SSL'])
# priceFixed = bool(os.environ["PF"])
# start = int(os.environ['START'])
# end = int(os.environ['END'])
# interval = os.environ['INT']

############################################
## Find most profitable per interval, market
############################################

tradesMade = []
settingsUsed = []
profitsEarned = []

print("TESTING")

def randomSettings(maxStopLimit, stepsStopLimit, priceFixed):
    BTSL = 0
    while BTSL <= maxStopLimit:
        STSL = 0
        
        while STSL <= maxStopLimit:
            randomCoins(BTSL, STSL, priceFixed)
            STSL += stepsStopLimit
        
        BTSL += stepsStopLimit
     
def randomCoins(BTSL, STSL, priceFixed):
    for market in markets:
        randomDate(market, BTSL, STSL, priceFixed)
           
def randomDate(market, BTSL, STSL, priceFixed):
    # Get the chartdata
    chart = requests.get("https://api.binance.com/api/v3/klines?symbol=" + market + "&interval=" + interval + "&limit=1000" + "&startTime=" + str(start * 1000) + "&endTime=" + str(end * 1000)).json()

    # Run the date forwards
    testChart = chart
    testingDate = start
    while testingDate < end:
        testSettingsAndNewChart(testChart, BTSL, STSL, market, priceFixed)
        testingDate += day
        if len(testChart) > 0: del testChart[0]
        
    # Run the date backwards
    # Reset chart data
    testChart = chart
    testingDate = end
    while start < testingDate:
        if len(testChart) > 0: del testChart[-1]
        testingDate -= day
        testSettingsAndNewChart(testChart, BTSL, STSL, market, priceFixed)
        
def testSettingsAndNewChart(chart, BTSL, STSL, market, priceFixed):
    trades, resultMoney = trading(chart, buySide, currentOrder, botMoney, BTSL, STSL, priceFixed)
    if resultMoney > botMoney: 
        tradesMade.append(trades)
        settingsUsed.append({"market": market, "BTSL": BTSL, "STSL": STSL, "priceFixed": priceFixed, "resultMoney": resultMoney})
        profitsEarned.append(resultMoney)

def getChartData(market, interval, start, end):
    limit = 1000
    currentEnd = start
    
    if "m" in interval:
        callsPerDay = 60 / int(interval[:-1]) * 24
        callsOverTimespan = (end - start) / day
        totalCalls = callsPerDay * callsOverTimespan
        callsNeeded = totalCalls / limit
        
        calls = 0
        chart = []
        
        while calls <= callsNeeded:
            calls += 1
            
            # if calls > callsNeeded: currentEnd = end
            nextTimestamp = int(limit / callsPerDay * day)
            
            start = currentEnd
            currentEnd += nextTimestamp
            
            print(start, currentEnd)
            call = requests.get("https://api.binance.com/api/v3/klines?symbol=" + market + "&interval=" + interval + "&limit=10" + "&startTime=" + str(start * 1000) + "&endTime=" + str(currentEnd * 1000)).json()
            
            print(call[0][0] > start and call[0][0] < currentEnd)
            
            for data in call:
                chart.append(data)
        #     for candle in data:
        #         print(candle)
        #         chart.append(candle)
        
    print(callsNeeded)
    print(len(chart))

# getChartData(markets[0], interval, start, end)
## Testing price variable
# randomSettings(maxStopLimit, stepsStopLimit, priceFixed)

# Get the best amount of the array
# Get the settings for all the trades with the same outcome
# Remove these indexes from the array
# Do this for the x best amount

# max_value = max(profitsEarned)
# print(max_value)
# indexes = [i for i,val in enumerate(profitsEarned) if val==max_value]
# for i in indexes: 
#     print(settingsUsed[i])
    
# trades = 0
# profitable = 0
# for trade in tradesMade[indexes[0]]:
#     trades += 1
#     if trade['profitable']: profitable += 1
    
# # print(trades, profitable)
# print(str(float(profitable) / float(trades) * 100) + "% of the trades was profitabe")

print("END")