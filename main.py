import os
import asyncio
import pandas as pd
import yfinance as yf
from telegram import Bot

# Token & Chat ID Telegram Anda
TELEGRAM_BOT_TOKEN = "8694938627:AAHFF-uRBgSZIWFHK941fMMKglZIeZtAeVw"
TELEGRAM_CHAT_ID = "1768576462"

# Daftar emiten IDX yang ingin dipindai
WATCHLIST = [
    "TLKM.JK", "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", 
    "PGAS.JK", "UNVR.JK", "ADRO.JK", "ANTM.JK", "ICBP.JK"
]

def check_stock_signal(ticker_symbol):
    try:
        df = yf.download(ticker_symbol, period="60d", interval="1d", progress=False)
        if len(df) < 30:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()

        # MACD (12, 26, 9)
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = macd_line - signal_line

        # RSI (14)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI14'] = 100 - (100 / (1 + rs))

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        close_price = float(latest['Close'])
        volume = float(latest['Volume'])
        vol_ma20 = float(latest['Vol_MA20'])
        ema20 = float(latest['EMA20'])
        value = close_price * volume
        price_change_pct = ((close_price - float(prev['Close'])) / float(prev['Close'])) * 100

        # Kriteria Screener "HAKA / Breakout Momentum"
        cond_macd_hist = float(latest['MACD_Hist']) > 0
        cond_vol = volume > (vol_ma20 * 2.0)                                    # Volume meledak minimal 2x lipat
        cond_ema = close_price > ema20                                          # Harga di atas tren
        cond_val = value >= 5_000_000_000                                       # Likuiditas minimal 5 Miliar
        cond_change = price_change_pct >= 3.0                                   # Harga sedang melesat kuat min. +3%
        cond_rsi = float(latest['RSI14']) > 50 and float(latest['RSI14']) > float(prev['RSI14']) # RSI kuat & menanjak

        if cond_macd_hist and cond_vol and cond_ema and cond_val and cond_change and cond_rsi:
            return {
                "ticker": ticker_symbol.replace(".JK", ""),
                "price": close_price,
                "change": price_change_pct,
                "rsi": float(latest['RSI14']),
                "volume_surge": volume / vol_ma20
            }
    except Exception as e:
        print(f"Error scanning {ticker_symbol}: {e}")
    return None

async def run_screener():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    signals = []

    print("Memulai proses pemindaian momentum HAKA...")
    for ticker in WATCHLIST:
        res = check_stock_signal(ticker)
        if res:
            signals.append(res)

    if signals:
        message = "🔥 *SINYAL BREAKOUT / READY TO HAKA* 🔥\n\n"
        for s in signals:
            message += (
                f"📌 *{s['ticker']}*\n"
                f"• Harga: Rp {s['price']:,.0f} ({s['change']:+.2f}%)\n"
                f"• Lonjakan Volume: {s['volume_surge']:.1f}x dari rata-rata\n"
                f"• RSI 14: {s['rsi']:.1f} (Strong Momentum)\n"
                f"• Status: Gas HAKA / Buy on Breakout! 🚀\n\n"
            )
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
        print("Pesan alert HAKA berhasil dikirim ke Telegram!")
    else:
        print("Belum ada emiten yang memenuhi kriteria breakout hari ini.")

if __name__ == "__main__":
    asyncio.run(run_screener())
