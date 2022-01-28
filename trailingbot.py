def trading(chart, buySide, currentOrder, botMoney, BTSL, STSL, priceFixed):
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
                createStopLossOrder(buySide, currentOrder)
                    
            ## Check if there is a buy or sell option
            if (low < previousLow and buySide and possibleBuyOrder < currentOrder) or (low > previousLow and not buySide and possibleSellOrder > currentOrder): ## BUY
                if buySide: currentOrder = possibleBuyOrder
                else: currentOrder = possibleSellOrder
                createStopLossOrder(buySide, currentOrder)
        
        ## Check if we can filled an order
        if not currentOrder == None:
            if (low > currentOrder and buySide) or (low < currentOrder and not buySide):
                side = ""
                profit = 0
                
                if buySide: 
                    side = "BOUGHT"
                    if len(trades) > 0: profit = trades[-1]['price'] / currentOrder * 100
                    botMoney = botMoney / currentOrder 
                    
                else:
                    side = "SOLD"
                    if len(trades) > 0: profit =  currentOrder / trades[-1]['price'] * 100
                    botMoney = botMoney * currentOrder 
                
                trades.append({"side": side, "price": currentOrder, "timestamp": timestamp, "botMoney": botMoney, "profitable": bool(profit > 100)})
                
                currentOrder = None
                buySide = not buySide
                
        previousLow=low
    return(trades, botMoney)

## Create (test) orders
def createStopLossOrder(buySide, order):
    order = round(order, 2)
    # if buySide: print("BSL at", order)
    # else: print("SSL at", order)