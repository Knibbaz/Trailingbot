import os
from dotenv import load_dotenv, find_dotenv
from python_bitvavo_api.bitvavo import Bitvavo

load_dotenv(find_dotenv())

APISECRET = os.environ.get("APISECRET")
APIKEY = os.environ.get("APIKEY")

bitvavo = Bitvavo({
  'APIKEY': APIKEY,
  'APISECRET': APISECRET,
  'RESTURL': 'https://api.bitvavo.com/v2',
  'WSURL': 'wss://ws.bitvavo.com/v2/',
  'ACCESSWINDOW': 10000,
  'DEBUGGING': False
})

def cancelOrder(coin, orderId): return bitvavo.cancelOrder(coin + '-EUR', orderId)

def getBalance(symbol): return bitvavo.balance({'symbol': symbol})[0]
# def getBalance(): return bitvavo.balance({})
def getChartCandles(coin, interval): return bitvavo.candles(coin + '-EUR', interval, {})
def getOrder(coin, orderId): return bitvavo.getOrder(coin + '-EUR', orderId)
def getOpenOrders(): return bitvavo.ordersOpen({})

def placeLimitOrder(coin, side, amount, targetPrice):
  return bitvavo.placeOrder(coin + '-EUR', side, 'limit', { 'amount': amount, 'price': targetPrice })

def placeStopLossOrder(coin, side, amount, targetPrice):
  return bitvavo.placeOrder(coin + '-EUR', side, 'stopLossLimit', { 'amount': amount, 'price': targetPrice, 'triggerAmount': targetPrice, 'triggerType': 'price', 'triggerReference': 'lastTrade'})