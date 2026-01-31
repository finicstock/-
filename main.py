import yfinance as yf
import requests
import os
from datetime import datetime, timedelta

# UTC 시간을 한국 시간(UTC+9)으로 변환
now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d')

# 깃허브 Secrets에서 가져오기
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_market_data():
    tickers = {
        "📊 나스닥 선물": "NQ=F",
        "📊 S&P500 선물": "ES=F",
        "📊 다우 선물": "YM=F",
        "🇺🇸 미 채권 2년물": "2Y=F", # 2Y=F가 안되면 ^ZT로 자동 시도하도록 하단 보강
        "🇺🇸 미 채권 10년물": "^TNX",
        "💵 달러지수": "DX-Y.NYB",
        "🇰🇷 달러/원 환율": "USDKRW=X"
    }
    
    results = f"📅 {today_str} 시장 브리핑\n"
    
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            
            # [전략] 먼저 5일치 데이터를 가져옵니다.
            hist = t.history(period="5d")
            
            # 데이터가 있으면 (최소 1개 이상)
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                
                # 등락 계산이 가능할 때 (데이터 2개 이상)
                if len(hist) >= 2:
                    prev_price = hist['Close'].iloc[-2]
                    change = current_price - prev_price
                    change_pct = (change / prev_price) * 100
                    emoji = "🔺" if change > 0 else "🔻"
                    results += f"\n{name}: {current_price:,.2f} ({emoji} {abs(change_pct):.2f}%)"
                else:
                    # 데이터가 1개뿐이면 가격만 표시
                    results += f"\n{name}: {current_price:,.2f} (변동 확인불가)"
            else:
                # hist가 완전히 비었을 때 최후의 수단으로 현재가 직접 조회
                price = t.fast_info.last_price
                if price:
                    results += f"\n{name}: {price:,.2f} (현재가)"
                else:
                    results += f"\n{name}: 점검 중"
                    
        except Exception:
            results += f"\n{name}: 조회 일시중단"
            
    results += "\n\n#미국증시 #주요지수 #환율 #채권금리"
    return results

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    market_info = get_market_data()
    send_to_channel(market_info)
