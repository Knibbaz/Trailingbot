#!/usr/bin/python3
import requests
from datetime import datetime

day = 86400
interval = '1d'
start = int(datetime.now().timestamp()) - (day * 365)
end = int(datetime.now().timestamp())
market = "BTC"

# Get the chartdata
chart = requests.get("https://api.binance.com/api/v3/klines?symbol=" + market + "EUR&interval=" + interval + "&limit=1000" + "&startTime=" + str(start * 1000) + "&endTime=" + str(end * 1000)).json()

## Percentage above low to buy
## Percentage below low to sell
BTSL = 20
STSL = 10

def trading(BTSL, STSL):
    buySide = True
    previousLow = None
    currentOrder = None
    
    trades = []
    botMoney = 1000

    for candle in chart:
        timestamp = float(candle[0] / 1000)
        low = float(candle[3])
        
        possibleBuyOrder = low * (1 + BTSL / 100)
        possibleSellOrder = low * (1 - STSL / 100)
        
        ## Skip first run
        if not previousLow == None:
            
            ## For creating the first order or after bought/sold
            if currentOrder == None and (low < previousLow and buySide or low > previousLow and not buySide):
                currentOrder = possibleBuyOrder
                createStopLossOrder(buySide, currentOrder)
                    
            ## Check if there is a buy or sell option
            if (low < previousLow and buySide and possibleBuyOrder < currentOrder) or (low > previousLow and not buySide and possibleSellOrder > currentOrder): ## BUY
                if buySide: currentOrder = possibleBuyOrder
                else: currentOrder = possibleSellOrder
                createStopLossOrder(buySide, currentOrder)
        
         ## Check if we can filled an order
        if not currentOrder == None:
            if (low > currentOrder and buySide) or (low < currentOrder and not buySide): ##
                string = ""
                
                if buySide: 
                    botMoney = botMoney / currentOrder 
                    string = "BOUGHT"
                    
                else:
                    botMoney = botMoney * currentOrder 
                    string = "SOLD"
                
                trades.append({"side": string, "price": currentOrder, "timestamp": timestamp, "botMoney": botMoney})
                
                print(string, round(currentOrder, 2), round(botMoney, 2))
                
                currentOrder = None
                buySide = not buySide
                
        previousLow=low
    return(trades, round(botMoney, 2))

## Create (test) orders
def createStopLossOrder(buySide, order):
    order = round(order, 2)
    if buySide: print("BSL at", order)
    else: print("SSL at", order)
    
## Run the bot and print the results
print(trading(BTSL, STSL))