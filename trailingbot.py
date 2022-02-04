#!/usr/bin/python3
import json
from dotenv import load_dotenv, find_dotenv
import requests
from datetime import datetime
import bitvavo

load_dotenv(find_dotenv())

day = 86400 ## Timestamp for one day
start = int(datetime.now().timestamp()) - (day * 10) ## First timestamp
end = int(datetime.now().timestamp() - (day / 24 / 60 * 30)) ## Latest timestamp

## Bot settings
with open('settings.json', 'r') as file: data = json.load(file)
interval = data["interval"]
exchange = data["exchange"]
market = data['market']
BTSL = data['BTSL']
STSL = data['STSL']
fixedPrice = data['fixedPrice']

with open('botMoney.json', 'r') as file: data = json.load(file)
buySide = data['buySide']
botMoney = data['botMoney']
currentOrder = data['currentOrder']
orderId = data['orderId']

# Get the chartdata
chart = requests.get("https://api.binance.com/api/v3/klines?symbol=" + market + "EUR&interval=" + interval + "&limit=1000" + "&startTime=" + str(start * 1000) + "&endTime=" + str(end * 1000)).json()
if len(chart) >= 1000: raise Exception("Not all the data is loaded")

def trading(buySide, currentOrder, botMoney, BTSL, STSL, fixedPrice, orderId):
    previousLow = None
    trades = []
    
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
            
            ## For creating the first order or after bought/sold
            if currentOrder == None and (low < previousLow and buySide or low > previousLow and not buySide):
                if buySide: currentOrder = possibleBuyOrder
                else: currentOrder = possibleSellOrder

                createStopLossOrder(buySide, currentOrder, timestamp, orderId)
                
            if not currentOrder == None:
                # Check if there is a buy or sell option
                if (low < previousLow and buySide and possibleBuyOrder < currentOrder) or (low > previousLow and not buySide and possibleSellOrder > currentOrder):
                    if buySide: currentOrder = possibleBuyOrder
                    else: currentOrder = possibleSellOrder
                    createStopLossOrder(buySide, currentOrder, timestamp, orderId)
                
        previousLow=low
    
    return(trades, botMoney)

## Create (test) orders
def createStopLossOrder(buySide, order, timestamp, orderId):    
    targetPrice = int(round(order, 0))
    
    if checkLatestTimestamp(timestamp):
        
        if not orderId == None:
            print("Cancel previous order")
            response = bitvavo.cancelOrder("ETH", orderId)
            print('Deleted', response['orderId'])
        
        if buySide: 
            response = bitvavo.placeStopLossOrder("ETH", "buy", botMoney, targetPrice)
            orderId = response['orderId']
            print(response)
        
        else:
            response = bitvavo.placeStopLossOrder("ETH", "sell", botMoney, targetPrice)
            orderId = response['orderId']
            print(response)
            
        updateSettings(targetPrice, orderId)

def checkLatestTimestamp(currentTimestamp):
    if interval == "15m": return currentTimestamp >= end - (day / 24 / 60 * 15)
    if interval == "30m": return currentTimestamp >= end - (day / 24 / 60 * 30)
    if interval == "1h": return currentTimestamp >= end - (day / 24)
    if interval == "4h": return currentTimestamp >= end - (day / 24 * 4)
    if interval == "8h": return currentTimestamp >= end - (day / 24 * 8)
    if interval == "1d": return currentTimestamp >= end - day

def updateSettings(currentOrder, orderId):
    with open('botMoney.json', 'w') as file: 
        json.dump({"buySide": buySide, "botMoney": botMoney, "currentOrder": currentOrder, "orderId": orderId}, file)

## Check if previous order is still open
if not orderId == None:
    
    response = bitvavo.getOrder("ETH", orderId)
    
    if response['status'] == "filled" and buySide:
        print("Previous buy order is filled")
        print(response)
        buySide = False
        # botMoney = ?
        
    elif response['status'] == "filled" and not buySide:
        print("Previous sell order is filled")
        buySide = True
        botMoney = response['filledAmountQuote']
        
    else:
        print("Previous order is still open")

## Check if the given botMoney is available on the exchange
if buySide: exchangeMoney = float(bitvavo.getBalance("EUR")['available'])
else: exchangeMoney = float(bitvavo.getBalance(market)['available'])

if exchangeMoney <= botMoney: raise Exception("The money is not (yet) available on the account")

## Run the bot
result = trading(buySide, currentOrder, botMoney, BTSL, STSL, fixedPrice, orderId)
print(result)