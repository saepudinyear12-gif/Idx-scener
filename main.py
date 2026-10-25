import os
import asyncio
import pandas as pd
import yfinance as yf
from telegram import Bot

# Token & Chat ID Telegram Anda
TELEGRAM_BOT_TOKEN = "8694938627:AAHFF-uRBgSZIWFHK941fMMKglZIeZtAeVw"
TELEGRAM_CHAT_ID = "1768576462"

# Watchlist Komprehensif Sektor Non-Bluechip Teraktif & High Volatility (PRIME & TECH telah dihapus)
WATCHLIST = [
    # --- 1. PROPERTI & REAL ESTATE ---
    "PANI.JK", "BSDE.JK", "CTRA.JK", "PWON.JK", "SMRA.JK", "ASRI.JK", "LPKR.JK", 
    "DILD.JK", "BEST.JK", "DUTI.JK", "BKSL.JK", "KIJA.JK", "MMLP.JK", "GWSA.JK",

    # --- 2. KESEHATAN (Health) ---
    "SILO.JK", "HEAL.JK", "MIKA.JK", "KAEF.JK", "INAF.JK", "DVLA.JK", "PEHA.JK", "RSGK.JK",
    
    # --- 3. TEKNOLOGI, DIGITAL & KABEL ---
    "GOTO.JK", "BUKA.JK", "EMTK.JK", "MTDL.JK", "BELI.JK", "SCMA.JK", 
    "FREN.JK", "EXCL.JK", "ISAT.JK", "WIFI.JK", "AXIO.JK",
    
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
        volume_lots = int(volume_shares / 100)
        vol_ma20 = float(latest['Vol_MA20'])
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

        # Pemetaan SnD & Support Bawah
        support_zone = round(df['Low'].tail(5).min(), 0)
        support_bawah = round(df['Low'].tail(20).min(), 0)
        resistance_zone = round(df['High'].tail(20).max(), 0)

        # Kalkulasi Trading Plan Berbasis SnD
        entry_low = int(close_price)
        entry_high = int(max(close_price, round(close_price * 1.02, 0)))
        stop_loss = int(round(support_zone * 0.98, 0))
        
        tp1 = int(resistance_zone) if resistance_zone > entry_high else int(round(close_price * 1.05, 0))
        tp2 = int(round(tp1 * 1.05, 0)) if tp1 > entry_high else int(round(close_price * 1.10, 0))

        # Rasio Lonjakan Volume vs Rata-rata 20 Hari
        vol_ratio = volume_shares / vol_ma20 if vol_ma20 > 0 else 1.0

        # --- KRITERIA UTAMA (TETAP LENGKAP) ---
        cond_vol = volume_shares > (vol_ma20 * 1.5)
        cond_change = price_change_pct >= 3.0
        cond_rsi = float(latest['RSI14']) > 55 and float(latest['RSI14']) > float(prev['RSI14'])
        cond_macd = float(latest['MACD_Hist']) > 0
        cond_val = value >= 1_000_000_000  # Min Transaksi Rp 1 Miliar
        cond_price = close_price <= 3000   # Maksimal Harga Saham Rp 3.000

        # --- TAMBAHAN DETEKSI POTENSI ARA (SUPER MOMENTUM) ---
        is_potential_ara = (volume_shares > (vol_ma20 * 3.0)) and (price_change_pct >= 10.0)

        if cond_vol and cond_change and cond_rsi and cond_macd and cond_val and cond_price:
            ticker_clean = ticker_symbol.replace(".JK", "")
            
            rating_text = "🚀 🔥 POTENSI ARA / SUPER MOMENTUM" if is_potential_ara else "🔥 SnD Momentum Breakout"
            
            return {
                "ticker": ticker_clean,
                "company_name": company_name,
                "price": close_price,
                "change": price_change,
                "change_pct": price_change_pct,
                "volume_lots": volume_lots,
                "vol_ratio": vol_ratio,
                "market_cap": market_cap,
                "pe": f"{pe:.2f}" if isinstance(pe, (int, float)) else pe,
                "pbv": f"{pbv:.2f}" if isinstance(pbv, (int, float)) else pbv,
                "roe": roe_str,
                "der": f"{der:.2f}" if isinstance(der, (int, float)) else der,
                "support": support_zone,
                "support_bawah": support_bawah if support_bawah < support_zone else int(support_zone * 0.95),
                "resist": resistance_zone,
                "entry_low": entry_low,
                "entry_high": entry_high,
                "stop_loss": stop_loss,
                "tp1": tp1,
                "tp2": tp2,
                "rating_text": rating_text
            }

    except Exception as e:
        pass
    return None

async def run_screener():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    signals = []

    print("Memindai emiten SnD & Historical Transaction...")
    for ticker in WATCHLIST:
        res = check_stock_signal(ticker)
        if res:
            signals.append(res)
        await asyncio.sleep(0.3)

    if signals:
        for s in signals:
            message = (
                f"🏢 <b>Emiten:</b> {s['company_name']} (${s['ticker']})\n\n"
                f"📈 <b>1. SNAPSHOT HARGA & SnD</b>\n"
                f"├── Harga Live: Rp {s['price']:,.0f}\n"
                f"├── Perubahan: {s['change']:+,.0f} ({s['change_pct']:+.2f}%)\n"
                f"├── Volume: {s['volume_lots']:,} lot ({s['vol_ratio']:.1f}x MA20)\n"
                f"├── Demand Zone: Rp {s['support']:,.0f}\n"
                f"└── Supply Zone: Rp {s['resist']:,.0f}\n\n"
                f"💎 <b>2. VALUASI & FUNDAMENTAL</b>\n"
                f"├── P/E: {s['pe']} | P/BV: {s['pbv']}x\n"
                f"└── ROE: {s['roe']} | DER: {s['der']}x\n\n"
                f"🐳 <b>3. BANDARMOLOGY & HISTORICAL TRANSACTION</b>\n"
                f"🟢 <b>Akumulasi Jejak Whale:</b> Lonjakan volume {s['vol_ratio']:.1f}x dari rata-rata menunjukkan kesiapan <i>markup phase</i>.\n\n"
                f"🧠 <b>4. ANALISIS SKENARIO SnD (IF-THEN)</b>\n"
                f"• Jika berhasil menembus resistance <b>Rp {s['resist']:,.0f}</b> dengan volume besar, silakan HAKA, peluang terbuka lebar.\n"
                f"• Jika terjadi <i>false breakout</i> atau gagal, potensi koreksi turun menuju support lanjutan di <b>Rp {s['support_bawah']:,.0f}</b>.\n\n"
                f"🎯 <b>5. TRADING PLAN</b>\n"
                f"• <b>Entry:</b> {s['entry_low']:,.0f} – {s['entry_high']:,.0f}\n"
                f"• <b>Stop Loss (SL):</b> {s['stop_loss']:,.0f} (jebol area support)\n"
                f"• <b>Take Profit 1:</b> {s['tp1']:,.0f}\n"
                f"• <b>Take Profit 2:</b> {s['tp2']:,.0f}\n\n"
                f"⭐ <b>6. RATING</b>\n"
                f"└── {s['rating_text']}\n\n"
                f"<i>Disclaimer: Live market data & psikologi tren. DYOR!</i>"
            )
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML", disable_web_page_preview=True)
            await asyncio.sleep(1)
            
        print("Alert SnD Berhasil dikirim ke Telegram!")
    else:
        print("Belum ada emiten yang memenuhi skenario SnD hari ini.")

if __name__ == "__main__":
    asyncio.run(run_screener())
