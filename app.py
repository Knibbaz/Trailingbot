import time
import json
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import trailingbot

load_dotenv(find_dotenv())

day = 86400 ## Timestamp for one day
count = 0

while True:
    start = int(datetime.now().timestamp() - (day / 24)) ## First timestamp
    end = int(datetime.now().timestamp()) ## Latest timestamp
    
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
    
    ## Run the bot
    print(count)
    print(datetime.now())
    result = trailingbot.startTrading(market, interval, start, end, buySide, currentOrder, botMoney, BTSL, STSL, fixedPrice, orderId)
    print(result)
    time.sleep(60 * 5)
    count += 1