from curl_cffi import requests  # Thay thế requests thường bằng curl_cffi
import json
from datetime import datetime
import time

# 1. CẤU HÌNH PROXY
PROXY_HOST = "14.250.212.38:36428"
PROXY_USER = "ZalMQa"
PROXY_PASS = "BRQrEd"
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}"

PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

# 2. HEADERS GIẢ LẬP
# Với curl_cffi, ta không cần bộ Headers quá dài dòng vì nó đã tự động fake
HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/"
}

def fetch_sofascore_api():
    current_date = datetime.now().strftime("%Y-%m-%d")
    api_url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{current_date}"
    
    try:
        print(f"[{datetime.now()}] Đang kết nối API Sofascore ({current_date})...")
        
        # SỬ DỤNG curl_cffi VỚI THUỘC TÍNH impersonate
        response = requests.get(
            api_url, 
            headers=HEADERS, 
            proxies=PROXIES, 
            impersonate="chrome120", # Chìa khóa vượt qua Cloudflare
            timeout=30
        )
        
        # Nếu vẫn dính lỗi 403, in ra để debug
        if response.status_code != 200:
            print(f"Lỗi HTTP {response.status_code}: Bị chặn. Nội dung: {response.text[:100]}")
            return
            
        raw_data = response.json()
        events = raw_data.get('events', [])
        
        matches_list = []
        
        # BÓC TÁCH VÀ LỌC DỮ LIỆU
        for event in events:
            status_type = event.get('status', {}).get('type')
            
            # ĐIỀU KIỆN LỌC: Chỉ lấy trận "Chưa bắt đầu" (notstarted)
            if status_type != "notstarted":
                continue
                
            timestamp = event.get('startTimestamp')
            time_str = datetime.fromtimestamp(timestamp + 7 * 3600).strftime("%H:%M") if timestamp else "N/A"
            
            home_team = event['homeTeam']['name']
            away_team = event['awayTeam']['name']
            
            matches_list.append({
                "time": time_str,
                "home": home_team,
                "away": away_team,
                "score": "vs",
                "status": "Sắp diễn ra"
            })

        print(f"Lọc thành công: Còn lại {len(matches_list)} trận sắp diễn ra!")

        final_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "matches": matches_list
        }
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
        print("Đã cập nhật data.json thành công!")

    except Exception as e:
        print(f"Lỗi hệ thống hoặc bóc tách JSON: {e}")

if __name__ == "__main__":
    fetch_sofascore_api()
