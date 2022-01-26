import os
from dotenv import load_dotenv
from binance.spot import Spot as Client
load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

client = Client(API_KEY, API_SECRET)

symbol = "ETHUSDT"
amount = 10
price = 2000
quantity = round(amount / price, 5)

order = client.new_order_test(
    symbol=symbol,
    side="BUY",
    type="LIMIT",
    timeInForce="GTC",
    quantity=quantity,
    price=price)

print(order)
