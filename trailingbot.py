#!/usr/bin/python3
import json
import requests
import bitvavo
from icecream import ic

## Timestamp for one day
day = 86400

# Get the chartdata
def getChartData(market, interval, start, end):
    chart = requests.get("https://api.binance.com/api/v3/klines?symbol=" + market + "EUR&interval=" + interval + "&limit=1000" + "&startTime=" + str(start * 1000) + "&endTime=" + str(end * 1000)).json()
    if len(chart) >= 1000: raise Exception("Not all the data is loaded. Bring the start or end date closer or increase the interval")
    del chart[-1]
    return chart

# Start trailing candles
def startTrading(chart, currentState, botSettings):
    market = chart['market']
    interval = chart['interval']
    start = chart['start']
    end = chart['end']
    
    buySide = currentState['buySide']
    botMoney = currentState['botMoney']
    orderId = currentState['orderId']
    amount = currentState['amount']
    targetPrice = currentState['targetPrice']
    
    BTSL = botSettings['BTSL']
    STSL = botSettings['STSL']
    fixedPrice = botSettings['fixedPrice']
    
    previousLow = None
    trades = []
    
    ## Check if previous order is still open
    if not orderId == None and not orderId == "TEST":
        order = bitvavo.getOrder("ETH", orderId)
        orderStatus = order['status']
        orderSide = order['side']
        ic("Previous order status", orderStatus)
        
        if orderStatus == "filled" or orderStatus == "canceled":
            filledAmount, filledPrice, payedFee = bitvavo.getOrderDetailsSorted(order)
            botMoney = round(filledAmount * filledPrice - payedFee, 2)
            
            ## Check if previous FILLED order bought or sold
            if orderSide == "buy" and orderStatus == "filled": 
                buySide = False
                updateCurrentState(buySide, botMoney, None, None, None)
            elif orderSide == "sell" and orderStatus == "filled": 
                buySide = True
                updateCurrentState(buySide, botMoney, None, None, None)
            
            ## Check if previous order was CANCELED
            if orderStatus == "canceled":
                botMoney = round(float(order['amount']) * float(order['price']), 2)
            ## Check if previous order was trying to buy or sell
                if orderSide == "buy": 
                    buySide = True
                    updateCurrentState(buySide, botMoney, None, None, None)
                elif orderSide == "sell":
                    buySide = False
                    updateCurrentState(buySide, botMoney, None, None, None)
    
    ## Get the latest chart data
    chart = getChartData(market, interval, start, end)
    
    ## If no order, create order based on the latest candle
    if orderId == None:
        timestamp = float(chart[-1][0] / 1000)
        low = float(chart[-1][3])
        ic("Creating the first order")
        
        newTargetPrice = getPossibleTargetPrice(buySide, fixedPrice, low, BTSL, STSL)
        newAmount = botMoney / newTargetPrice
        print(amount)
        
        createStopLossOrder(buySide, newAmount, newTargetPrice, orderId, checkLatestTimestamp(interval, timestamp, end), True)
    
    for candle in chart:
        timestamp = float(candle[0] / 1000)
        low = float(candle[3])
        
        ## Get the new target price
        newTargetPrice = getPossibleTargetPrice(buySide, fixedPrice, low, BTSL, STSL)
        newAmount = botMoney / newTargetPrice
        
        ## Skip first run and 
        if not previousLow == None and not targetPrice == None:
            
            ## Check if there is a buy or sell option
            if (low < previousLow and buySide and newTargetPrice < targetPrice) or (low > previousLow and not buySide and newTargetPrice > targetPrice):
                createStopLossOrder(buySide, newAmount, newTargetPrice, orderId, checkLatestTimestamp(interval, timestamp, end), False)
        previousLow=low
    
    return(trades, botMoney)

## Create orders
def createStopLossOrder(buySide, amount, targetPrice, orderId, isLatestTimestamp, isNewOrder):
    if isLatestTimestamp or isNewOrder:
        botMoney = amount * targetPrice
        
        if not orderId == None:
            response = bitvavo.cancelOrder("ETH", orderId)
            # ic(response)
            # ic("NEW AMOUNT", amount)
            # print('Canceled', response['orderId'])
            print("CANCEL ORDER ID", orderId)
            
        if buySide:
            # response = bitvavo.placeStopLossOrder("ETH", "buy", amount, targetPrice)
            # print(response)
            # orderId = response['orderId']
            # updateCurrentState(buySide, botMoney, orderId, amount, targetPrice)
            
            print("BUY STOP LOSS", amount, targetPrice)
            updateCurrentState(buySide, botMoney, "TEST", amount, targetPrice)
            
        elif not buySide:
            # response = bitvavo.placeStopLossOrder("ETH", "sell", amount, targetPrice)
            # orderId = response['orderId']
            # updateCurrentState(buySide, botMoney, orderId, amount, targetPrice)
            
            print("SELL STOP LOSS", amount, targetPrice)
            updateCurrentState(buySide, botMoney, "TEST", amount, targetPrice)

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

def getPossibleTargetPrice(buySide, fixedPrice, low, BTSL, STSL):
    if fixedPrice:
        possibleBuyOrder = low + BTSL
        possibleSellOrder = low - STSL
        
    else:
        possibleBuyOrder = low * (1 + BTSL / 100)
        possibleSellOrder = low * (1 - STSL / 100)
        
    if buySide: return float(possibleBuyOrder)
    elif not buySide: return float(possibleSellOrder)

def updateCurrentState(buySide, botMoney, orderId, amount, targetPrice):
    with open('currentState.json', 'w') as file: 
        json.dump({"buySide": buySide, "botMoney": round(botMoney, 2), "orderId": orderId, "amount": amount, "targetPrice": targetPrice}, file)
        
# def writeTrades():
#     print("TODO")