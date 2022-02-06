#!/usr/bin/python3
import json
import requests
import bitvavo
from icecream import ic

day = 86400 ## Timestamp for one day

# Get the chartdata
def getChartData(market, interval, start, end):
    chart = requests.get("https://api.binance.com/api/v3/klines?symbol=" + market + "EUR&interval=" + interval + "&limit=1000" + "&startTime=" + str(start * 1000) + "&endTime=" + str(end * 1000)).json()
    if len(chart) >= 1000: raise Exception("Not all the data is loaded. Bring the start or end date closer or increase the interval")
    return chart

def startTrading(market, interval, start, end, buySide, currentOrder, botMoney, BTSL, STSL, fixedPrice, orderId):
    previousLow = None
    trades = []
    
    ## MAKE A FUNCTION FOR THIS
    ## Check if previous order is still open
    if not orderId == None:
        ic("Check order")
        response = bitvavo.getOrder("ETH", orderId)
        ic("Order", response['status'])
        
        if response['status'] == "filled" or response['status'] == "canceled":
            currentOrder = None
            orderId = None
            
            if buySide:
                ic("Previous buy order is filled")
                buySide = False
                # botMoney = ?
            
            if not buySide:
                ic("Previous sell order is filled")
                buySide = True
                botMoney = float(response['filledAmountQuote'])
            
            if response['status'] == "canceled":
                if response['side'] == "buy": 
                    buySide = True
                    botMoney = float(response['amount'] * response['price'])
                    
                if response['side'] == "sell": 
                    buySide = False
                    botMoney = float(response['amount'])
            
            updateSettings(buySide, botMoney, currentOrder, orderId)
    
    ic("Get chart data")
    chart = getChartData(market, interval, start, end)
    ic("Chart length", len(chart))
    
    ## If no order, create order based on the latest candle
    if currentOrder == None:
        timestamp = float(chart[-1][0] / 1000)
        low = float(chart[-1][3])
        ic("Creating the first order")
        if fixedPrice:
            possibleBuyOrder = low + BTSL
            possibleSellOrder = low - STSL
        else:
            possibleBuyOrder = low * (1 + BTSL / 100)
            possibleSellOrder = low * (1 - STSL / 100)
            
        if buySide: currentOrder = possibleBuyOrder
        else: currentOrder = possibleSellOrder
        createStopLossOrder(buySide, botMoney, currentOrder, timestamp, orderId, interval, end, True)
    
    for candle in chart:
        timestamp = float(candle[0] / 1000)
        low = float(candle[3])
        
        if fixedPrice:
            possibleBuyOrder = low + BTSL
            possibleSellOrder = low - STSL
        else:
            possibleBuyOrder = low * (1 + BTSL / 100)
            possibleSellOrder = low * (1 - STSL / 100)
        
        ## Skip first run
        if not previousLow == None:
            
            # Check if there is a buy or sell option
            if not currentOrder == None:
                if (low < previousLow and buySide and possibleBuyOrder < currentOrder) or (low > previousLow and not buySide and possibleSellOrder > currentOrder):
                    if buySide: targetPrice = possibleBuyOrder
                    else: targetPrice = possibleSellOrder
                    createStopLossOrder(buySide, botMoney, targetPrice, timestamp, orderId, interval, end, False)
                
        previousLow=low
    
    return(trades, botMoney)

## Create (test) orders
def createStopLossOrder(buySide, botMoney, order, timestamp, orderId, interval, end, isNewOrder):    
    targetPrice = int(round(order, 0))
    
    if checkLatestTimestamp(interval, timestamp, end) or isNewOrder:
        if not orderId == None:
            response = bitvavo.cancelOrder("ETH", orderId)
            print('Canceled', response['orderId'])
            
        if buySide:
            amount = float(round(botMoney / targetPrice, 5))
            response = bitvavo.placeStopLossOrder("ETH", "buy", amount, targetPrice)
            orderId = response['orderId']
            print("STOPLOSS BUY", response['market'], response['amount'], response['price'])
            
        else:
            response = bitvavo.placeStopLossOrder("ETH", "sell", botMoney, targetPrice)
            orderId = response['orderId']
            print("STOPLOSS SELL", response['market'], response['amount'], response['price'])
            
        updateSettings(buySide, botMoney, targetPrice, orderId)

def checkLatestTimestamp(interval, currentTimestamp, end):
    if interval == "1m": return currentTimestamp >= end - (day / 24 / 60)
    if interval == "5m": return currentTimestamp >= end - (day / 24 / 60 * 5)
    if interval == "15m": return currentTimestamp >= end - (day / 24 / 60 * 15)
    if interval == "30m": return currentTimestamp >= end - (day / 24 / 60 * 30)
    if interval == "1h": return currentTimestamp >= end - (day / 24)
    if interval == "2h": return currentTimestamp >= end - (day / 24 * 2)
    if interval == "4h": return currentTimestamp >= end - (day / 24 * 4)
    if interval == "6h": return currentTimestamp >= end - (day / 24 * 5)
    if interval == "8h": return currentTimestamp >= end - (day / 24 * 8)
    if interval == "12h": return currentTimestamp >= end - (day / 24 * 12)
    if interval == "1d": return currentTimestamp >= end - day

def updateSettings(buySide, botMoney, currentOrder, orderId):
    with open('botMoney.json', 'w') as file: 
        json.dump({"buySide": buySide, "botMoney": botMoney, "currentOrder": currentOrder, "orderId": orderId}, file)