from trailingbot import trading
import requests
from datetime import datetime

## Bot settings
buySide = True
currentOrder = None
botMoney = 1000

markets = ["BTCUSDT", "BTCEUR", "ETHUSDT", "ETHEUR"]

day = 86400 ## Timestamp for one day
start = int(datetime.now().timestamp()) - (day * 30) ## amount days ago for today
end = int(datetime.now().timestamp()) ## Today
interval = '1d' ## Timestamp to trade on
market = "ETH" ## Market to trade on

tradesTesting = []
settingsTesting = []
resultMoneyTesting = []

print("TESTING")

def tradingTesting():
    ## Testing price variable
    maxStopLimit = 20
    stepsStopLimit = 1
    randomSettings(maxStopLimit, stepsStopLimit, False)
    
    ## Testing price fixed
    maxStopLimit = 1000
    stepsStopLimit = 100
    randomSettings(maxStopLimit, stepsStopLimit, True)

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
    testingDate = start
    while testingDate < end:
        trades, resultMoney = trading(chart, buySide, currentOrder, botMoney, BTSL, STSL, priceFixed)
        if resultMoney > botMoney: 
            tradesTesting.append(trades)
            settingsTesting.append({"market": market, "testingDate": testingDate, "end": end, "BTSL": BTSL, "STSL": STSL, "priceFixed": priceFixed})
            resultMoneyTesting.append(resultMoney)
        testingDate += day
        if len(chart) > 0: del chart[0]
        
    # Get the chartdata
    chart = requests.get("https://api.binance.com/api/v3/klines?symbol=" + market + "&interval=" + interval + "&limit=1000" + "&startTime=" + str(start * 1000) + "&endTime=" + str(end * 1000)).json()

    # Run the date backwards
    testingDate = end
    while start < testingDate:
        if len(chart) > 0: del chart[-1]
        testingDate -= day
        trades, resultMoney = trading(chart, buySide, currentOrder, botMoney, BTSL, STSL, priceFixed)
        if resultMoney > botMoney: 
            tradesTesting.append(trades)
            settingsTesting.append({"market": market, "testingDate": testingDate, "end": end, "BTSL": BTSL, "STSL": STSL, "priceFixed": priceFixed})
            resultMoneyTesting.append(resultMoney)

tradingTesting()
print()

max_value = max(resultMoneyTesting)
max_index = resultMoneyTesting.index(max_value)
print(resultMoneyTesting[max_index])
print(tradesTesting[max_index])
print(settingsTesting[max_index])

print()
print("END")