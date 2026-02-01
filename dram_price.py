import yfinance as yf
import requests
import os
from datetime import datetime, timedelta

# 한국 시간 설정
now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d')

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_dram_data():
    # D램 현물가 및 반도체 관련 지표
    # 지표 설명: DXI(DRAMeXchange Index)를 추종하려 노력하는 대용 티커들
    tickers = {
        "📟 D램 지수(DXI)": "DXI", 
        "📟 필라델피아 반도체": "^SOX"
    }
    
    results = f"💾 {today_str} 반도체/D램 시황\n"
    
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="5d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                emoji = "🔺" if change_pct > 0 else "⬇️"
                results += f"\n{name}: {current_price:,.2f} ({emoji} {abs(change_pct):.2f}%)"
            else:
                results += f"\n{name}: 업데이트 대기 중"
        except:
            results += f"\n{name}: 조회 불가"
            
    results += "\n\n#DRAM #반도체 #IT시황"
    return results

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    dram_info = get_dram_data()
    send_to_channel(dram_info)
