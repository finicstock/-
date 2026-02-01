import requests
import os
from datetime import datetime, timedelta
import re

now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d %H:%M')

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_ai_memory_data():
    url = "https://www.dramexchange.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        content = response.text
        
        msg = f"🤖 {today_str} AI/서버 메모리 시황\n"
        found_data = False

        # 닉스님이 올려주신 이미지의 표 순서와 사양에 맞게 정밀 타겟팅
        # (이름, 검색 키워드)
        targets = [
            ("DDR5 16Gb (주류)", "DDR5 16Gb.*?\d+/\d+"),
            ("DDR4 16Gb (주류)", "DDR4 16Gb.*?3200"),
            ("DDR4 8Gb (주류)", "DDR4 8Gb.*?3200")
        ]
        
        for name, keyword in targets:
            # 패턴 설명: 품목명...세션평균...세션변동률 순서로 추출
            # 이미지상의 'Session Average'와 'Session Change' 값을 타겟팅합니다.
            pattern = re.compile(rf"{keyword}.*?(\d+\.\d+).*?(\d+\.\d+).*?(\d+\.\d+).*?(\d+\.\d+).*?(\d+\.\d+).*?([+-]?\d+\.\d+)\s*%", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            
            if match:
                price = match.group(5)  # Session Average 값
                change = match.group(6) # Session Change (%) 값
                
                emoji = "🔺" if float(change) > 0 else ("⬇️" if float(change) < 0 else "🔹")
                msg += f"\n🔸 {name}: ${price} ({emoji}{change}%)"
                found_data = True

        if not found_data:
            return "⚠️ 타겟 품목 데이터를 찾지 못했습니다. 사이트 구조를 확인해주세요."
            
        msg += "\n\n#DRAM #HBM #반도체정밀시황"
        return msg

    except Exception as e:
        return f"❌ 실행 에러: {str(e)}"

def send_to_channel(text):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    result = get_ai_memory_data()
    send_to_channel(result)
