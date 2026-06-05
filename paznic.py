import os, json, traceback, requests
from datetime import datetime, timedelta

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')


def trimite_alerta(text):
    if TOKEN and CHAT_ID:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
        )


try:
    lipsa = [k for k in ['TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID',
                         'ALPACA_API_KEY', 'ALPACA_SECRET_KEY']
             if not os.environ.get(k)]
    if lipsa:
        trimite_alerta("Paznic: lipsesc secretele: " + ", ".join(lipsa))
        raise SystemExit("Lipsesc secrete: " + ", ".join(lipsa))

    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, StockSnapshotRequest
    from alpaca.data.timeframe import TimeFrame
    from alpaca.data.enums import DataFeed

    data_client = StockHistoricalDataClient(
        os.environ['ALPACA_API_KEY'], os.environ['ALPACA_SECRET_KEY']
    )
    watchlist = ["MU", "SNDK", "MRVL", "ARM", "AVGO", "DELL",
                 "WDC", "STX", "CSCO", "CIEN", "LITE"]
    TOLERANTA = 1.02

    try:
        with open("stare.json") as f:
            stare = json.load(f)
    except FileNotFoundError:
        stare = {}

    snapshots = data_client.get_stock_snapshot(
        StockSnapshotRequest(symbol_or_symbols=watchlist, feed=DataFeed.IEX)
    )
    bars = data_client.get_stock_bars(
        StockBarsRequest(symbol_or_symbols=watchlist, timeframe=TimeFrame.Day,
                         start=datetime.now() - timedelta(days=40), feed=DataFeed.IEX)
    ).df

    stare_noua = {}
    for sym in watchlist:
        snap = snapshots.get(sym)
        if not snap or snap.latest_trade is None or sym not in bars.index.get_level_values(0):
            continue
        pret = snap.latest_trade.price
        closes = bars.loc[sym]["close"]
        sma20 = closes.tail(20).mean()
        sma5 = closes.tail(5).mean()
        if pret <= sma20 * TOLERANTA and pret >= sma5:
            status = "stabilizat"
        elif pret <= sma20 * TOLERANTA:
            status = "in_cadere"
        else:
            status = "afara"
        stare_noua[sym] = status
        if status != stare.get(sym):
            if status == "in_cadere":
                trimite_alerta(f"📉 {sym} a intrat in zona (media de 20), inca scade — {pret:.2f}")
            elif status == "stabilizat":
                trimite_alerta(f"✅ {sym} se stabilizeaza in zona — {pret:.2f} (media20: {sma20:.2f})")

    with open("stare.json", "w") as f:
        json.dump(stare_noua, f)
    print("Verificare terminata.")

except Exception:
    trimite_alerta("Paznic EROARE:\n" + traceback.format_exc()[-500:])
    raise
