import logging
import pandas as pd
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Token Bot Telegram Anda
TELEGRAM_BOT_TOKEN = "8694938627:AAHFF-uRBgSZIWFHK941fMMKglZIeZtAeVw"

# Konfigurasi logging agar terlihat prosesnya di terminal
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fungsi untuk menganalisis saham (mirip dengan logika sebelumnya)
def analyze_stock(ticker_symbol):
    try:
        # Pastikan format ticker berakhiran .JK untuk bursa Indonesia
        if not ticker_symbol.endswith(".JK"):
            ticker_symbol += ".JK"
            
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="60d", interval="1d")
        if len(df) < 30:
            return None

        info = tk.info
        company_name = info.get('longName', ticker_symbol.replace('.JK', ''))

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
        volume_lots = int(volume_shares / 100)
        vol_ma20 = float(latest['Vol_MA20'])
        
        price_change = close_price - prev_close
        price_change_pct = (price_change / prev_close) * 100

        # Fundamental & Valuasi
        pe = info.get('trailingPE', 'N/A')
        pbv = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity')
        roe_str = f"{roe*100:.2f}%" if roe else "N/A"
        der = info.get('debtToEquity', 'N/A')

        # Support & Resistance / Demand & Supply Otomatis (20 Hari)
        support_zone = round(df['Low'].tail(20).min(), 0)
        supply_zone = round(df['High'].tail(20).max(), 0)

        # Trading Plan Kalkulasi
        entry_low = int(close_price)
        entry_high = int(round(close_price * 1.02, 0))
        stop_loss = int(round(support_zone * 0.99, 0))
        tp1 = int(round(close_price * 1.05, 0))
        tp2 = int(round(close_price * 1.10, 0))
        fallback_support = int(round(support_zone * 0.95, 0))

        vol_ratio = volume_shares / vol_ma20 if vol_ma20 > 0 else 1.0
        ticker_clean = ticker_symbol.replace(".JK", "")

        message = (
            f"(${ticker_clean}) - {company_name}\n\n"
            f"📈 1. SNAPSHOT HARGA & SnD\n"
            f"— Harga Live: Rp {close_price:,.0f}\n"
            f"— Perubahan: {price_change:+,.0f} ({price_change_pct:+.2f}%)\n"
            f"— Volume: {volume_lots:,} lot ({vol_ratio:.1f}x MA20)\n"
            f"— Demand Zone: Rp {support_zone:,.0f}\n"
            f"— Supply Zone: Rp {supply_zone:,.0f}\n\n"
            f"💎 2. VALUASI & FUNDAMENTAL\n"
            f"— P/E: {pe if pe=='N/A' else f'{pe:,.2f}x'} | P/BV: {pbv if pbv=='N/A' else f'{pbv:,.2f}x'}\n"
            f"— ROE: {roe_str} | DER: {der if der=='N/A' else f'{der:,.2f}x'}\n\n"
            f"🐋 3. BANDARMOLOGY & HISTORICAL TRANSACTION\n"
            f"🟢 Akumulasi Jejak Whale: Lonjakan volume {vol_ratio:.1f}x dari rata-rata.\n\n"
            f"🧠 4. ANALISIS SKENARIO SnD (IF-THEN)\n"
            f"• Jika berhasil menembus resistance Rp {supply_zone:,.0f} dengan volume besar, silakan HAKA.\n"
            f"• Jika terjadi false breakout, potensi koreksi ke support Rp {fallback_support:,.0f}.\n\n"
            f"🎯 5. TRADING PLAN\n"
            f"• Entry: {entry_low:,.0f} – {entry_high:,.0f}\n"
            f"• Stop Loss (SL): {stop_loss:,.0f}\n"
            f"• Take Profit 1: {tp1:,.0f}\n"
            f"• Take Profit 2: {tp2:,.0f}\n\n"
            f"⭐ 6. RATING\n"
            f"🚀🔥 ANALISIS MANUAL INSTAN"
        )
        return message
    except Exception as e:
        return f"Gagal memuat data untuk emiten tersebut. Error: {e}"

# Perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Bot Cuan Saya siap digunakan secara manual.\n\n"
        "Ketik perintah `/cek KODE_SAHAM` (contoh: `/cek TOBA` atau `/cek BBCA`) untuk melihat analisis lengkapnya!"
    )

# Perintah /cek <saham>
async def cek_saham(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Mohon masukkan kode sahamnya. Contoh: `/cek TOBA`")
        return
    
    ticker = context.args[0].upper()
    await update.message.reply_text(f"Sedang memindai data untuk ${ticker}...")
    
    result_message = analyze_stock(ticker)
    await update.message.reply_text(result_message)

def main():
    # Inisialisasi Bot dengan Application (Versi terbaru python-telegram-bot)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Daftarkan command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cek", cek_saham))

    print("Bot Telegram interaktif sedang berjalan... (Tekan Ctrl+C untuk berhenti)")
    # Jalankan bot secara terus menerus (polling)
    application.run_polling()

if __name__ == "__main__":
    main()
