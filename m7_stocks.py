import yfinance as yf
import requests
import os
from datetime import datetime, timedelta

# 한국 시간(UTC+9) 설정
now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d')

# 깃허브 Secrets에서 토큰과 ID 가져오기
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_m7_data():
    # M7 종목 리스트 + 마이크론(MU)
    tickers = {
        "🍎 애플": "AAPL",
        "💻 마이크로소프트": "MSFT",
        "🔍 구글": "GOOGL",
        "📦 아마존": "AMZN",
        "🦾 엔비디아": "NVDA",
        "📱 메타": "META",
        "🚗 테슬라": "TSLA",
        "💾 마이크론": "MU"
    }
    
    results = f"🚀 {today_str} M7 + MU 종가 정보\n"
    
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            # 마감 직후이므로 안정적으로 5일치 데이터를 가져와서 계산
            hist = t.history(period="5d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                # 상승 🔺, 하락 ⬇️ (닉스님 취향 반영!)
                emoji = "🔺" if change_pct > 0 else "⬇️"
                results += f"\n{name}: ${current_price:.2f} ({emoji} {abs(change_pct):.2f}%)"
            else:
                results += f"\n{name}: 데이터 미비"
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
