import os
import asyncio
import pandas as pd
import yfinance as yf
from telegram import Bot

# Token & Chat ID Telegram Anda
TELEGRAM_BOT_TOKEN = "8694938627:AAHFF-uRBgSZIWFHK941fMMKglZIeZtAeVw"
TELEGRAM_CHAT_ID = "1768576462"

# Watchlist Saham (Bluechip + Gorengan / Lapis 2 & 3)
WATCHLIST = [
    "TLKM.JK", "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "UNVR.JK", "PGAS.JK",
    "BUMI.JK", "BRMS.JK", "DOOH.JK", "HUMI.JK", "STRK.JK", "GOTO.JK", 
    "PNLF.JK", "ADRO.JK", "ANTM.JK", "ICBP.JK", "ENRG.JK", "DEWA.JK"
]

def check_stock_signal(ticker_symbol):
    try:
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="60d", interval="1d")
        if len(df) < 30:
            return None

        info = tk.info
        company_name = info.get('longName', ticker_symbol.replace('.JK', ''))

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
        prev_close = float(prev['Close'])
        volume_shares = float(latest['Volume'])
        volume_lots = int(volume_shares / 100)  # Konversi ke Lot
        vol_ma20 = float(latest['Vol_MA20'])
        ema20 = float(latest['EMA20'])
        value = close_price * volume_shares
        
        price_change = close_price - prev_close
        price_change_pct = (price_change / prev_close) * 100

        # Data Fundamental & Valuasi
        market_cap = info.get('marketCap', 0) / 1e12  # Dalam Triliun (T)
        pe = info.get('trailingPE', 'N/A')
        pbv = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity')
        roe_str = f"{roe*100:.2f}%" if roe else "N/A"
        der = info.get('debtToEquity', 'N/A')

        # Support & Resistance Otomatis dari High/Low 20 Hari terakhir
        support = round(df['Low'].tail(20).min(), 0)
        resist = round(df['High'].tail(20).max(), 0)

        # Kriteria Sinyal: Strong Bullish / Momentum Breakout
        cond_vol = volume_shares > (vol_ma20 * 1.5)
        cond_change = price_change_pct >= 3.0
        cond_rsi = float(latest['RSI14']) > 55 and float(latest['RSI14']) > float(prev['RSI14'])
        cond_macd = float(latest['MACD_Hist']) > 0
        cond_val = value >= 1_500_000_000  # Min Transaksi 1.5 Miliar

        if cond_vol and cond_change and cond_rsi and cond_macd and cond_val:
            ticker_clean = ticker_symbol.replace(".JK", "")
            news_link = f"https://www.google.com/search?q={ticker_clean}+stock+news+idx"
            
            return {
                "ticker": ticker_clean,
                "company_name": company_name,
                "price": close_price,
                "change": price_change,
                "change_pct": price_change_pct,
                "volume_lots": volume_lots,
                "market_cap": market_cap,
                "pe": f"{pe:.2f}" if isinstance(pe, (int, float)) else pe,
                "pbv": f"{pbv:.2f}" if isinstance(pbv, (int, float)) else pbv,
                "roe": roe_str,
                "der": f"{der:.2f}" if isinstance(der, (int, float)) else der,
                "support": support,
                "resist": resist,
                "news_link": news_link
            }

    except Exception as e:
        print(f"Error scanning {ticker_symbol}: {e}")
    return None

async def run_screener():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    signals = []

    print("Memindai emiten Strong Bullish VVIP...")
    for ticker in WATCHLIST:
        res = check_stock_signal(ticker)
        if res:
            signals.append(res)

    if signals:
        for s in signals:
            message = (
                f"|| <b>SCANNER VVIP — ${s['ticker']}</b> ||\n\n"
                f"🏢 <b>Emiten:</b> {s['company_name']}\n\n"
                f"📈 <b>1. SNAPSHOT HARGA</b>\n"
                f"├── Harga Live: Rp {s['price']:,.0f}\n"
                f"├── Perubahan: {s['change']:+,.0f} ({s['change_pct']:+.2f}%)\n"
                f"├── Volume: {s['volume_lots']:,} lot\n"
                f"└── Market Cap: Rp {s['market_cap']:.2f} T\n\n"
                f"💎 <b>2. VALUASI & FUNDAMENTAL</b>\n"
                f"├── P/E: {s['pe']} | P/BV: {s['pbv']}x\n"
                f"└── ROE: {s['roe']} | DER: {s['der']}x\n\n"
                f"📊 <b>3. TEKNIKAL & TREN</b>\n"
                f"├── Tren: 🚀 Strong Bullish / Momentum Breakout\n"
                f"└── Support / Resist: {s['support']:,.0f} / {s['resist']:,.0f}\n\n"
                f"🐳 <b>4. BANDARMOLOGY</b>\n"
                f"🟢 <b>Akumulasi Bandar (Markup Phase):</b>\n"
                f"Terdeteksi lonjakan volume dengan dorongan bid tebal.\n\n"
                f"📰 <b>5. BERITA</b>\n"
                f"• {s['ticker']} - Analisis Teknikal & Market Update\n"
                f"🔗 <a href='{s['news_link']}'>Baca selengkapnya</a>"
            )
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML", disable_web_page_preview=True)
            await asyncio.sleep(1)
            
        print("Alert VVIP berhasil dikirim ke Telegram!")
    else:
        print("Belum ada emiten Strong Bullish yang memenuhi kriteria.")

if __name__ == "__main__":
    asyncio.run(run_screener())
