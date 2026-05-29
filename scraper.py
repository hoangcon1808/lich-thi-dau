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

# 2. BỘ HEADERS GIẢ LẬP TRÌNH DUYỆT (Tránh bị chặn)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

def scrape_data():
    target_url = "https://www.flashscore.com/" 
    
    try:
        print(f"[{datetime.now()}] Đang kết nối tới {target_url} qua Proxy...")
        response = requests.get(target_url, headers=HEADERS, proxies=PROXIES, timeout=20)
        response.raise_for_status()
        
        html_content = response.text
        print(f"Lấy thành công mã nguồn: {len(html_content)} bytes.")

        # =================================================================
        # TODO: VIẾT LOGIC BÓC TÁCH DỮ LIỆU TỪ HTML TẠI ĐÂY (Dùng BeautifulSoup)
        # Ví dụ: soup = BeautifulSoup(html_content, 'html.parser')
        # =================================================================
        
        # DỮ LIỆU MẪU (Mock Data) ĐỂ TEST GIAO DIỆN VÀ GITHUB ACTIONS
        scraped_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "matches": [
                {"time": "02:00", "home": "Real Madrid", "away": "Dortmund", "score": "2 - 1", "status": "FT"},
                {"time": "22:00", "home": "Man Utd", "away": "Man City", "score": "vs", "status": "Sắp diễn ra"},
                {"time": "23:30", "home": "Arsenal", "away": "Liverpool", "score": "1 - 0", "status": "HT"}
            ]
        }
        
        # 3. LƯU DỮ LIỆU VÀO FILE JSON
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)
            
        print("Đã lưu dữ liệu vào data.json thành công!")

    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối / Lỗi Proxy: {e}")
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    scrape_data()
