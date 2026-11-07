# kite-first-order

Your first Zerodha Kite Connect calls in Python. You log in, read your profile, cash and holdings, then place one limit buy of 1 share and cancel it right away.

It runs on a mock account by default, so you can try every step with no Zerodha login, no network and no real order. The mock has the same method names as the `kiteconnect` library, and its responses are copied from the examples in the [Kite Connect docs](https://kite.trade/docs/connect/v3/).

This is a technical tutorial only. It is not investment advice.

## Files

| File | What it does |
|---|---|
| `first_order.py` | Reads your account, then places and cancels one order |
| `mock_kite.py` | The mock account: no login, no network, no real orders |
| `auth.py` | Logs in to your own Zerodha account and saves today's access token |
| `output_mock.txt` | What the three mock runs print |

## Run it on the mock account

You need Python 3.10 or later. The mock needs no packages.

```bash
python3 first_order.py --mock
```

This prints the profile, the cash, the holdings, and the error you get for a live price on the free Personal app:

```
Logged in as AB1234 | exchanges: BFO, MCX, NSE, CDS, BSE, BCD, MF, NFO
Cash available for equity: 99725.05
Holdings: 2
   AARON: 1 shares, bought at 161.00, now 352.95
   SBIN: 16 shares, bought at 801.78, now 762.45
Live price: Insufficient permission for that call. (the free Personal app has no market data)
```

Add a symbol and a price to place one limit buy of 1 share (product CNC), then cancel it:

```bash
python3 first_order.py SBIN 300 --mock
```

```
Placed order 171229000724687 | BUY 1 SBIN LIMIT 300.0
Status: PUT ORDER REQ RECEIVED -> VALIDATION PENDING -> OPEN PENDING -> OPEN
After cancel: CANCELLED | cancelled quantity: 1
```

Add `--wrong-ip` to see the error Kite returns when the order comes from an IP address you have not allowed for your app.

## Run it on your own account

1. Create a Personal app on the [Kite developer console](https://developers.kite.trade/). Set the redirect URL to `http://127.0.0.1:5000`.
2. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in `API_KEY` and `API_SECRET` from the app page.
4. Log in. This opens Zerodha's login page in your browser and saves the token to `access_token.txt`:
   ```bash
   python3 auth.py
   ```
5. Run the same commands without `--mock`.

## What to know

- **The token expires every morning.** The access token stops working at 6 AM the next day, so you run `auth.py` once a day.
- **The free Personal app has no market data.** `kite.ltp()` fails with "Insufficient permission for that call", so you type the price yourself. Live prices need the paid Connect plan.
- **Orders need an allowed IP.** Kite accepts orders only from the static IP addresses you add on the developer console. From any other IP, the order fails with the error shown by `--wrong-ip`.
- **The price you type is a real limit.** A limit buy far below the last price, like SBIN at 300, stays open and does not fill, which is why the script cancels it. A price at or above the last price can fill before the cancel.
- **Keep `.env` and `access_token.txt` private.** Both are in `.gitignore`.

## Try next

Change the order to a sell of a share you already hold. Use `TRANSACTION_TYPE_SELL` and add it to `mock_kite.py` first.
