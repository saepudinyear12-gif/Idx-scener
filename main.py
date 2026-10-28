import os
import asyncio
import pandas as pd
import yfinance as yf
from telegram import Bot

# Token & Chat ID Telegram Anda
TELEGRAM_BOT_TOKEN = "8694938627:AAHFF-uRBgSZIWFHK941fMMKglZIeZtAeVw"
TELEGRAM_CHAT_ID = "1768576462"

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

def check_stock_signal(ticker_symbol):
    try:
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
        stop_loss = int(round(support_zone * 0.99, 0)) # jebol area support
        tp1 = int(round(close_price * 1.05, 0))
        tp2 = int(round(close_price * 1.10, 0))
        fallback_support = int(round(support_zone * 0.95, 0))

        vol_ratio = volume_shares / vol_ma20 if vol_ma20 > 0 else 1.0

        # Kriteria Sinyal Sesuai (Vol lonjakan, Harga Naik >3%, Max Rp 3.000)
        cond_vol = volume_shares > (vol_ma20 * 1.5)
        cond_change = price_change_pct >= 3.0
        cond_rsi = float(latest['RSI14']) > 55
        cond_macd = float(latest['MACD_Hist']) > 0
        cond_val = value >= 1_000_000_000
        cond_price = close_price <= 3000

        if cond_vol and cond_change and cond_rsi and cond_macd and cond_val and cond_price:
            ticker_clean = ticker_symbol.replace(".JK", "")
            
            return {
                "ticker": ticker_clean,
                "company_name": company_name,
                "price": close_price,
                "change": price_change,
                "change_pct": price_change_pct,
                "volume_lots": volume_lots,
                "vol_ratio": vol_ratio,
                "pe": f"{pe:,.2f}x" if isinstance(pe, (int, float)) else pe,
                "pbv": f"{pbv:,.2f}x" if isinstance(pbv, (int, float)) else pbv,
                "roe": roe_str,
                "der": f"{der:,.2f}x" if isinstance(der, (int, float)) else der,
                "demand_zone": support_zone,
                "supply_zone": supply_zone,
                "fallback_support": fallback_support,
                "entry_low": entry_low,
                "entry_high": entry_high,
                "stop_loss": stop_loss,
                "tp1": tp1,
                "tp2": tp2,
            }

    except Exception as e:
        pass
    return None

async def run_screener():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    signals = []

    print("Memindai emiten Strong Bullish VVIP (Max Rp 3.000)...")
    for ticker in WATCHLIST:
        res = check_stock_signal(ticker)
        if res:
            signals.append(res)
        await asyncio.sleep(0.3)

    if signals:
        for s in signals:
            message = (
                f"(${s['ticker']})\n\n"
                f"📈 1. SNAPSHOT HARGA & SnD\n"
                f"— Harga Live: Rp {s['price']:,.0f}\n"
                f"— Perubahan: {s['change']:+,.0f} ({s['change_pct']:+.2f}%)\n"
                f"— Volume: {s['volume_lots']:,} lot ({s['vol_ratio']:.1f}x MA20)\n"
                f"— Demand Zone: Rp {s['demand_zone']:,.0f}\n"
                f"— Supply Zone: Rp {s['supply_zone']:,.0f}\n\n"
                f"💎 2. VALUASI & FUNDAMENTAL\n"
                f"— P/E: {s['pe']} | P/BV: {s['pbv']}\n"
                f"— ROE: {s['roe']} | DER: {s['der']}\n\n"
                f"🐋 3. BANDARMOLOGY & HISTORICAL TRANSACTION\n"
                f"🟢 Akumulasi Jejak Whale: Lonjakan volume {s['vol_ratio']:.1f}x dari rata-rata menunjukkan kesiapan markup phase.\n\n"
                f"🧠 4. ANALISIS SKENARIO SnD (IF-THEN)\n"
                f"• Jika berhasil menembus resistance Rp {s['supply_zone']:,.0f} dengan volume besar, silakan HAKA, peluang terbuka lebar.\n"
                f"• Jika terjadi false breakout atau gagal, potensi koreksi turun menuju support lanjutan di Rp {s['fallback_support']:,.0f}.\n\n"
                f"🎯 5. TRADING PLAN\n"
                f"• Entry: {s['entry_low']:,.0f} – {s['entry_high']:,.0f}\n"
                f"• Stop Loss (SL): {s['stop_loss']:,.0f} (jebol area support)\n"
                f"• Take Profit 1: {s['tp1']:,.0f}\n"
                f"• Take Profit 2: {s['tp2']:,.0f}\n\n"
                f"⭐ 6. RATING\n"
                f"🚀🔥 POTENSI ARA / SUPER MOMENTUM"
            )
            
            try:
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, disable_web_page_preview=True)
            except Exception as e:
                print(f"Gagal mengirim pesan untuk {s['ticker']}: {e}")
            
            await asyncio.sleep(1)
            
        print("Alert VVIP gaya bot 'CUAN SAYA' berhasil dikirim ke Telegram!")
    else:
        print("Belum ada emiten Strong Bullish yang memenuhi kriteria hari ini.")

if __name__ == "__main__":
    asyncio.run(run_screener())
