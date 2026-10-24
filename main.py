import os
import asyncio
import pandas as pd
import yfinance as yf
from telegram import Bot

# Mengambil Token & Chat ID secara aman dari GitHub Secrets
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Watchlist Komprehensif Sektor Non-Bluechip Teraktif & High Volatility
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

def calculate_snd_and_fib(df):
    """Menghitung zona Supply & Demand serta Target Fibonacci Extension"""
    if len(df) < 20:
        return None
    recent_df = df.tail(20)
    swing_high = recent_df['High'].max()
    swing_low = recent_df['Low'].min()
    price_range = swing_high - swing_low
    if price_range == 0:
        return None
    
    fib_1272 = swing_high + (price_range * 0.272)
    fib_1618 = swing_high + (price_range * 0.618)
    
    return {
        "swing_high": int(swing_high),
        "swing_low": int(swing_low),
        "fib_1272": int(fib_1272),
        "fib_1618": int(fib_1618),
        "demand_zone": int(swing_low),
        "supply_zone": int(swing_high)
    }

def check_stock_signal(ticker_symbol):
    try:
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="60d", interval="1d", progress=False)
        if df is None or df.empty or len(df) < 30:
            return None

        try:
            info = tk.info or {}
        except Exception:
            info = {}

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
        vol_ma20 = float(latest['Vol_MA20'])
        value = close_price * volume_shares
        value_miliar = value / 1e9  
        
        price_change = close_price - prev_close
        price_change_pct = (price_change / prev_close) * 100

        pe = info.get('trailingPE', 'N/A')
        pbv = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity')
        roe_str = f"{roe*100:.2f}%" if roe is not None else "N/A"

        snd_fib = calculate_snd_and_fib(df)
        if not snd_fib:
            return None

        support_zone = snd_fib["demand_zone"]
        resistance_zone = snd_fib["supply_zone"]
        fib_tp1 = snd_fib["fib_1272"]
        fib_tp2 = snd_fib["fib_1618"]

        support_bawah = round(df['Low'].tail(20).min(), 0)

        vol_ratio = volume_shares / vol_ma20 if vol_ma20 > 0 else 1.0
        vol_surge_pct = int((vol_ratio - 1) * 100) if vol_ratio > 1 else 0

        # Filter Dasar: Nilai transaksi min 1M, Harga maks 3000, Volume minimal 1.1x MA20
        cond_base = (value >= 1_000_000_000) and (close_price <= 3000) and (volume_shares >= (vol_ma20 * 1.1))
        if not cond_base:
            return None

        rsi_val = float(latest['RSI14'])
        macd_hist = float(latest['MACD_Hist'])
        ticker_clean = ticker_symbol.replace(".JK", "")

        # --- LOGIKA 1: BULLISH (DILONGGARKAN AGAR MUDAH TERTANGKAP) ---
        # Harga naik mulai dari 0% ke atas (menghijau tipis pun masuk), RSI > 48, Dekat Resisten (80%)
        cond_bull_change = 0.0 <= price_change_pct < 20.0
        cond_bull_rsi = rsi_val > 48
        cond_bull_macd = macd_hist > -0.001 # Sangat longgar untuk MACD
        cond_bull_breakout = close_price >= (resistance_zone * 0.80)

        if cond_bull_change and cond_bull_rsi and cond_bull_macd and cond_bull_breakout:
            entry_low = int(close_price)
            stop_loss = int(round(support_zone * 0.98, 0))
            potensi_ara = "TINGGI" if (vol_ratio >= 2.5 and price_change_pct >= 8.0) else "MENENGAH"

            return {
                "signal_type": "BULLISH",
                "ticker": ticker_clean,
                "company_name": company_name,
                "price": close_price,
                "change_pct": price_change_pct,
                "value_miliar": value_miliar,
                "rsi": f"{rsi_val:.1f}",
                "vol_ratio_raw": vol_ratio,
                "vol_ratio": f"{vol_ratio:.1f}",
                "vol_surge": f"{vol_surge_pct}%",
                "potensi_ara": potensi_ara,
                "support": support_zone,
                "resist": resistance_zone,
                "fib_tp1": fib_tp1,
                "fib_tp2": fib_tp2,
                "entry": entry_low,
                "stop_loss": stop_loss,
                "pe": f"{pe:.2f}" if isinstance(pe, (int, float)) else pe,
                "pbv": f"{pbv:.2f}" if isinstance(pbv, (int, float)) else pbv,
                "roe": roe_str,
            }

        # --- LOGIKA 2: BEARISH ---
        cond_bear_change = -15.0 < price_change_pct <= -1.0
        cond_bear_rsi = rsi_val < 50
        cond_bear_macd = macd_hist < 0
        cond_bear_breakdown = close_price <= (support_bawah * 1.05)

        if cond_bear_change and cond_bear_rsi and cond_bear_macd and cond_bear_breakdown:
            return {
                "signal_type": "BEARISH",
                "ticker": ticker_clean,
                "company_name": company_name,
                "price": close_price,
                "change_pct": price_change_pct,
                "value_miliar": value_miliar,
                "rsi": f"{rsi_val:.1f}",
                "vol_ratio_raw": vol_ratio,
                "vol_ratio": f"{vol_ratio:.1f}",
                "vol_surge": f"{vol_surge_pct}%",
                "support_bawah": support_bawah,
                "resist": resistance_zone,
                "pe": f"{pe:.2f}" if isinstance(pe, (int, float)) else pe,
                "pbv": f"{pbv:.2f}" if isinstance(pe, (int, float)) else pbv,
                "roe": roe_str,
            }

    except Exception as e:
        print(f"Skipping {ticker_symbol} due to error: {e}")
    return None

async def run_screener():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Token atau Chat ID Telegram belum diset di environment variables.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    signals = []

    print("Memindai emiten Mode Peka (SGER & High Volume)...")
    for ticker in WATCHLIST:
        try:
            res = check_stock_signal(ticker)
            if res:
                signals.append(res)
        except Exception as e:
            print(f"Gagal memproses emiten {ticker}: {e}")
        await asyncio.sleep(0.3)

    if signals:
        signals = sorted(signals, key=lambda x: x['vol_ratio_raw'], reverse=True)

        for i, s in enumerate(signals, 1):
            if s['signal_type'] == "BULLISH":
                message = (
                    f"🟢 <b>#{i} {s['ticker']} — SINYAL ENTRY (BULLISH)</b>\n"
                    f"✅ <i>Breakout & Akumulasi Whale Terkonfirmasi</i>\n\n"
                    f"<b>KUAT 🔼 (Analisis Tren & Whale)</b>\n"
                    f"├── Harga Live: Rp {s['price']:,.0f} ({s['change_pct']:+.2f}%)\n"
                    f"├── Zona Entry (Fib/SnD): <b>Rp {s['entry']:,.0f}</b>\n"
                    f"├── Est. TP Utama (Fib 1.618): <b>Rp {s['fib_tp2']:,.0f}</b>\n"
                    f"├── TP Konservatif (Fib 1.272): Rp {s['fib_tp1']:,.0f}\n"
                    f"├── Est. SL: <b>Rp {s['stop_loss']:,.0f}</b>\n"
                    f"├── Likuiditas: Rp {s['value_miliar']:.2f} M/hari\n"
                    f"├── RSI-14: {s['rsi']} 🟢 Momentum Naik\n"
                    f"├── Volume Surge: {s['vol_surge']} ⬆️ ({s['vol_ratio']}x MA20)\n"
                    f"├── Potensi ARA: <b>{s['potensi_ara']}</b>\n"
                    f"├── Demand Zone: Rp {s['support']:,.0f}\n"
                    f"└── Supply Zone: Rp {s['resist']:,.0f}\n\n"
                    f"💎 <b>Valuasi:</b> P/E: {s['pe']} | P/BV: {s['pbv']}x | ROE: {s['roe']}\n\n"
                    f"<blockquote>🎯 <b>REKOMENDASI: LAYAK ENTRY</b> (Akumulasi kuat). Tetap disiplin Stop Loss!</blockquote>"
                )
            else:
                message = (
                    f"🔴 <b>#{i} {s['ticker']} — WARNING! WASPADA (BEARISH)</b>\n"
                    f"⚠️ <i>Distribusi / Breakdown Support SnD</i>\n\n"
                    f"<b>TEKANAN JUAL TINGGI 🔽</b>\n"
                    f"├── Harga Live: Rp {s['price']:,.0f} ({s['change_pct']:+.2f}%)\n"
                    f"├── Likuiditas: Rp {s['value_miliar']:.2f} M/hari\n"
                    f"├── RSI-14: {s['rsi']} 🔴 Momentum Lemah/Turun\n"
                    f"├── Volume Dump: {s['vol_surge']} ⬇️ ({s['vol_ratio']}x MA20)\n"
                    f"├── Support Kritis Terancam: Rp {s['support_bawah']:,.0f}\n"
                    f"└── Supply Zone Atas: Rp {s['resist']:,.0f}\n\n"
                    f"💎 <b>Valuasi:</b> P/E: {s['pe']} | P/BV: {s['pbv']}x | ROE: {s['roe']}\n\n"
                    f"<blockquote>🚫 <b>REKOMENDASI: JANGAN ENTRY!</b> (Risiko koreksi lanjutan / jebol support).</blockquote>"
                )

            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML", disable_web_page_preview=True)
            await asyncio.sleep(1)
            
        print("Alert Sektor & SnD Berhasil dikirim ke Telegram!")
    else:
        print("Belum ada emiten yang memenuhi kriteria hari ini.")

if __name__ == "__main__":
    asyncio.run(run_screener())
