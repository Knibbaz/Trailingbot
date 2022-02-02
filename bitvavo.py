import os
from dotenv import load_dotenv
from python_bitvavo_api.bitvavo import Bitvavo

load_dotenv()

APIKEY = os.getenv('APIKEY')
APISECRET = os.getenv('APISECRET')

bitvavo = Bitvavo({
  'APIKEY': APIKEY,
  'APISECRET': APISECRET,
  'RESTURL': 'https://api.bitvavo.com/v2',
  'WSURL': 'wss://ws.bitvavo.com/v2/',
  'ACCESSWINDOW': 10000,
  'DEBUGGING': False
})


def getBalance(symbol): return bitvavo.balance({'symbol': symbol})[0]
def getBalance(): return bitvavo.balance({})
def getChartCandles(coin, interval): return bitvavo.candles(coin + '-EUR', interval, {})
def getOrder(coin, orderId): return bitvavo.getOrder(coin + '-EUR', orderId)
def getOpenOrders(): return bitvavo.ordersOpen({})

def placeStopLossOrder(coin, side, amount, targetPrice):
    return bitvavo.placeOrder(coin + '-EUR', side, 'stopLossLimit', { 'amount': amount, 'price': targetPrice, 'triggerAmount': targetPrice, 'triggerType': 'price', 'triggerReference': 'lastTrade'})