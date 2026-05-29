import requests
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
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Cache-Control": "max-age=0"
}

def fetch_sofascore_api():
    current_date = datetime.now().strftime("%Y-%m-%d")
    api_url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{current_date}"
    
    try:
        print(f"[{datetime.now()}] Đang kết nối API Sofascore ({current_date})...")
        
        response = requests.get(api_url, headers=HEADERS, proxies=PROXIES, timeout=20)
        response.raise_for_status()
        
        raw_data = response.json()
        events = raw_data.get('events', [])
        
        matches_list = []
        
        # BÓC TÁCH VÀ LỌC DỮ LIỆU
        for event in events:
            # Lấy loại trạng thái trận đấu
            status_type = event.get('status', {}).get('type')
            
            # ĐIỀU KIỆN LỌC: Chỉ lấy trận "Chưa bắt đầu" (notstarted)
            # Bỏ qua các trận inprogress (đang đá), finished (đã xong), canceled (hủy)...
            if status_type != "notstarted":
                continue
                
            # Xử lý thời gian thi đấu (Cộng thêm 7 tiếng cho múi giờ Việt Nam)
            timestamp = event.get('startTimestamp')
            time_str = datetime.fromtimestamp(timestamp + 7 * 3600).strftime("%H:%M") if timestamp else "N/A"
            
            # Thông tin đội bóng
            home_team = event['homeTeam']['name']
            away_team = event['awayTeam']['name']
            
            matches_list.append({
                "time": time_str,
                "home": home_team,
                "away": away_team,
                "score": "vs", # Trận chưa đá luôn để chữ "vs"
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

    except requests.exceptions.HTTPError as err:
        print(f"Lỗi HTTP: {err}")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi Proxy / Mạng: {e}")
    except Exception as e:
        print(f"Lỗi bóc tách JSON: {e}")

if __name__ == "__main__":
    fetch_sofascore_api()
