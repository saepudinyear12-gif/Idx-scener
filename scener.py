import os
import requests
import yfinance as yf

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

watchlist_idx = [
    'BBCA.JK',
    'ASII.JK',
    'BBRI.JK',
    'BMRI.JK',
    'BBNI.JK',
    'ANTM.JK',
    'TLKM.JK',
    'ADRO.JK',
]


def send_telegram_message(message):
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
  payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
  requests.post(url, json=payload)


def run_stock_screener():
  for ticker in watchlist_idx:
    try:
      stock = yf.Ticker(ticker)
      df = stock.history(period='1mo')
      if len(df) < 20:
        continue

      current_price = df['Close'].iloc[-1]
      prev_price = df['Close'].iloc[-2]
      avg_volume = df['Volume'].iloc[-21:-1].mean()
      current_volume = df['Volume'].iloc[-1]

      if current_volume > (avg_volume * 1.5) and current_price > prev_price:
        clean_name = ticker.replace('.JK', '')
        change_pct = ((current_price - prev_price) / prev_price) * 100

        message = (
            f'🚨 *SINYAL POTENSI NAIK (SCREENER)* 🚨\n\n'
            f'🔹 *Emiten:* `{clean_name}`\n'
            f'💰 *Harga:* Rp {current_price:,.0f}\n'
            f'📈 *Perubahan:* +{change_pct:.2f}%'
        )
        send_telegram_message(message)
    except Exception as e:
      print(f'Error pada {ticker}: {e}')


if __name__ == '__main__':
  run_stock_screener()
