from curl_cffi import requests
import json
from datetime import datetime

# 1. CẤU HÌNH PROXY
PROXY_HOST = "14.250.212.38:36428"
PROXY_USER = "ZalMQa"
PROXY_PASS = "BRQrEd"
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}"

PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/"
}

# BẢNG ƯU TIÊN GIẢI ĐẤU (Số càng nhỏ, xếp càng cao)
# Mặc định các giải không có trong danh sách này sẽ có mức ưu tiên là 99 (xếp cuối)
LEAGUE_PRIORITY = {
    "World Cup": 1,
    "EURO": 2,
    "UEFA Champions League": 3,
    "UEFA Europa League": 4,
    "Premier League": 5,      # Ngoại Hạng Anh
    "LaLiga": 6,              # Tây Ban Nha
    "Serie A": 7,             # Ý
    "Bundesliga": 8,          # Đức
    "Ligue 1": 9,             # Pháp
    "V-League": 10,           # Việt Nam
    "Saudi Professional League": 11,
    "MLS": 12
}

def get_priority(league_name):
    # Kiểm tra xem tên giải đấu có chứa các từ khóa ưu tiên ở trên không
    for key, priority in LEAGUE_PRIORITY.items():
        if key.lower() in league_name.lower():
            return priority
    return 99 # Nhóm các giải cỏ, giải phụ xuống cuối

def fetch_sofascore_api():
    current_date = datetime.now().strftime("%Y-%m-%d")
    api_url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{current_date}"
    
    try:
        print(f"[{datetime.now()}] Đang kết nối API Sofascore ({current_date})...")
        
        response = requests.get(
            api_url, 
            headers=HEADERS, 
            proxies=PROXIES, 
            impersonate="chrome120", 
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Lỗi HTTP {response.status_code}: Bị chặn.")
            return
            
        raw_data = response.json()
        events = raw_data.get('events', [])
        
        # Dùng Dictionary để nhóm các trận đấu theo giải
        leagues_dict = {}
        total_matches = 0
        
        for event in events:
            status_type = event.get('status', {}).get('type')
            
            if status_type != "notstarted":
                continue
                
            timestamp = event.get('startTimestamp')
            time_str = datetime.fromtimestamp(timestamp + 7 * 3600).strftime("%H:%M") if timestamp else "N/A"
            
            home_team = event['homeTeam']['name']
            away_team = event['awayTeam']['name']
            
            # LẤY THÔNG TIN GIẢI ĐẤU
            tournament_info = event.get('tournament', {})
            league_name = tournament_info.get('name', 'Giải đấu khác')
            category_name = tournament_info.get('category', {}).get('name', '') # Lấy tên quốc gia (Vd: England)
            
            # Gộp tên quốc gia và tên giải (Ví dụ: England - Premier League)
            full_league_name = f"{category_name} - {league_name}" if category_name else league_name
            
            # Nếu giải này chưa có trong dict, tạo mới
            if full_league_name not in leagues_dict:
                leagues_dict[full_league_name] = {
                    "name": full_league_name,
                    "priority": get_priority(league_name),
                    "matches": []
                }
                
            # Thêm trận đấu vào đúng giải của nó
            leagues_dict[full_league_name]["matches"].append({
                "time": time_str,
                "home": home_team,
                "away": away_team,
                "score": "vs",
                "status": "Sắp diễn ra"
            })
            total_matches += 1

        # SẮP XẾP: Các giải có priority nhỏ xếp trước, nếu bằng nhau thì xếp theo tên chữ cái
        sorted_leagues = sorted(leagues_dict.values(), key=lambda x: (x['priority'], x['name']))

        print(f"Lọc thành công: {total_matches} trận sắp diễn ra từ {len(sorted_leagues)} giải đấu!")

        final_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (UTC)",
            "leagues": sorted_leagues # Cấu trúc JSON mới: Danh sách các giải đấu
        }
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
        print("Đã cập nhật data.json thành công!")

    except Exception as e:
        print(f"Lỗi hệ thống hoặc bóc tách JSON: {e}")

if __name__ == "__main__":
    fetch_sofascore_api()
