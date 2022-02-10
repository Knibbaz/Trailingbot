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

    if interval == "1m": schedule.every(1).minute.do(runBot)
    if interval == "5m": schedule.every(5).minutes.do(runBot)
    if interval == "15m": schedule.every(15).minutes.do(runBot)
    if interval == "30m": schedule.every(30).minutes.do(runBot)
    if interval == "1h": schedule.every(1).hour.do(runBot)
    if interval == "2h": schedule.every(2).hours.do(runBot)
    if interval == "4h": schedule.every(4).hours.do(runBot)
    if interval == "6h": schedule.every(6).hours.do(runBot)
    if interval == "8h": schedule.every(8).hours.do(runBot)
    if interval == "12h": schedule.every(12).hours.do(runBot)
    if interval == "1d": schedule.every(1).day.do(runBot)

runBot()

while True:
    schedule.run_pending()