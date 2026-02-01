import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

# 한국 시간 설정
now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d %H:%M')

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_dram_spot_price():
    url = "https://www.dramexchange.com/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # DRAMeXchange 메인 페이지의 가격 테이블 추출 (예시 포맷)
        # 실제 사이트 구조에 따라 선택자(Selector)는 조정될 수 있습니다.
        items = soup.select('#spot-price-table tr') 
        
        msg = f"💾 {today_str} DRAM 현물가 업데이트\n"
        
        # 주요 품목 필터링 (DDR4 8Gb 등)
        count = 0
        for item in items:
            cols = item.find_all('td')
            if len(cols) >= 3:
                name = cols[0].text.strip()
                price = cols[1].text.strip()
                change = cols[2].text.strip()
                
                if "DDR4 8Gb" in name or "DXI" in name:
                    emoji = "🔺" if "+" in change else "⬇️"
                    msg += f"\n🔸 {name}: ${price} ({emoji} {change})"
                    count += 1
            if count >= 5: break # 주요 항목 5개만 추출

        if count == 0:
            return "데이터를 읽어왔으나 표시할 항목이 없습니다."
        return msg

    except Exception as e:
        return f"DRAM 가격 크롤링 중 오류 발생: {e}"

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    dram_info = get_dram_spot_price()
    send_to_channel(dram_info)
