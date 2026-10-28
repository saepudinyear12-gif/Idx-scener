import os
import asyncio
import logging
import pandas as pd
import yfinance as yf
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# --- KONFIGURASI BOT ---
TELEGRAM_BOT_TOKEN = "8805497572:AAH9XxKICtNGdiF5J19o61tZ27ht_BYFjeE"
TELEGRAM_CHAT_ID = "1768576462"  # Chat ID default untuk kirim hasil screener otomatis

# Konfigurasi logging agar proses bot terlihat di terminal
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Watchlist Komprehensif Sektor
WATCHLIST = [
    # --- 1. PROPERTI & REAL ESTATE ---
    "PANI.JK", "BSDE.JK", "CTRA.JK", "PWON.JK", "SMRA.JK", "ASRI.JK", "LPKR.JK", 
    "DILD.JK", "BEST.JK", "DUTI.JK", "BKSL.JK", "KIJA.JK", "MMLP.JK", "GWSA.JK",

    # --- 2. KESEHATAN (Health) ---
    "SILO.JK", "HEAL.JK", "MIKA.JK", "KAEF.JK", "INAF.JK", "DVLA.JK", "PEHA.JK", "RSGK.JK",
    
    # --- 3. TEKNOLOGI, DIGITAL & KABEL ---
    "GOTO.JK", "BUKA.JK", "EMTK.JK", "MTDL.JK", "BELI.JK", "SCMA.JK", 
    "EXCL.JK", "ISAT.JK", "WIFI.JK", "AXIO.JK",
    
    # --- 4. BAHAN BAKU / BASIC MATERIALS ---
    "BRPT.JK", "TPIA.JK", "TKIM.JK", "INKP.JK", "IMPC.JK", "ESSA.JK", "NCKL.JK", 
    "MBMA.JK", "PSAB.JK", "DKHH.JK", "ANTM.JK", "INCO.JK", "MDKA.JK",
    
    # --- 5. ENERGI (Batubara, Migas, EBT & Jasa Energi) ---
    "BUMI.JK", "BRMS.JK", "DEWA.JK", "ENRG.JK", "ELSA.JK", "DOID.JK", "RAJA.JK", "PGEO.JK",
    "ADRO.JK", "PTBA.JK", "ITMG.JK", "HRUM.JK", "ADMR.JK", "MEDC.JK", "INDY.JK", "TOBA.JK", 
    "BSSR.JK", "BIPI.JK", "SGER.JK", "RMKE.JK", "IATA.JK", "COAL.JK", "SHIP.JK", "SOCI.JK", "TPMA.JK",
    
    # --- 6. TEKSTIL & GARMEN ---
    "ARGO.JK", "BELL.JK", "TRIS.JK", "POLU.JK", "SSTM.JK", "ERTX.JK", "ESTI.JK", "RICY.JK", "TFCO.JK", "PBRX.JK", "ADMG.JK",

    # --- 7. TRANSPORTASI, LOGISTIK & MARITIM ---
    "ASSA.JK", "BIRD.JK", "HAIS.JK", "PSSI.JK", "BBRM.JK", "GTSI.JK", "SMDR.JK", "TMAS.JK", "BOAT.JK",
    "LEAD.JK", "WINS.JK", "HITS.JK", "IPCC.JK",

    # --- 8. CONSUMER, RETAIL, KEUANGAN & MULTIFINANCE ---
    "ACES.JK", "ERAA.JK", "MAPI.JK", "MAPA.JK", "CMRY.JK", "SIDO.JK", "JPFA.JK", "CPIN.JK", "CLEO.JK", "MIDI.JK",
    "ARTO.JK", "BRIS.JK", "PNLF.JK", "BBYB.JK", "AGRO.JK", "BABP.JK", "CFIN.JK", "ADMF.JK", "WOMF.JK",
    "BANK.JK", "INPC.JK", "BBHI.JK", "MASB.JK", "BGTG.JK",

    # --- 9. PERKEBUNAN, CPO & PERTANIAN ---
    "TAPG.JK", "DSNG.JK", "SSMS.JK", "LSIP.JK", "AALI.JK", "PALM.JK", "BWPT.JK", "SIMP.JK", "SGRO.JK", "CSRA.JK",

    # --- 10. PERINDUSTRIAN & KOMPONEN OTOMOTIF ---
    "AUTO.JK", "DRMA.JK", "SMSM.JK", "BOLT.JK", "GJTL.JK", "IMAS.JK", "KBLI.JK", "VOKS.JK", "ARNA.JK", "MARK.JK",

    # --- 11. MEDIA & HIBURAN ---
    "TMPO.JK", "FILM.JK", "FORU.JK", "MARI.JK", "MNCN.JK", "BMTR.JK", "VIVA.JK",

    # --- 12. KONSTRUKSI SWASTA, KAWASAN INDUSTRI & INFRASTRUKTUR ---
    "ACST.JK", "TOTL.JK", "NRCA.JK", "PPRE.JK", "WEGE.JK", "IDPR.JK", "KBLM.JK",
    "SSIA.JK", "IPAC.JK", "MPXL.JK", "SAME.JK",

    # --- 13. KEMASAN, PLASTIK & DAUR ULANG ---
    "PBID.JK", "IPOL.JK", "FAPA.JK", "SOUL.JK", "TALF.JK", "KMTR.JK", "NPGF.JK",

    # --- 14. PETERNAKAN & PAKAN TERNAK (POULTRY) ---
    "MAIN.JK", "SIPD.JK", "WMUU.JK", "WMPP.JK",

    # --- 15. HOTEL, RESTORAN & PARIWISATA (HOREKA) ---
    "FAST.JK", "PZZA.JK", "PANR.JK", "BUVA.JK",

    # --- 16. HOLDING INVESTASI & ASURANSI ---
    "ABMM.JK", "ABDA.JK", "ASBI.JK", "AHAP.JK",

    # --- 17. INFRASTRUKTUR, DATA CENTER & MENARA ---
    "TOWR.JK", "TBIG.JK", "CENT.JK", "IBST.JK", "MTEL.JK", "BALI.JK",

    # --- 18. NIKEL, MINERAL KRITIS & EV ---
    "NICL.JK", "DKFT.JK", "CITA.JK", "NICK.JK",

    # --- HIGH VOLATILITY / GORENGAN SUPER AKTIF LAINNYA ---
    "DOOH.JK", "HUMI.JK", "STRK.JK", "KEEN.JK", "CUAN.JK", "PACK.JK", 
    "TRUE.JK", "HILL.JK", "NSSS.JK", "MOLI.JK", "JGLE.JK", "MPRO.JK", "AMMN.JK", "SAGE.JK"
]

# --- FUNGSI ANALISIS UTAMA (GAYA CUAN SAYA) ---
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
        value = close_price * volume_shares
        
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

        # Cek kondisi untuk screener otomatis
        cond_vol = volume_shares > (vol_ma20 * 1.5)
        cond_change = price_change_pct >= 3.0
        cond_rsi = float(latest['RSI14']) > 55
        cond_macd = float(latest['MACD_Hist']) > 0
        cond_val = value >= 1_000_000_000
        cond_price = close_price <= 3000

        is_passed = (cond_vol and cond_change and cond_rsi and cond_macd and cond_val and cond_price)

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
            f"🟢 Akumulasi Jejak Whale: Lonjakan volume {vol_ratio:.1f}x dari rata-rata menunjukkan kesiapan markup phase.\n\n"
            f"🧠 4. ANALISIS SKENARIO SnD (IF-THEN)\n"
            f"• Jika berhasil menembus resistance Rp {supply_zone:,.0f} dengan volume besar, silakan HAKA, peluang terbuka lebar.\n"
            f"• Jika terjadi false breakout atau gagal, potensi koreksi turun menuju support lanjutan di Rp {fallback_support:,.0f}.\n\n"
            f"🎯 5. TRADING PLAN\n"
            f"• Entry: {entry_low:,.0f} – {entry_high:,.0f}\n"
            f"• Stop Loss (SL): {stop_loss:,.0f} (jebol area support)\n"
            f"• Take Profit 1: {tp1:,.0f}\n"
            f"• Take Profit 2: {tp2:,.0f}\n\n"
            f"⭐ 6. RATING\n"
            f"🚀🔥 POTENSI ARA / SUPER MOMENTUM"
        )
        return message, is_passed
    except Exception as e:
        return f"Gagal memuat data untuk emiten tersebut. Error: {e}", False

# --- FITUR TELEGRAM BOT: HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Bot Cuan Saya Aktif!**\n\n"
        "• Ketik `/cek KODE_SAHAM` (contoh: `/cek TOBA` atau `/cek BBCA`) untuk analisis manual instan.\n"
        "• Atau jalankan perintah `/scan` untuk memindai seluruh watchlist secara otomatis."
    )

async def cek_saham(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Mohon masukkan kode sahamnya. Contoh: `/cek TOBA`")
        return
    
    ticker = context.args[0].upper()
    await update.message.reply_text(f"Sedang memindai data untuk ${ticker}...")
    
    result_message, _ = analyze_stock(ticker)
    await update.message.reply_text(result_message, disable_web_page_preview=True)

async def run_manual_screener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Memindai emiten Strong Bullish VVIP (Max Rp 3.000) dari watchlist...")
    signals_count = 0

    for ticker in WATCHLIST:
        msg, is_passed = analyze_stock(ticker)
        if is_passed:
            await update.message.reply_text(msg, disable_web_page_preview=True)
            signals_count += 1
            await asyncio.sleep(1)
        await asyncio.sleep(0.2)

    if signals_count == 0:
        await update.message.reply_text("Belum ada emiten Strong Bullish yang memenuhi kriteria saat ini.")
    else:
        await update.message.reply_text(f"Selesai! Total {signals_count} emiten ditemukan.")

# --- MAIN PROGRAM ---
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Daftarkan command handlers untuk Telegram Interaktif
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cek", cek_saham))
    application.add_handler(CommandHandler("scan", run_manual_screener))

    print("Bot Telegram Gabungan (Manual & Screener) siap berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
