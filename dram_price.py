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

        targets = [
            ("DDR5 16Gb", r"DDR5 16Gb.*?4800/5600"),
            ("DDR4 16Gb", r"DDR4 16Gb.*?3200"),
            ("DDR4 8Gb", r"DDR4 8Gb.*?3200")
        ]
        
        for name, keyword in targets:
            pattern = re.compile(rf"{keyword}.*?</tr>", re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            
            if match:
                row_html = match.group(0)
                nums = re.findall(r"(\d+\.\d+)", row_html)
                # 부호 추출
                sign_match = re.search(r"([+-])\d+\.\d+\s*%", row_html)
                sign = sign_match.group(1) if sign_match else ""
                
                if len(nums) >= 6:
                    price = nums[4]   # Session Average
                    change = nums[5]  # Session Change
                    
                    # 변동률 숫자가 0.00인지 확인
                    is_zero = float(change) == 0.0
                    
                    if is_zero:
                        emoji = "➖"  # 보합 이모지
                    elif sign == "-":
                        emoji = "⬇️"  # 하락
                    else:
                        emoji = "🔺"  # 상승 (보통 +가 붙거나 부호가 없음)
                    
                    msg += f"\n🔸 {name}: ${price} ({emoji}{sign}{change}%)"
                    found_data = True

        # DXI 지수 추출 및 보합 로직 적용
        dxi_pattern = re.compile(r"DXI.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?).*?([+-])?(\d+\.\d+)\s*%", re.IGNORECASE | re.DOTALL)
        dxi_match = dxi_pattern.search(content)
        
        if dxi_match:
            dxi_val, dxi_sign, dxi_change = dxi_match.groups()
            dxi_sign = dxi_sign if dxi_sign else ""
            
            if float(dxi_change) == 0.0:
                dxi_emoji = "➖"
            elif dxi_sign == "-":
                dxi_emoji = "⬇️"
            else:
                dxi_emoji = "🔺"
                
            msg += f"\n\n📈 DXI Index: {dxi_val} ({dxi_emoji}{dxi_sign}{dxi_change}%)"
            found_data = True

        if not found_data:
            return "⚠️ 데이터를 매칭하지 못했습니다."
            
        msg += "\n\n#DRAM #HBM #반도체시황"
        return msg

    except Exception as e:
        return f"❌ 실행 에러: {str(e)}"

def send_to_channel(text):
    if not
