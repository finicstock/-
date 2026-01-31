import yfinance as yf
import requests
import os

# 깃허브에서 설정한 비밀 정보를 가져옵니다
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_market_data():
    tickers = {
        "💵 달러지수": "DX-Y.NYB", 
        "📈 미 10년물 금리": "^TNX", 
        "🏛 S&P 500": "^GSPC", 
        "🚀 나스닥": "^IXIC"
    }
    results = "📢 [경제 지표 브리핑]\n"
    for name, sym in tickers.items():
        ticker = yf.Ticker(sym)
        price = ticker.fast_info.last_price
        results += f"\n{name}: {price:.2f}"
    results += "\n\n#미국증시 #경제지표 #자동업데이트"
    return results

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    market_info = get_market_data()
    send_to_channel(market_info)
