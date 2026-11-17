import os
import yfinance as yf
import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from google import genai

# ==========================================
# KONFIGURASI API & TELEGRAM
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 13 SEKTOR UTAMA BEI + LAPIS 2 & 3
SECTORS_IDX = {
    "1. Energi": [
        "BUMI.JK", "DEWA.JK", "ENRG.JK", "ELSA.JK", "MEDC.JK", "DOID.JK", "INDY.JK", 
        "TOBA.JK", "BIPI.JK", "APEX.JK", "FIRE.JK", "MITI.JK", "SGER.JK", "TOOL.JK", "BOSS.JK", "TGRA.JK"
    ],
    "2. Barang Baku": [
        "BRMS.JK", "NCKL.JK", "PSAB.JK", "ANTM.JK", "INCO.JK", "TINS.JK", "ADMR.JK", 
        "HRUM.JK", "SWID.JK", "CBRE.JK", "DKFT.JK", "ARCI.JK", "CARS.JK", "PACK.JK", "ALKA.JK", "INDS.JK"
    ],
    "3. Perindustrian": [
        "ASII.JK", "PTRO.JK", "KOKA.JK", "MARK.JK", "WOOD.JK", "IKAN.JK", "ASRI.JK", 
        "LAND.JK", "KPIG.JK", "EAST.JK", "ARGO.JK"
    ],
    "4. Konsumen Primer": [
        "ICBP.JK", "INDF.JK", "MYOR.JK", "CLEO.JK", "MIDI.JK", "PAMG.JK", "ZONE.JK", 
        "BOBA.JK", "BUDI.JK", "PSDN.JK", "STAA.JK"
    ],
    "5. Konsumen Non-Primer": [
        "ACES.JK", "ERAA.JK", "MPPA.JK", "MAPA.JK", "AUTO.JK", "BABY.JK", "GLOB.JK", "POLU.JK", "DUCK.JK"
    ],
    "6. Kesehatan": [
        "HEAL.JK", "MIKA.JK", "SILO.JK", "PEHA.JK", "MERK.JK", "DVLA.JK"
    ],
    "7. Keuangan": [
        "AGRO.JK", "BNGA.JK", "PNBN.JK", "BBYB.JK", "ARTO.JK", "AMAR.JK", "BVIC.JK", 
        "BABP.JK", "BCIC.JK", "MAYA.JK", "PNBS.JK", "BANK.JK"
    ],
    "8. Properti & Real Estate": [
        "BSDE.JK", "PWON.JK", "CTRA.JK", "SMRA.JK", "APLN.JK", "PANI.JK", "BEST.JK", 
        "KIJA.JK", "LPCK.JK", "JRPT.JK", "DMAS.JK", "BKSL.JK", "POLA.JK"
    ],
    "9. Teknologi": [
        "GOTO.JK", "BUKA.JK", "EMTK.JK", "BELI.JK", "FUTR.JK", "CYBR.JK", "MPIX.JK", 
        "SEMA.JK", "TECH.JK", "DIVA.JK", "BUVA.JK", "ATIC.JK", "SCNP.JK", "RUN.JK"
    ],
    "10. Infrastruktur": [
        "MTEL.JK", "ISAT.JK", "EXCL.JK", "TBIG.JK", "TOWR.JK", "META.JK", "WIFI.JK"
    ],
    "11. Transportasi & Logistik": [
        "BIRD.JK", "ELPI.JK", "TMAS.JK", "IPCC.JK", "SAFE.JK", "PORT.JK", "RATU.JK", 
        "JAST.JK", "AXIO.JK", "SHIP.JK"
    ],
    "12. Media & Telekomunikasi": [
        "SCMA.JK", "MNCN.JK", "VIVA.JK", "NETV.JK", "BTEL.JK", "DNET.JK"
    ],
    "13. Konglomerasi & Lainnya": [
        "CUAN.JK", "BREN.JK", "AGAR.JK", "CBDK.JK", "RAJA.JK"
    ]
}

UNIVERSE_IDX = list(set(ticker for list_saham in SECTORS_IDX.values() for ticker in list_saham))

def hitung_cmf(df, period=20):
    mf_multiplier = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low']).replace(0, 1)
    mf_volume = mf_multiplier * df['Volume']
    cmf = mf_volume.rolling(window=period).sum() / df['Volume'].rolling(window=period).sum()
    return float(cmf.iloc[-1])

def jalankan_screener_batch():
    print(f"Mengunduh data batch untuk {len(UNIVERSE_IDX)} emiten...")
    data = yf.download(UNIVERSE_IDX, period="2mo", interval="1d", group_by="ticker", progress=False)
    kandidat_bagus = []
    
    for ticker in UNIVERSE_IDX:
        try:
            df = data[ticker].dropna(how="all")
            if df.empty or len(df) < 25:
                continue
                
            close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            high_10 = float(df['High'].iloc[-10:].max())
            vol = float(df['Volume'].iloc[-1])
            avg_vol_10 = float(df['Volume'].iloc[-11:-1].mean())
            ma5 = float(df['Close'].iloc[-5:].mean())
            cmf = hitung_cmf(df)
            
            if not (50 <= close <= 3000):
                continue
            if (close * vol) < 1_500_000_000:
                continue
                
            pct_change = ((close - prev_close) / prev_close) * 100
            vol_spike = vol / avg_vol_10 if avg_vol_10 > 0 else 0
            
            if pct_change < 1.0 or vol_spike < 1.2 or cmf < 0.01:
                continue
            if not (close >= ma5):
                continue
                
            target_1 = int(round(max(high_10 * 1.03, close * 1.06)))
            rating = "A+" if (vol_spike > 2.0 and cmf > 0.10) else "A"
            
            kandidat_bagus.append({
                "ticker": ticker.replace(".JK", ""),
                "price": int(close),
                "pct": round(pct_change, 2),
                "vol_spike": round(vol_spike, 1),
                "cmf": round(cmf, 2),
                "rating": rating,
                "target_1": f"Rp {target_1:,}".replace(",", "."),
                "score": (pct_change * 0.4) + (vol_spike * 0.4) + (cmf * 10)
            })
        except Exception:
            continue
            
    kandidat_bagus.sort(key=lambda x: x['score'], reverse=True)
    return kandidat_bagus[:4]

def buat_narasi_ai(saham_list):
    if not GEMINI_API_KEY:
        return "🤖 *AI Market Insight:* Momentum breakout terdeteksi."
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"Buatkan ringkasan analisa scalping singkat untuk saham berikut: {saham_list}"
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return f"🤖 *AI Market Insight:*\n{response.text}"
    except Exception:
        return "🤖 *AI Insight:* Sektor terpantau aktif."

def generate_card_image(saham_list, output_path="screener_result.png"):
    width, header_h, card_h, padding = 720, 110, 260, 28
    total_h = header_h + (len(saham_list) * (card_h + 24)) + 40
    
    img = Image.new("RGB", (width, total_h), "#f2fbf6")
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 30)
        font_sub = ImageFont.truetype("arial.ttf", 20)
        font_ticker = ImageFont.truetype("arial.ttf", 32)
        font_label = ImageFont.truetype("arial.ttf", 16)
        font_val = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font_title = font_sub = font_ticker = font_label = font_val = ImageFont.load_default()

    tgl = datetime.now().strftime("%d-%m-%Y")
    draw.text((padding, 28), "13-Sector AI Screener", fill="#10b981", font=font_title)
    draw.text((padding, 68), f"Scan Tanggal {tgl} | Main Automated", fill="#6b7280", font=font_sub)
    
    y_cursor = header_h
    for s in saham_list:
        card_box = [padding, y_cursor, width - padding, y_cursor + card_h]
        draw.rounded_rectangle(card_box, radius=22, fill="#ffffff", outline="#d1fae5", width=2)
        
        draw.rounded_rectangle([padding + 22, y_cursor + 20, padding + 78, y_cursor + 76], radius=14, fill="#d1fae5")
        draw.text((padding + 33, y_cursor + 34), s['ticker'][:2], fill="#059669", font=font_val)
        
        draw.text((padding + 95, y_cursor + 20), f"{s['ticker']}  [{s['rating']}]", fill="#111827", font=font_ticker)
        draw.text((padding + 95, y_cursor + 56), f"Last: Rp {s['price']:,} (+{s['pct']}%) • Vol {s['vol_spike']}x", fill="#6b7280", font=font_label)
        
        box_w = (width - (padding * 2) - 64) // 2
        box_h = 68
        col1_x = padding + 22
        col2_x = col1_x + box_w + 20
        row1_y = y_cursor + 95
        row2_y = row1_y + box_h + 14
        
        draw.rounded_rectangle([col1_x, row1_y, col1_x + box_w, row1_y + box_h], radius=12, fill="#f9fafb")
        draw.text((col1_x + 16, row1_y + 10), "TEKANAN BELI", fill="#9ca3af", font=font_label)
        draw.text((col1_x + 16, row1_y + 32), "Kuat (HAKA)", fill="#10b981", font=font_val)
        
        draw.rounded_rectangle([col2_x, row1_y, col2_x + box_w, row1_y + box_h], radius=12, fill="#f9fafb")
        draw.text((col2_x + 16, row1_y + 10), "BANDAR / FLOW", fill="#9ca3af", font=font_label)
        draw.text((col2_x + 16, row1_y + 32), f"Akumulasi ({s['cmf']})", fill="#10b981", font=font_val)
        
        draw.rounded_rectangle([col1_x, row2_y, col1_x + box_w, row2_y + box_h], radius=12, fill="#f9fafb")
        draw.text((col1_x + 16, row2_y + 10), "SENTIMEN TREN", fill="#9ca3af", font=font_label)
        draw.text((col1_x + 16, row2_y + 32), "Positif (Uptrend)", fill="#111827", font=font_val)
        
        draw.rounded_rectangle([col2_x, row2_y, col2_x + box_w, row2_y + box_h], radius=12, fill="#ecfdf5")
        draw.text((col2_x + 16, row2_y + 10), "TARGET 1", fill="#6b7280", font=font_label)
        draw.text((col2_x + 16, row2_y + 32), s['target_1'], fill="#059669", font=font_val)
        
        y_cursor += card_h + 24
        
    img.save(output_path)
    return output_path

def kirim_ke_telegram(image_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(image_path, "rb") as img_file:
        payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
        files = {"photo": img_file}
        requests.post(url, data=payload, files=files)

if __name__ == "__main__":
    print("Memulai screener utama 13 sektor...")
    hasil = jalankan_screener_batch()
    if hasil:
        img_file = generate_card_image(hasil)
        narasi = buat_narasi_ai(hasil)
        print("Mengirim hasil ke Telegram...")
        kirim_ke_telegram(img_file, narasi)
    else:
        print("Tidak ada saham yang memenuhi kriteria hari ini.")
