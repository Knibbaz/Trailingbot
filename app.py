import schedule
import time
import json
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import trailingbot

load_dotenv(find_dotenv())

day = 86400  # Timestamp for one day

def runBot():
    start = int(datetime.now().timestamp() - (day / 24))  # First timestamp
    end = int(datetime.now().timestamp())  # Latest timestamp

    # Bot settings
    with open('settings.json', 'r') as file:
        data = json.load(file)
        interval = data['interval']
        market = data['market']
        BTSL = data['BTSL']
        STSL = data['STSL']
        fixedPrice = data['fixedPrice']

    with open('currentState.json', 'r') as file:
        data = json.load(file)
        buySide = data['buySide']
        botMoney = data['botMoney']
        orderId = data['orderId']
        amount = data['amount']
        targetPrice = data['targetPrice']

    # Run the bot
    print(datetime.now())
    
    chart = {"market": market, "interval": interval, "start": start, "end": end}
    botSettings = {"BTSL": BTSL, "STSL": STSL, "fixedPrice": fixedPrice}
    currentState = {"buySide": buySide, "botMoney": botMoney, "orderId": orderId, "amount": amount, "targetPrice": targetPrice}

    trailingbot.startTrading(chart, currentState, botSettings)

runBot()
 
schedule.every(1).minute.do(runBot)

while True:
    schedule.run_pending()