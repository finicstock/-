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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # DRAMeXchange의 현물가 테이블 섹션을 더 정확하게 타겟팅
        # 클래스명이나 ID가 수시로 변하므로, 테이블 태그 자체를 탐색
        tables = soup.find_all('table')
        
        msg = f"💾 {today_str} DRAM 현물가 브리핑\n"
        found_data = False

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    name = cols[0].text.strip()
                    price = cols[1].text.strip()
                    change = cols[2].text.strip()
                    
                    # 'DDR'이나 'DXI' 문구가 포함된 행만 추출
                    if any(keyword in name for keyword in ["DDR4", "DDR5", "DXI", "Spot"]):
                        emoji = "🔺" if "+" in change else "⬇️"
                        msg += f"\n🔸 {name}: ${price} ({emoji}{change})"
                        found_data = True

        if not found_data:
            # 만약 위 방법으로도 안 잡히면, 페이지 내의 모든 텍스트 중 숫자가 포함된 부분이라도 시도
            return "⚠️ 사이트 구조 변경으로 데이터를 추출할 수 없습니다. 수동 점검이 필요합니다."
            
        return msg

    except Exception as e:
        return f"❌ 크롤링 에러 발생: {str(e)}"

def send_to_channel(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    dram_info = get_dram_spot_price()
    send_to_channel(dram_info)
