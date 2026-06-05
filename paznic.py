import os
import requests
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockSnapshotRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
data_client = StockHistoricalDataClient(
    os.environ['ALPACA_API_KEY'], os.environ['ALPACA_SECRET_KEY']
)

def trimite_alerta(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": text})

watchlist = ["MU","SNDK","MRVL","ARM","AVGO","DELL","WDC","STX","CSCO","CIEN","LITE"]
TOLERANTA = 1.02

snapshots = data_client.get_stock_snapshot(
    StockSnapshotRequest(symbol_or_symbols=watchlist, feed=DataFeed.IEX)
)
bars = data_client.get_stock_bars(
    StockBarsRequest(symbol_or_symbols=watchlist, timeframe=TimeFrame.Day,
                     start=datetime.now() - timedelta(days=40), feed=DataFeed.IEX)
).df

stabilizat_list, in_cadere_list = [], []
for sym in watchlist:
    snap = snapshots.get(sym)
    if not snap or snap.latest_trade is None or sym not in bars.index.get_level_values(0):
        continue
    pret = snap.latest_trade.price
    closes = bars.loc[sym]["close"]
    sma20 = closes.tail(20).mean()
    sma5  = closes.tail(5).mean()
    in_zona = pret <= sma20 * TOLERANTA
    stabilizat = pret >= sma5
    if in_zona and stabilizat:
        stabilizat_list.append(f"{sym}: {pret:.2f} (media20: {sma20:.2f})")
    elif in_zona:
        in_cadere_list.append(f"{sym}: {pret:.2f} (media20: {sma20:.2f})")

if in_cadere_list:
    trimite_alerta("📉 In zona (la media de 20), dar inca scade — urmareste:\n" + "\n".join(in_cadere_list))
if stabilizat_list:
    trimite_alerta("✅ In zona SI se stabilizeaza — posibil moment de intrare:\n" + "\n".join(stabilizat_list))

print("Verificare terminata.")
