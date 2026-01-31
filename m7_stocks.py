import yfinance as yf
import requests
import os
from datetime import datetime, timedelta

# 한국 시간 설정
now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d')

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_m7_data():
    # M7 종목 + 마이크론(MU) 티커 설정
    tickers = {
        "🍎 애플": "AAPL",
        " Microsoft": "MSFT",
        " Google": "GOOGL",
        " Amazon": "AMZN",
        " NVIDIA": "NVDA",
        " Meta": "META",
        " Tesla": "TSLA",
        " MU 마이크론": "MU"
    }
    
    results = f"🚀 {today_str} M7+MU 종가 브리핑\n"
    
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="2d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                emoji = "🔺" if change_pct > 0 else "⬇️"
                results += f"\n{name}: ${current_price:.2f} ({emoji} {abs(change_pct):.2f}%)"
        except Exception:
            results += f"\n{name}: 조회 실패"
            
    results += "\n\n#M7 #미국주식 #빅테크 #반도체"
    return results

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    m7_info = get_m7_data()
    send_to_channel(m7_info)
