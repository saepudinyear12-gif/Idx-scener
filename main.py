import os
import asyncio
import pandas as pd
import yfinance as yf
from telegram import Bot

# Token & Chat ID Telegram Anda
TELEGRAM_BOT_TOKEN = "8694938627:AAHFF-uRBgSZIWFHK941fMMKglZIeZtAeVw"
TELEGRAM_CHAT_ID = "1768576462"

# Watchlist Komprehensif Sektor Non-Bluechip Teraktif & High Volatility
WATCHLIST = [
    # --- 1. PROPERTI & REAL ESTATE ---
    "PANI.JK", "BSDE.JK", "CTRA.JK", "PWON.JK", "SMRA.JK", "ASRI.JK", "LPKR.JK", 
    "DILD.JK", "BEST.JK", "DUTI.JK", "BKSL.JK", "KIJA.JK", "MMLP.JK", "GWSA.JK",

    # --- 2. KESEHATAN (Health) ---
    "SILO.JK", "HEAL.JK", "MIKA.JK", "KAEF.JK", "INAF.JK", "DVLA.JK", "PEHA.JK", "RSGK.JK", "PRIME.JK",
    
    # --- 3. TEKNOLOGI, DIGITAL & KABEL ---
    "GOTO.JK", "BUKA.JK", "EMTK.JK", "MTDL.JK", "BELI.JK", "TECH.JK", "SCMA.JK", 
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
        value_miliar = value / 1e9  # Dalam Miliar Rp
        
        price_change = close_price - prev_close
        price_change_pct = (price_change / prev_close) * 100

        # Data Fundamental & Valuasi
        pe = info.get('trailingPE', 'N/A')
        pbv = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity')
        roe_str = f"{roe*100:.2f}%" if roe else "N/A"
        der = info.get('debtToEquity', 'N/A')

        # Pemetaan SnD & Support Bawah
        support_zone = round(df['Low'].tail(5).min(), 0)
        support_bawah = round(df['Low'].tail(20).min(), 0)
        resistance_zone = round(df['High'].tail(20).max(), 0)

        # Kalkulasi Trading Plan & Metrik Kartu
        entry_low = int(close_price)
        stop_loss = int(round(support_zone * 0.98, 0))
        tp1 = int(resistance_zone) if resistance_zone > entry_low else int(round(close_price * 1.05, 0))
        tp2 = int(round(tp1 * 1.05, 0)) if tp1 > entry_low else int(round(close_price * 1.10, 0))

        vol_ratio = volume_shares / vol_ma20 if vol_ma20 > 0 else 1.0
        vol_surge_pct = int((vol_ratio - 1) * 100) if vol_ratio > 1 else 0

        # --- KRITERIA FILTER (DENGAN KONFIRMASI BREAKOUT) ---
        cond_vol = volume_shares > (vol_ma20 * 1.2)        # Lonjakan volume minimal 1.2x MA20
        cond_change = 1.0 <= price_change_pct < 15.0      # Kenaikan 1% s.d. <15%
        cond_rsi = float(latest['RSI14']) > 50            # RSI di atas 50
        cond_macd = float(latest['MACD_Hist']) > 0        # MACD histogram positif
        cond_val = value >= 1_000_000_000                 # Min Transaksi Rp 1 Miliar
        cond_price = close_price <= 3000                  # Maksimal Harga Saham Rp 3.000
        
        # Filter Breakout: Harga mendekati atau melewati resistance 20 hari (dalam radius 3% dari High 20h)
        cond_breakout = close_price >= (resistance_zone * 0.97)

        # Potensi ARA TINGGI jika volume >= 3x dan kenaikan >= 10%
        potensi_ara = "TINGGI" if (vol_ratio >= 3.0 and price_change_pct >= 10.0) else "MENENGAH"

        if cond_vol and cond_change and cond_rsi and cond_macd and cond_val and cond_price and cond_breakout:
            ticker_clean = ticker_symbol.replace(".JK", "")
            rsi_val = float(latest['RSI14'])
            
            return {
                "ticker": ticker_clean,
                "company_name": company_name,
                "price": close_price,
                "change": price_change,
                "change_pct": price_change_pct,
                "value_miliar": value_miliar,
                "rsi": f"{rsi_val:.1f}",
                "vol_surge": f"{vol_surge_pct}%",
                "vol_ratio_raw": vol_ratio,  # Disimpan untuk keperluan sorting
                "vol_ratio": f"{vol_ratio:.1f}",
                "potensi_ara": potensi_ara,
                "support": support_zone,
                "support_bawah": support_bawah if support_bawah < support_zone else int(support_zone * 0.95),
                "resist": resistance_zone,
                "entry": entry_low,
                "stop_loss": stop_loss,
                "tp1": tp1,
                "tp2": tp2,
                "pe": f"{pe:.2f}" if isinstance(pe, (int, float)) else pe,
                "pbv": f"{pbv:.2f}" if isinstance(pbv, (int, float)) else pbv,
                "roe": roe_str,
                "der": f"{der:.2f}" if isinstance(der, (int, float)) else der,
            }

    except Exception as e:
        pass
    return None

async def run_screener():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    signals = []

    print("Memindai emiten Breakout & Sorting Volume...")
    for ticker in WATCHLIST:
        res = check_stock_signal(ticker)
        if res:
            signals.append(res)
        await asyncio.sleep(0.3)

    if signals:
        # --- FITUR SORTING: URUTKAN BERDASARKAN VOLUME SURGE TERBESAR ---
        signals = sorted(signals, key=lambda x: x['vol_ratio_raw'], reverse=True)

        for i, s in enumerate(signals, 1):
            message = (
                f"<b>#{i} {s['ticker']}</b>\n"
                f"✅ <i>Breakout & Volume Surge Screener</i>\n\n"
                f"<b>KUAT 🔼 (Analisis Tren & Whale)</b>\n"
                f"├── Harga Live: Rp {s['price']:,.0f} ({s['change_pct']:+.2f}%)\n"
                f"├── Zona Entry (Fib/SnD): <b>Rp {s['entry']:,.0f}</b>\n"
                f"├── Est. TP Besok: <b>Rp {s['tp1']:,.0f}</b>\n"
                f"├── Est. SL Besok: <b>Rp {s['stop_loss']:,.0f}</b>\n"
                f"├── Likuiditas: Rp {s['value_miliar']:.2f} M/hari\n"
                f"├── RSI-14: {s['rsi']} 🔴 Momentum\n"
                f"├── Volume Surge: {s['vol_surge']} ⬆️ ({s['vol_ratio']}x MA20)\n"
                f"├── Potensi ARA Besok: <b>{s['potensi_ara']}</b>\n"
                f"├── Demand Zone: Rp {s['support']:,.0f}\n"
                f"└── Supply Zone (Breakout): Rp {s['resist']:,.0f}\n\n"
                f"💎 <b>Fundamental & Valuasi:</b>\n"
                f"└── P/E: {s['pe']} | P/BV: {s['pbv']}x | ROE: {s['roe']}\n\n"
                f"⚡ <i>Sinyal Akumulasi & Breakout Terkonfirmasi ✅</i>\n\n"
                f"<blockquote>🎯 <b>Potensi ARA {s['potensi_ara']}</b> — akumulasi & momentum kuat (heuristik, BUKAN jaminan). DYOR!</blockquote>"
            )
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML", disable_web_page_preview=True)
            await asyncio.sleep(1)
            
        print("Alert Breakout & Sorting Berhasil dikirim ke Telegram!")
    else:
        print("Belum ada emiten yang memenuhi kriteria breakout hari ini.")

if __name__ == "__main__":
    asyncio.run(run_screener())
