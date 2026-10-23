import os
import asyncio
import pandas as pd
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token Telegram Bot Anda
TELEGRAM_BOT_TOKEN = "8694938627:AAHFF-uRBgSZIWFHK941fMMKglZIeZtAeVw"

def analyze_stock(ticker_symbol):
    try:
        if not ticker_symbol.endswith(".JK"):
            ticker_symbol += ".JK"
        
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="60d", interval="1d")
        if len(df) < 30:
            return None

        info = tk.info
        company_name = info.get('longName', ticker_symbol.replace('.JK', ''))

        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()

        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = macd_line - signal_line

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
        vol_ma20 = float(latest['Vol_MA20'])
        value = close_price * volume_shares
        value_miliar = value / 1e9
        
        price_change = close_price - prev_close
        price_change_pct = (price_change / prev_close) * 100

        pe = info.get('trailingPE', 'N/A')
        pbv = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity')
        roe_str = f"{roe*100:.2f}%" if roe else "N/A"

        support_zone = round(df['Low'].tail(5).min(), 0)
        resistance_zone = round(df['High'].tail(20).max(), 0)

        vol_ratio = volume_shares / vol_ma20 if vol_ma20 > 0 else 1.0
        vol_surge_pct = int((vol_ratio - 1) * 100) if vol_ratio > 1 else 0

        rsi_val = float(latest['RSI14'])
        ticker_clean = ticker_symbol.replace(".JK", "")

        signal_type = "BULLISH" if (price_change_pct >= 0 and rsi_val >= 50) else "BEARISH"
        potensi_ara = "TINGGI" if (vol_ratio >= 3.0 and price_change_pct >= 10.0) else "MENENGAH"

        return {
            "signal_type": signal_type,
            "ticker": ticker_clean,
            "company_name": company_name,
            "price": close_price,
            "change_pct": price_change_pct,
            "value_miliar": value_miliar,
            "rsi": f"{rsi_val:.1f}",
            "vol_ratio": f"{vol_ratio:.1f}",
            "vol_surge": f"{vol_surge_pct}%",
            "potensi_ara": potensi_ara,
            "support": support_zone,
            "resist": resistance_zone,
            "entry": int(close_price),
            "stop_loss": int(round(support_zone * 0.98, 0)),
            "tp1": int(resistance_zone) if resistance_zone > close_price else int(round(close_price * 1.05, 0)),
            "pe": f"{pe:.2f}" if isinstance(pe, (int, float)) else pe,
            "pbv": f"{pbv:.2f}" if isinstance(pbv, (int, float)) else pbv,
            "roe": roe_str,
        }
    except Exception as e:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Bot Screener Saham Interaktif Aktif!</b>\n\n"
        "Ketik perintah berikut untuk mengecek emiten secara instan:\n"
        "👉 <code>/cek toba</code>\n"
        "👉 <code>/cek sger</code>\n"
        "👉 <code>/cek wmuu</code>",
        parse_mode="HTML"
    )

async def cek_saham(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Format salah! Gunakan contoh: <code>/cek toba</code>", parse_mode="HTML")
        return
    
    ticker_input = context.args[0].upper()
    await update.message.reply_text(f"⏳ Sedang memindai data live untuk <b>{ticker_input}</b>...", parse_mode="HTML")
    
    s = analyze_stock(ticker_input)
    if not s:
        await update.message.reply_text(f"❌ Gagal mendapatkan data atau emiten <b>{ticker_input}</b> tidak ditemukan.", parse_mode="HTML")
        return

    if s['signal_type'] == "BULLISH":
        message = (
            f"🟢 <b>{s['ticker']} — ANALISIS LIVE (BULLISH)</b>\n"
            f"✅ <i>{s['company_name']}</i>\n\n"
            f"<b>KUAT 🔼 (Analisis Tren & Whale)</b>\n"
            f"├── Harga Live: Rp {s['price']:,.0f} ({s['change_pct']:+.2f}%)\n"
            f"├── Zona Entry: <b>Rp {s['entry']:,.0f}</b>\n"
            f"├── Est. TP: <b>Rp {s['tp1']:,.0f}</b>\n"
            f"├── Est. SL: <b>Rp {s['stop_loss']:,.0f}</b>\n"
            f"├── Likuiditas: Rp {s['value_miliar']:.2f} M/hari\n"
            f"├── RSI-14: {s['rsi']} 🟢 Momentum Naik\n"
            f"├── Volume Surge: {s['vol_surge']} ({s['vol_ratio']}x MA20)\n"
            f"└── Potensi ARA: <b>{s['potensi_ara']}</b>\n\n"
            f"💎 <b>Valuasi:</b> P/E: {s['pe']} | P/BV: {s['pbv']}x | ROE: {s['roe']}"
        )
    else:
        message = (
            f"🔴 <b>{s['ticker']} — ANALISIS LIVE (BEARISH)</b>\n"
            f"⚠️ <i>{s['company_name']}</i>\n\n"
            f"<b>TEKANAN JUAL 🔽</b>\n"
            f"├── Harga Live: Rp {s['price']:,.0f} ({s['change_pct']:+.2f}%)\n"
            f"├── Likuiditas: Rp {s['value_miliar']:.2f} M/hari\n"
            f"├── RSI-14: {s['rsi']} 🔴 Momentum Lemah\n"
            f"└── Volume Dump: {s['vol_surge']} ({s['vol_ratio']}x MA20)\n\n"
            f"💎 <b>Valuasi:</b> P/E: {s['pe']} | P/BV: {s['pbv']}x | ROE: {s['roe']}"
        )

    await update.message.reply_text(message, parse_mode="HTML")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cek", cek_saham))
    
    print("Bot Long Polling Berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
