#!/usr/bin/python3
import requests
from datetime import datetime
import bitvavo

day = 86400 ## Timestamp for one day

interval = '15m' ## Timestamp to trade on
start = int(datetime.now().timestamp()) - (day * 30) ##
end = int(datetime.now().timestamp()) ##
market = "ETH" ## Market to trade on

tradingExchange = "Bitvavo"

# Get the chartdata
chart = requests.get("https://api.binance.com/api/v3/klines?symbol=" + market + "EUR&interval=" + interval + "&limit=1000" + "&startTime=" + str(start * 1000) + "&endTime=" + str(end * 1000)).json()

def trading(buySide, currentOrder, botMoney, BTSL, STSL, priceFixed):
    previousLow = None
    trades = []
    
    for candle in chart:
        timestamp = float(candle[0] / 1000)
        low = float(candle[3])
        
        if priceFixed:
            possibleBuyOrder = low + BTSL
            possibleSellOrder = low - STSL
        else:
            possibleBuyOrder = low * (1 + BTSL / 100)
            possibleSellOrder = low * (1 - STSL / 100)
        
        ## Skip first run
        if not previousLow == None:
            
            ## For creating the first order or after bought/sold
            if currentOrder == None and (low < previousLow and buySide or low > previousLow and not buySide):
                currentOrder = possibleBuyOrder
                createStopLossOrder(buySide, currentOrder, timestamp)
                    
            ## Check if there is a buy or sell option
            if (low < previousLow and buySide and possibleBuyOrder < currentOrder) or (low > previousLow and not buySide and possibleSellOrder > currentOrder): ## BUY
                if buySide: currentOrder = possibleBuyOrder
                else: currentOrder = possibleSellOrder
                createStopLossOrder(buySide, currentOrder, timestamp)
        
         ## Check if we can filled an order
        if not currentOrder == None:
            if (low > currentOrder and buySide) or (low < currentOrder and not buySide): ##
                string = ""
                profit = 0
                
                if buySide: 
                    string = "BOUGHT"
                    if len(trades) > 0: profit = trades[-1]['price'] / currentOrder * 100
                    botMoney = botMoney / currentOrder 
                    
                else:
                    string = "SOLD"
                    if len(trades) > 0: profit =  currentOrder / trades[-1]['price'] * 100
                    botMoney = botMoney * currentOrder 
                
                trades.append({"side": string, "price": currentOrder, "timestamp": timestamp, "botMoney": botMoney, "profitable": bool(profit > 100)})
                
                print(string, round(currentOrder, 2), round(botMoney, 2))
                
                currentOrder = None
                buySide = not buySide
                
        previousLow=low
    print()
    return(trades, botMoney)

## Create (test) orders
def createStopLossOrder(buySide, order, timestamp):
    order = round(order, 2)
    if buySide: print("BSL at", order)
    else: print("SSL at", order)
    
    exchange = getExchange()
    
    ## FIX BASED ON INTERVAL
    if timestamp >= datetime.now().timestamp() - day:
        print("Place real order")
        result = exchange.placeStopLossOrder("ETH", "sell", 0.02, 2700)
        print(result)
        
def getExchange():
    if tradingExchange == "Bitvavo": return bitvavo

def isItBetweenTheInterval(currentTimestamp):
    if interval == "15m": return currentTimestamp >= datetime.now().timestamp() - (day / 24 / 60 * 15)
    if interval == "30m": return currentTimestamp >= datetime.now().timestamp() - (day / 24 / 60 * 30)
    if interval == "1h": return currentTimestamp >= datetime.now().timestamp() - (day / 24)
    if interval == "4h": return currentTimestamp >= datetime.now().timestamp() - (day / 24 * 4)
    if interval == "8h": return currentTimestamp >= datetime.now().timestamp() - (day / 24 * 8)
    if interval == "1d": return currentTimestamp >= datetime.now().timestamp() - day

## Bot settings
BTSL = 10 ## Percentage or fixed price above low to buy.
STSL = 7.5 ## Percentage or fixed price below low to sell.
priceFixed = False ## Set if you want to use percentage or fixed price for placing orders.
buySide = True ## Do you want to start with buying (True) or with selling (False).
currentOrder = None ## If have running orders, set its price here. Otherwise set it to None.
botMoney = 1000 ## The amount of money the bot can play with. If you own crypto already, you can put the amount here and must set buySide to False.

## Run the bot
# trades, botMoney = trading(buySide, currentOrder, botMoney, BTSL, STSL, priceFixed)
# print(trades)

# ## If recently bought, multiply the amount bought by the latest closing rate
# if trades[-1]['side'] == "BOUGHT": botMoney = botMoney * float(chart[-1][4])
# print("\nResult:", botMoney)

intervalThingy(datetime.now().timestamp() - (day / 5))