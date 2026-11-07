"""Your first Kite Connect calls: read your account, then place and cancel one order.

Usage:
  python3 first_order.py --mock                     read only, on the mock account
  python3 first_order.py SBIN 300 --mock            also places a 1 share limit buy, then cancels it
  python3 first_order.py SBIN 300 --mock --wrong-ip the same order from an IP that is not allowed
Drop --mock to run on your own Zerodha account, after python3 auth.py.

The free Personal app has no market data, so you type the price.
This is a technical tutorial only. It is not investment advice.
"""

import json
import os
import sys
import time

args = [a for a in sys.argv[1:] if not a.startswith("--")]

if "--mock" in sys.argv:
    from mock_kite import MockKite
    kite = MockKite(ip_allowed="--wrong-ip" not in sys.argv)
else:
    from dotenv import load_dotenv
    from kiteconnect import KiteConnect
    load_dotenv()
    kite = KiteConnect(api_key=os.getenv("API_KEY"))
    kite.set_access_token(json.load(open("access_token.txt"))["access_token"])

# 1. Read: who is logged in, how much cash is free, what you hold
profile = kite.profile()
print("Logged in as", profile["user_id"], "| exchanges:", ", ".join(profile["exchanges"]))

equity = kite.margins("equity")
print("Cash available for equity:", equity["available"]["live_balance"])

holdings = kite.holdings()
print("Holdings:", len(holdings))
for h in holdings:
    print(f"   {h['tradingsymbol']}: {h['quantity']} shares, bought at {h['average_price']:.2f}, now {h['last_price']}")

try:
    kite.ltp("NSE:SBIN")
except Exception as e:
    print("Live price:", e, "(the free Personal app has no market data)")

if len(args) < 2:
    sys.exit(0)

# 2. Write: one limit buy of 1 share, cancelled right away
order = dict(
    variety=kite.VARIETY_REGULAR,
    exchange=kite.EXCHANGE_NSE,
    tradingsymbol=args[0].upper(),
    transaction_type=kite.TRANSACTION_TYPE_BUY,
    quantity=1,
    product=kite.PRODUCT_CNC,
    order_type=kite.ORDER_TYPE_LIMIT,
    price=float(args[1]),
)

try:
    order_id = kite.place_order(**order)
except Exception as e:
    print("Order failed:", e)
    sys.exit(1)

print("Placed order", order_id, "| BUY 1", order["tradingsymbol"], "LIMIT", order["price"])
time.sleep(1)
print("Status:", " -> ".join(o["status"] for o in kite.order_history(order_id)))

kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=order_id)
time.sleep(1)
last = kite.order_history(order_id)[-1]
print("After cancel:", last["status"], "| cancelled quantity:", last["cancelled_quantity"])
