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

        # 1. 개별 품목 타겟팅 (정교한 키워드 매칭)
        targets = [
            ("DDR5 16Gb", r"DDR5 16Gb.*?4800/5600"),
            ("DDR4 16Gb", r"DDR4 16Gb.*?3200"),
            ("DDR4 8Gb", r"DDR4 8Gb.*?3200")
        ]
        
        for name, keyword in targets:
            # 품목이 포함된 줄(Row)을 추출
            pattern = re.compile(rf"{keyword}.*?</tr>", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            
            if match:
                row_html = match.group(0)
                # 숫자만 모두 추출 (가격, 등락폭 등)
                nums = re.findall(r"(\d+\.\d+)", row_html)
                # 부호(+/-) 추출
                sign_match = re.search(r"([+-])\d+\.\d+\s*%", row_html)
                
                # 이미지 기준: 5번째 숫자가 Average, 마지막 숫자가 Change
                if len(nums) >= 6:
                    price = nums[4]
                    change = nums[-1]
                    sign = sign_match.group(1) if sign_match else ""
                    
                    emoji = "🔺" if sign == "+" else ("⬇️" if sign == "-" else "🔹")
                    msg += f"\n🔸 {name}: ${price} ({emoji}{sign}{change}%)"
                    found_data = True

        # 2. DXI Index 추출 (가장 확실한 패턴으로 수정)
        dxi_pattern = re.compile(r"DXI.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?).*?([+-])(\d+\.\d+)\s*%", re.IGNORECASE | re.DOTALL)
        dxi_match = dxi_pattern.search(content)
        
        if dxi_match:
            dxi_val = dxi_match.group(1)
            dxi_sign = dxi_match.group(2)
            dxi_change = dxi_match.group(3)
            dxi_emoji = "🔺" if dxi_sign == "+" else "⬇️"
            msg += f"\n\n📈 DXI Index: {dxi_val} ({dxi_emoji}{dxi_sign}{dxi_change}%)"
            found_data = True

        if not found_data:
            return "⚠️ 타겟 데이터를 매칭하지 못했습니다."
            
        msg += "\n\n#DRAM #HBM #반도체시황"
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
