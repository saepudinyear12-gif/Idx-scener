import pandas as pd
import requests
import yfinance as yf

# Daftar contoh saham IDX (Anda bisa menambahkannya sesuai kebutuhan)
tickers = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "BBNI.JK",
    "ASII.JK",
    "TLKM.JK",
    "GOTO.JK",
    "ADRO.JK",
    "ANTM.JK",
    "ICBP.JK",
    "UNVR.JK",
    "INDF.JK",
    "KLBF.JK",
    "SMGR.JK",
    "INKP.JK",
]

# Parameter Filter
MIN_TRANSACTION_VALUE = (
    1_000_000_000  # Minimal nilai transaksi Rp 1 Miliar
)


def run_screener():
  results = []

  for ticker in tickers:
    try:
      # Ambil data historis 60 hari terakhir agar perhitungan MACD stabil
      df = yf.download(ticker, period="60d", interval="1d", progress=False)
      if hasattr(df.columns, 'levels'):
      df.columns = df.columns.get_level_values(0)
    
      if len(df) < 35:
        continue

      # Hitung Indikator MACD (EMA 12, EMA 26, Signal 9)
      exp12 = df["Close"].ewm(span=12, adjust=False).mean()
      exp26 = df["Close"].ewm(span=26, adjust=False).mean()
      df["MACD"] = exp12 - exp26
      df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

      # Hitung rata-rata volume 20 hari ke belakang (tidak termasuk hari ini)
      df["Vol_MA20"] = df["Volume"].iloc[-21:-1].mean()

      # Ambil data hari terakhir
      last_row = df.iloc[-1]
      close_price = last_row["Close"]
      prev_close = df.iloc[-2]["Close"]
      volume = last_row["Volume"]
      vol_ma20 = last_row["Vol_MA20"]
      macd = last_row["MACD"]
      signal = last_row["Signal"]

      # Hitung Nilai Transaksi hari ini (Harga x Volume)
      transaction_value = close_price * volume

      # Kriteria Filter Lengkap:
      # 1. Harga ditutup naik dibanding hari sebelumnya
      # 2. Volume hari ini > 1.5x dari rata-rata volume 20 hari
      # 3. Nilai transaksi minimal Rp 1 Miliar (likuid & mudah exit)
      # 4. MACD berada di atas garis Signal (momentum tren naik/bullish)
      is_price_up = close_price > prev_close
      is_volume_spike = volume > (1.5 * vol_ma20)
      is_liquid = transaction_value >= MIN_TRANSACTION_VALUE
      is_macd_bullish = macd > signal

      if is_price_up and is_volume_spike and is_liquid and is_macd_bullish:
        results.append({
            "ticker": ticker,
            "close": close_price,
            "volume": volume,
            "value": transaction_value,
        })
    except Exception as e:
      print(f"Error memproses {ticker}: {e}")

  return results


def send_telegram_notification(message):
  import os

  token = os.environ.get("TELEGRAM_BOT_TOKEN")
  chat_id = os.environ.get("TELEGRAM_CHAT_ID")

  if not token or not chat_id:
    print("Token atau Chat ID Telegram belum diset di Secrets!")
    return

  url = f"https://api.telegram.org/bot{token}/sendMessage"
  payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
  requests.post(url, json=payload)


if __name__ == "__main__":
  matched_stocks = run_screener()

  if matched_stocks:
    msg = "🚨 *Sinyal Screener Saham IDX (Trend Bullish)* 🚨\n\n"
    for stock in matched_stocks:
      val_in_billion = stock["value"] / 1_000_000_000
      msg += (
          f"• *{stock['ticker']}*\n  Harga: {stock['close']:.2f}\n  Transaksi:"
          f" Rp {val_in_billion:.2f} Miliar\n  Status: Konfirmasi MACD Naik"
          " 📈\n\n"
      )
    send_telegram_notification(msg)
  else:
    print(
        "Tidak ada saham yang memenuhi kriteria (Volume + Transaksi >= 1M +"
        " MACD Bullish) hari ini."
    )
      
