"""A mock Kite Connect account for practice. No login, no network, no real orders.

Same method names and constants as the kiteconnect library. Every response is
copied from the examples in the Kite Connect docs (kite.trade/docs/connect/v3).
The error messages are the ones Zerodha's API returns.
"""


class MockKite:
    VARIETY_REGULAR = "regular"
    EXCHANGE_NSE = "NSE"
    TRANSACTION_TYPE_BUY = "BUY"
    PRODUCT_CNC = "CNC"
    ORDER_TYPE_LIMIT = "LIMIT"

    def __init__(self, api_key=None, personal_app=True, ip_allowed=True):
        self.personal_app = personal_app  # the free plan has no market data
        self.ip_allowed = ip_allowed      # orders need a whitelisted static IP
        self.history = []

    def set_access_token(self, token):
        pass

    # Read calls: user and portfolio docs
    def profile(self):
        return {"user_id": "AB1234", "user_name": "AxAx Bxx", "broker": "ZERODHA",
                "exchanges": ["BFO", "MCX", "NSE", "CDS", "BSE", "BCD", "MF", "NFO"],
                "products": ["CNC", "NRML", "MIS", "BO", "CO"]}

    def margins(self, segment):
        return {"enabled": True, "net": 99725.05,
                "available": {"cash": 245431.6, "live_balance": 99725.05}}

    def holdings(self):
        return [
            {"tradingsymbol": "AARON", "exchange": "NSE", "quantity": 1,
             "average_price": 161, "last_price": 352.95},
            {"tradingsymbol": "SBIN", "exchange": "BSE", "quantity": 16,
             "average_price": 801.78125, "last_price": 762.45},
        ]

    def ltp(self, *instruments):
        if self.personal_app:
            raise PermissionError("Insufficient permission for that call.")
        return {i: {"last_price": 762.45} for i in instruments}

    # Write calls: orders docs
    def place_order(self, variety, exchange, tradingsymbol, transaction_type,
                    quantity, product, order_type, price=None, **kwargs):
        if not self.ip_allowed:
            raise PermissionError(
                "IP is not allowed to place orders for this app. "
                "Update allowed IPs on the Kite developer console")
        self.order = dict(order_id="171229000724687", exchange=exchange,
                          tradingsymbol=tradingsymbol, transaction_type=transaction_type,
                          quantity=quantity, product=product, order_type=order_type,
                          price=price, pending_quantity=quantity, cancelled_quantity=0)
        for status in ("PUT ORDER REQ RECEIVED", "VALIDATION PENDING", "OPEN PENDING", "OPEN"):
            self.history.append({**self.order, "status": status})
        return self.order["order_id"]

    def order_history(self, order_id):
        return self.history

    def cancel_order(self, variety, order_id):
        self.history.append({**self.order, "status": "CANCEL PENDING"})
        self.history.append({**self.order, "status": "CANCELLED", "pending_quantity": 0,
                             "cancelled_quantity": self.order["quantity"]})
        return order_id
