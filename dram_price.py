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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        content = response.text
        
        msg = f"🤖 {today_str} AI/서버 메모리 시황\n"
        found_data = False

        # 찾고 싶은 키워드들 (DDR5, DDR4, DXI 등)
        targets = ["DDR5 16Gb", "DDR4 16Gb", "DDR4 8Gb"]
        
        for target in targets:
            # 더 유연한 정규식: 품목명 뒤에 나오는 첫 번째 숫자(가격)와 등락폭 추출
            pattern = re.compile(rf"{target}.*?(\d+\.\d+).*?([+-]\d+\.\d+)", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            
            if match:
                price = match.group(1)
                change = match.group(2)
                emoji = "🔺" if "+" in change else "⬇️"
                msg += f"\n🔸 {target}: ${price} ({emoji}{change.replace('+', '')}%)"
                found_data = True

        # DXI 지수 별도 추출
        dxi_pattern = re.compile(r"DXI.*?(\d+[\d,.]*).*?([+-]\d+\.\d+)", re.IGNORECASE | re.DOTALL)
        dxi_match = dxi_pattern.search(content)
        if dxi_match:
            emoji = "🔺" if "+" in dxi_match.group(2) else "⬇️"
            msg += f"\n\n📈 DXI Index: {dxi_match.group(1)} ({emoji}{dxi_match.group(2).replace('+', '')}%)"
            found_data = True

        if not found_data:
            return "⚠️ 현재 페이지에서 데이터를 찾을 수 없습니다. (구조 변경 확인 필요)"
            
        msg += "\n\n#DRAM #HBM #AI반도체"
        return msg

    except Exception as e:
        return f"❌ 실행 에러 발생: {str(e)}"

def send_to_channel(text):
    if not TOKEN or not CHAT_ID:
        print("토큰이나 챗 ID가 설정되지 않았습니다.")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    result = get_ai_memory_data()
    send_to_channel(result)
