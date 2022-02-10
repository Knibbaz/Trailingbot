## Bot settings
BTSL = 10 ## Percentage or fixed price above low to buy.
STSL = 7.5 ## Percentage or fixed price below low to sell.
priceFixed = False ## Set if you want to use percentage or fixed price for placing orders.
buySide = True ## Do you want to start with buying (True) or with selling (False).
currentOrder = None ## If have running orders, set its price here. Otherwise set it to None.
botMoney = 1000 ## The amount of money the bot can play with. If you own crypto already, you can put the amount here and must set buySide to False.

day = 86400 ## Timestamp for one day

interval = "4h" ## Timestamp to trade on
start = int(datetime.now().timestamp()) - (day * 40) ## First timestamp
end = int(datetime.now().timestamp()) ## Latest timestamp
market = "ETH" ## Market to trade on