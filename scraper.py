import requests
import json
from datetime import datetime
import time

# 1. CẤU HÌNH PROXY (Đã thiết lập chuẩn)
PROXY_HOST = "14.250.212.38:36428"
PROXY_USER = "ZalMQa"
PROXY_PASS = "BRQrEd"
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}"

PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

# 2. HEADERS GIẢ LẬP
# Sofascore yêu cầu chặt chẽ Origin và Referer để xác thực nguồn gọi
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
    # Lấy ngày hiện tại theo định dạng YYYY-MM-DD
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Endpoint API ngầm của Sofascore lấy tất cả trận bóng đá trong ngày
    api_url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{current_date}"
    
    try:
        print(f"[{datetime.now()}] Đang kết nối API Sofascore ({current_date})...")
        
        # Gọi API qua proxy
        response = requests.get(api_url, headers=HEADERS, proxies=PROXIES, timeout=20)
        response.raise_for_status()
        
        # Parse JSON trả về
        raw_data = response.json()
        events = raw_data.get('events', [])
        
        print(f"Lấy thành công {len(events)} trận đấu từ Sofascore!")

        matches_list = []
        
        # Lọc và bóc tách dữ liệu
        for event in events:
            # Bỏ qua các giải đấu quá nhỏ nếu muốn, ở đây ta lấy toàn bộ
            
            # Xử lý thời gian thi đấu (Sofascore trả về Unix Timestamp)
            timestamp = event.get('startTimestamp')
            time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M") if timestamp else "N/A"
            
            # Thông tin đội bóng
            home_team = event['homeTeam']['name']
            away_team = event['awayTeam']['name']
            
            # Xử lý tỷ số và trạng thái trận đấu
            status_desc = event['status']['description'] # Vd: Not started, Ended, 1st half...
            
            # Sofascore phân chia điểm số rành mạch trong JSON
            home_score = event.get('homeScore', {}).get('current')
            away_score = event.get('awayScore', {}).get('current')
            
            if home_score is not None and away_score is not None:
                score_str = f"{home_score} - {away_score}"
            else:
                score_str = "vs"

            # Tối ưu hiển thị trạng thái sang tiếng Việt (Tuỳ chọn)
            status_vn = status_desc
            if status_desc == "Not started": status_vn = "Sắp diễn ra"
            elif status_desc == "Ended": status_vn = "FT"
            elif status_desc == "Halftime": status_vn = "HT"
            elif status_desc == "Canceled": status_vn = "Hủy"

            matches_list.append({
                "time": time_str,
                "home": home_team,
                "away": away_team,
                "score": score_str,
                "status": status_vn
            })

        # Đóng gói dữ liệu theo chuẩn file index.html cần đọc
        final_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "matches": matches_list
        }
        
        # Ghi đè vào file data.json
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
        print("Đã cập nhật data.json thành công!")

    except requests.exceptions.HTTPError as err:
        print(f"Lỗi HTTP (Có thể bị Cloudflare chặn hoặc sai API ngầm): {err}")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi Proxy / Mạng: {e}")
    except Exception as e:
        print(f"Lỗi bóc tách JSON: {e}")

if __name__ == "__main__":
    fetch_sofascore_api()
