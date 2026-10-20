import os
import requests
import yfinance as yf

# Ambil Token dan Chat ID Telegram dari GitHub Secrets
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Daftar Saham Khusus Volatil, Second/Third Liner, Spekulatif & IPO (< 3.000 - Tanpa Blue Chip)
WATCHLIST = [
    # --- ENERGI, TAMBANG & MINING KECIL/MENENGAH ---
    "BUMI.JK", "ENRG.JK", "ELSA.JK", "INDY.JK", "HRUM.JK", "TOBA.JK", "BRMS.JK", "DEWA.JK", 
    "PSAB.JK", "CITA.JK", "ARCI.JK", "APEX.JK", "DOOH.JK", "PSSI.JK", "SOCI.JK", "CRAB.JK", 
    "INET.JK", "SMGA.JK", "NCKL.JK", "MBMA.JK", "TINS.JK", "ZINC.JK", "SMMT.JK", "RMKE.JK",
    "ADHI.JK", "PTPP.JK", "WIKA.JK", "WEGE.JK", "BIPI.JK", "PACK.JK", "GTSI.JK", "KOIN.JK",

    # --- PROPERTI, INFRASTRUKTUR & KONSTRUKSI LAPIS KEDUA/KETIGA ---
    "BSDE.JK", "CTRA.JK", "PWON.JK", "ASRI.JK", "SMRA.JK", "LPKR.JK", "KIJA.JK", "DMAS.JK", 
    "PANI.JK", "DGIK.JK", "BKSL.JK", "KRYA.JK", "PADA.JK", "STRK.JK", "GRPH.JK", "LAPD.JK", 
    "TAXI.JK", "KAQI.JK", "HUMI.JK", "RAAM.JK", "GTRA.JK", "KIP.JK", "LPCK.JK", "MMLP.JK", 
    "BEST.JK", "CITY.JK", "RBMS.JK", "SAFE.JK", "TOTL.JK", "NRCA.JK", "META.JK", "IPCC.JK",
    "FREN.JK", "BALI.JK", "CARS.JK", "JGLE.JK", "POLU.JK", "LAND.JK", "SATU.JK", "UANG.JK",

    # --- KEUANGAN, BANK DIGITAL & FINANCE LAPIS KECIL ---
    "AGRO.JK", "BBYB.JK", "PNLF.JK", "BFIN.JK", "BNGA.JK", "BABP.JK", "BACA.JK", "BANK.JK", 
    "BCIC.JK", "BGTG.JK", "BINA.JK", "BSWD.JK", "BHAT.JK", "FINN.JK", "ARTO.JK", "NOBU.JK", 
    "MEGA.JK", "MAYA.JK", "INPC.JK", "AMAR.JK", "BBSI.JK", "PNBS.JK", "BPII.JK", "GSMF.JK",

    # --- CONSUMER, RITEL, KESEHATAN & CPO ---
    "AISA.JK", "STAA.JK", "TAPG.JK", "DSNG.JK", "SIMP.JK", "LSIP.JK", "SSMS.JK", "PYFA.JK", 
    "SNLK.JK", "KAEF.JK", "INAF.JK", "DGNS.JK", "SRAJ.JK", "MIDI.JK", "CLEO.JK", "JPFA.JK", 
    "MAIN.JK", "ROTI.JK", "WOOD.JK", "PBSA.JK", "ERAA.JK", "GJTL.JK", "SCMA.JK", "MPPA.JK", 
    "FOOD.JK", "MAPA.JK", "RALS.JK", "ITAL.JK", "BUVA.JK", "HEAL.JK", "SILO.JK",

    # --- INDUSTRI, MANUFAKTUR & TEKSTIL ---
    "AUTO.JK", "SMSM.JK", "IMAS.JK", "HEXA.JK", "SRTG.JK", "AKPI.JK", "SRIL.JK", "PBRX.JK", 
    "POLY.JK", "MYTX.JK", "BELL.JK", "SBMA.JK", "SPMA.JK", "TRIS.JK", "BATA.JK", "FILM.JK", 
    "MDIA.JK", "VTP.JK", "MLIA.JK", "AMFG.JK", "TOTO.JK", "CINT.JK", "KDSI.JK", "SCCO.JK",
    "ALKA.JK", "ARGO.JK", "IKAI.JK", "KARW.JK", "KBLI.JK", "KBLM.JK", "MDKI.JK", "JECC.JK",

    # --- SAHAM FREKUENSI TINGGI / SPECIAL MOMENTUM / GORENGAN AKTIF ---
    "BSSP.JK", "NICE.JK", "BAJA.JK", "GDST.JK", "ISSP.JK", "TARA.JK", "SLIS.JK", "ZBRA.JK", 
    "BHIT.JK", "BCAP.JK", "KPIG.JK", "IPTV.JK", "MSKY.JK", "MARI.JK", "ABBA.JK", "NFCX.JK", 
    "ALDO.JK", "OASA.JK", "FORZ.JK", "COWL.JK", "JSPT.JK", "BTEK.JK", "IIKP.JK", "BPTR.JK", 
    "CASS.JK", "MICE.JK", "PORT.JK", "HAIS.JK", "PGLI.JK", "BOAT.JK", "CYBR.JK", "WIFI.JK",

    # --- TAMBAHAN SAHAM VOLATIL / IPO / HIGH FREQUENCY ---
    "HILL.JK", "MPRO.JK", "BSBK.JK", "SINI.JK", "JARR.JK", "MGLV.JK", 
    "LMAX.JK", "NSSS.JK", "MUTU.JK", "TRUE.JK", "RELF.JK", "KOKA.JK", "NICK.JK", 
    "MENN.JK", "SAGE.JK", "SOUL.JK", "CBRE.JK", "HAJJ.JK", "PEVE.JK", "PPRI.JK", 
    "MAHA.JK", "RSGK.JK", "TOOL.JK", "ALII.JK", "UDNG.JK", "AATI.JK", "NZIA.JK",
    "BEBS.JK", "NANO.JK", "BINO.JK", "AXIO.JK", "COIN.JK", "VTNY.JK", "OMED.JK"
]

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID belum diset.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Gagal mengirim pesan ke Telegram: {e}")

def run_preara_screener():
    signals = []
    clean_watchlist = list(set(WATCHLIST))
    
    for symbol in clean_watchlist:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1mo", interval="1d")
            
            if len(df) < 5:
                continue

            prev_close = df['Close'].iloc[-2]
            current_price = df['Close'].iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            
            # Hitung Rata-rata Volume 20 Hari
            ma_vol_20 = df['Volume'].tail(20).mean()
            
            # Persentase Perubahan Harga
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # Estimasi Nilai Transaksi
            total_value = current_price * current_volume

            # Logika Filter Pre-ARA:
            # 1. Harga di bawah 3.000 (0 < Harga < 3000)
            # 2. Price Change antara +3.0% s.d. +12.0%
            # 3. Volume > MA Volume 20
            # 4. Value > Rp 1 Miliar
            if 0 < current_price < 3000 and 3.0 <= change_pct <= 12.0 and current_volume > ma_vol_20 and total_value >= 1_000_000_000:
                clean_symbol = symbol.replace(".JK", "")
                signals.append(f"/{clean_symbol}:{int(current_price)} (+{change_pct:.1f}%)")
                
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    if signals:
        pesan_saham = "\n".join(signals[:30])
        message = f"🚀 *PRE-ARA SPECULATIVE & VOLATILE DETECTED (< 3.000)*\n\n{pesan_saham}"
        print("Sinyal Ditemukan:\n", message)
        send_telegram_alert(message)
    else:
        print("Screener Selesai: Tidak ada saham volatil < 3.000 yang memenuhi kriteria Pre-ARA.")

if __name__ == "__main__":
    run_preara_screener()
