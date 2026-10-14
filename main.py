import os
import asyncio
import pandas as pd
import yfinance as yf
from telegram import Bot

# Token & Chat ID Telegram Anda
TELEGRAM_BOT_TOKEN = "8694938627:AAHFF-uRBgSZIWFHK941fMMKglZIeZtAeVw"
TELEGRAM_CHAT_ID = "1768576462"

# Watchlist Gabungan: Blue Chip + Saham Gorengan / Lapis 2 & 3 Aktif
WATCHLIST = [
    # Bluechips / Big Cap
    "TLKM.JK", "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "UNVR.JK", "PGAS.JK",
    # Saham Gorengan / High Volatility / Second-Third Liner
    "BUMI.JK", "BRMS.JK", "DOOH.JK", "HUMI.JK", "STRK.JK", "GOTO.JK", 
    "PNLF.JK", "ADRO.JK", "ANTM.JK", "ICBP.JK", "ENRG.JK", "DEWA.JK"
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

        # Filter Minimal Likuiditas Disesuaikan untuk Gorengan (Min. Transaksi Rp 1.5 Miliar)
        if value < 1_500_000_000 or close_price < (ema20 * 0.97):
            return None

        signal_type = None

        # 1. Kriteria SINYAL HAKA (Breakout Momentum Ekstrem)
        cond_haka_vol = volume > (vol_ma20 * 2.0)
        cond_haka_change = price_change_pct >= 3.0
        cond_haka_rsi = float(latest['RSI14']) > 50 and float(latest['RSI14']) > float(prev['RSI14'])
        cond_haka_macd = float(latest['MACD_Hist']) > 0

        if cond_haka_vol and cond_haka_change and cond_haka_rsi and cond_haka_macd:
            signal_type = "HAKA"

        # 2. Kriteria SINYAL SWING PENDEK (Rebound Support / Gorengan Turning Up)
        else:
            cond_swing_vol = volume > vol_ma20
            cond_swing_change = 0.5 <= price_change_pct < 4.0
            cond_swing_rsi = 35 <= float(latest['RSI14']) <= 65 and float(latest['RSI14']) > float(prev['RSI14'])
            cond_swing_macd = float(latest['MACD_Hist']) > float(prev['MACD_Hist'])

            if cond_swing_vol and cond_swing_change and cond_swing_rsi and cond_swing_macd:
                signal_type = "SWING"

        if signal_type:
            # Hitung Kalkulasi Trading Plan Swing
            buy_low = close_price * 0.99
            tp1 = close_price * 1.04   # Target 1 (+4%)
            tp2 = close_price * 1.08   # Target 2 (+8% cocok utk gorengan)
            sl = close_price * 0.96    # Stop Loss (-4%)

            return {
                "ticker": ticker_symbol.replace(".JK", ""),
                "price": close_price,
                "change": price_change_pct,
                "rsi": float(latest['RSI14']),
                "volume_surge": volume / vol_ma20,
                "type": signal_type,
                "buy_area": f"{buy_low:,.0f} - {close_price:,.0f}",
                "tp1": tp1,
                "tp2": tp2,
                "sl": sl
            }

    except Exception as e:
        print(f"Error scanning {ticker_symbol}: {e}")
    return None

async def run_screener():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    signals = []

    print("Memulai pemindaian radar (Bluechip + Gorengan)...")
    for ticker in WATCHLIST:
        res = check_stock_signal(ticker)
        if res:
            signals.append(res)

    if signals:
        message = "📊 *RADAR SAHAM IDX DETECTED* 📊\n\n"
        for s in signals:
            if s['type'] == "HAKA":
                message += (
                    f"🔥 *{s['ticker']} (SIAP HAKA / BREAKOUT)* 🔥\n"
                    f"• Harga: Rp {s['price']:,.0f} ({s['change']:+.2f}%)\n"
                    f"• Vol Surge: {s['volume_surge']:.1f}x (Meledak!)\n"
                    f"• RSI 14: {s['rsi']:.1f}\n"
                    f"• Aksi: HAKA / Scalping / Day Trade 🚀\n\n"
                )
            elif s['type'] == "SWING":
                message += (
                    f"💎 *{s['ticker']} (SWING PENDEK / REBOUND)* 💎\n"
                    f"• Harga Sekarang: Rp {s['price']:,.0f} ({s['change']:+.2f}%)\n"
                    f"• Vol Surge: {s['volume_surge']:.1f}x | RSI: {s['rsi']:.1f}\n"
                    f"-----------------------------------\n"
                    f"📌 *TRADING PLAN SWING:* \n"
                    f"• 🛒 Area Buy: Rp {s['buy_area']}\n"
                    f"• 🎯 Target TP 1 (+4%): Rp {s['tp1']:,.0f}\n"
                    f"• 🚀 Target TP 2 (+8%): Rp {s['tp2']:,.0f}\n"
                    f"• 🛑 Stop Loss (-4%): Rp {s['sl']:,.0f}\n"
                    f"• ⏱️ Estimasi Hold: 1 - 3 Hari Kerja\n\n"
                )

        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
        print("Pesan alert berhasil dikirim ke Telegram!")
    else:
        print("Belum ada emiten yang memenuhi kriteria HAKA maupun Swing hari ini.")

if __name__ == "__main__":
    asyncio.run(run_screener())
