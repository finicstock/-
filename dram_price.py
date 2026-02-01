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

        # 1. 개별 품목 타겟팅 (줄 단위 정밀 매칭)
        # 각 행(tr)의 텍스트를 먼저 찾고 그 안에서 가격과 변동률을 추출합니다.
        targets = [
            ("DDR5 16Gb", r"DDR5 16Gb.*?4800/5600"),
            ("DDR4 16Gb", r"DDR4 16Gb.*?3200"),
            ("DDR4 8Gb", r"DDR4 8Gb.*?3200")
        ]
        
        for name, keyword in targets:
            # 품목이 포함된 전체 행 텍스트를 추출
            row_pattern = re.compile(rf"{keyword}.*?</tr>", re.IGNORECASE | re.DOTALL)
            row_match = row_pattern.search(content)
            
            if row_match:
                row_text = row_match.group(0)
                # 해당 행 안에서 5번째 숫자(Average)와 6번째 숫자(Change) 추출
                nums = re.findall(r"([+-]?\d+\.\d+)", row_text)
                if len(nums) >= 6:
                    price = nums[4]   # Session Average
                    change = nums[5]  # Session Change
                    emoji = "🔺" if float(change) > 0 else ("⬇️" if float(change) < 0 else "🔹")
                    msg += f"\n🔸 {name}: ${price} ({emoji}{change}%)"
                    found_data = True

        # 2. DXI 지수 추출
        # DXI는 별도의 영역에 있으므로 패턴을 단순화하여 다시 잡습니다.
        dxi_pattern = re.compile(r"DXI.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?).*?([+-]?\d+\.\d+)\s*%", re.IGNORECASE | re.DOTALL)
        dxi_match = dxi_pattern.search(content)
        
        if dxi_match:
            dxi_val = dxi_match.group(1)
            dxi_change = dxi_match.group(2)
            dxi_emoji = "🔺" if float(dxi_change) > 0 else ("⬇️" if float(dxi_change) < 0 else "🔹")
            msg += f"\n\n📈 DXI Index: {dxi_val} ({dxi_emoji}{dxi_change}%)"
            found_data = True

        if not found_data:
            return "⚠️ 데이터를 매칭하지 못했습니다. 사이트 구조를 재확인해주세요."
            
        msg += "\n\n#DRAM #HBM #반도체시황 #DXI"
        return msg

    except Exception as e:
        return f"❌ 실행 에러: {str(e)}"

def send_to_channel(text):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.
