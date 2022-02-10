import os
from dotenv import load_dotenv, find_dotenv
from python_bitvavo_api.bitvavo import Bitvavo

load_dotenv(find_dotenv())

APIKEY = os.environ.get("APIKEY")
APISECRET = os.environ.get("APISECRET")

if APIKEY == None or APISECRET == None:
  raise Exception("API is not set, you need to create a .env file with APIKEY= and APISECRET=")

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
def getChartCandles(coin, interval): return bitvavo.candles(coin + '-EUR', interval, {})
def getOrder(coin, orderId): return bitvavo.getOrder(coin + '-EUR', orderId)
def getOpenOrders(): return bitvavo.ordersOpen({})

def placeStopLossOrder(coin, side, amount, targetPrice):
  amount = float(getRightDecimals(amount))
  targetPrice = int(getRightDecimals(targetPrice))
  
  return bitvavo.placeOrder(coin + '-EUR', side, 'stopLossLimit', { 'amount': amount, 'price': targetPrice, 'triggerAmount': targetPrice, 'triggerType': 'price', 'triggerReference': 'lastTrade'})

## Extra functions
def getOrderDetailsSorted(order):
  filledAmount = 0
  filledPrice = []
  payedFee = 0
  
  fills = order['fills']
  
  for fill in fills :
    filledAmount += float(fill['amount'])
    filledPrice.append(float(fill['price']))
    payedFee += float(fill['fee'])
  
  if len(filledPrice) > 0: filledPrice = sum(filledPrice) / len(filledPrice)
  else: filledPrice = 0
  
  return filledAmount, filledPrice, payedFee

def getRightDecimals(input):
  if input >= 100000: return round(input, 0)
  elif input >= 10000: return round(input, 1)
  elif input >= 1000: return round(input, 2)
  elif input >= 100: return round(input, 3)
  elif input >= 10: return round(input, 4)
  else: return round(input, 5)