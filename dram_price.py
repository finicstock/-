import requests
import os
from datetime import datetime, timedelta
import re

now_kst = datetime.utcnow() + timedelta(hours=9)
today_str = now_kst.strftime('%Y-%m-%d %H:%M')

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def safe_float(text):
    """문자열에서 숫자만 추출하여 float로 변환 (실패 시 0.0 반환)"""
    try:
        clean_text = re.sub(r'[^-0.9.]', '', text)
        return float(clean_text) if clean_text else 0.0
    except:
        return 0.0

def get_ai_memory_data():
    url = "https://www.dramexchange.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        content = response.text
        
        msg = f"🤖 {today_str} AI/서버 메모리 시황\n"
        found_data = False

        targets = [
            ("DDR5 16Gb", r"DDR5 16Gb.*?4800/5600"),
            ("DDR4 16Gb", r"DDR4 16Gb.*?3200"),
            ("DDR4 8Gb", r"DDR4 8Gb.*?3200")
        ]
        
        for name, keyword in targets:
            try:
                pattern = re.compile(rf"{keyword}.*?</tr>", re.IGNORECASE | re.DOTALL)
                match = pattern.search(content)
                
                if match:
                    row_html = match.group(0)
                    # 숫자 및 퍼센트 패턴 추출
                    nums = re.findall(r"(\d+\.\d+)", row_html)
                    sign_match = re.search(r"([+-])\d+\.\d+\s*%", row_html)
                    sign = sign_match.group(1) if sign_match else ""
                    
                    if len(nums) >= 5:
                        price = nums[-2]   # Session Average 위치
                        change_val = safe_float(nums[-1])
                        
                        # 보합/상승/하락 로직
                        if change_val == 0.0:
                            emoji = "➖"
                        elif sign == "-":
                            emoji = "⬇️"
                        else:
                            emoji = "🔺"
                        
                        msg += f"\n🔸 {name}: ${price} ({emoji}{sign}{nums[-1]}%)"
                        found_data = True
            except:
                continue

        # DXI 지수 추출
        try:
            dxi_pattern = re.compile(r"DXI.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?).*?([+-])?(\d+\.\d+)\s*%", re.IGNORECASE | re.DOTALL)
            dxi_match = dxi_pattern.search(content)
            if dxi_match:
                val, d_sign, d_change = dxi_match.groups()
                d_sign = d_sign if d_sign else ""
                change_num = safe_float(d_change)
                
                if change_num == 0.0:
                    d_emoji = "➖"
                elif d_sign == "-":
                    d_emoji = "⬇️"
                else:
                    d_emoji = "🔺"
                msg += f"\n\n📈 DXI Index: {val} ({d_emoji}{d_sign}{d_change}%)"
                found_data = True
        except:
            pass

        msg += "\n\n#DRAM #HBM #반도체시황"
        return msg if found_data else "⚠️ 데이터를 찾지 못했습니다."

    except Exception as e:
        return f"❌ 실행 에러: {str(e)}"

def send_to_channel(text):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass

if __name__ == "__main__":
    result = get_ai_memory_data()
    send_to_channel(result)
