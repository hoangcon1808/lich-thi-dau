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

# BẢNG ƯU TIÊN GIẢI ĐẤU
LEAGUE_PRIORITY = {
    "World Cup": 1, "EURO": 2, "UEFA Champions League": 3, "UEFA Europa League": 4,
    "Premier League": 5, "LaLiga": 6, "Serie A": 7, "Bundesliga": 8,
    "Ligue 1": 9, "V-League": 10, "Saudi Professional League": 11, "MLS": 12
}

def get_priority(league_name):
    for key, priority in LEAGUE_PRIORITY.items():
        if key.lower() in league_name.lower():
            return priority
    return 99 

def fetch_sofascore_api():
    current_date = datetime.now().strftime("%Y-%m-%d")
    api_url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{current_date}"
    
    try:
        print(f"[{datetime.now()}] Đang kết nối API Sofascore ({current_date})...")
        
        response = requests.get(
            api_url, headers=HEADERS, proxies=PROXIES, impersonate="chrome120", timeout=30
        )
        
        if response.status_code != 200:
            print(f"Lỗi HTTP {response.status_code}: Bị chặn.")
            return
            
        raw_data = response.json()
        events = raw_data.get('events', [])
        
        # TẠO 2 TẬP DỮ LIỆU RIÊNG BIỆT
        live_leagues_dict = {}
        upcoming_leagues_dict = {}
        
        for event in events:
            status_type = event.get('status', {}).get('type')
            
            if status_type not in ["notstarted", "inprogress"]:
                continue
                
            timestamp = event.get('startTimestamp')
            time_str = datetime.fromtimestamp(timestamp + 7 * 3600).strftime("%H:%M") if timestamp else "N/A"
            
            home_team = event['homeTeam']['name']
            away_team = event['awayTeam']['name']
            
            is_live = (status_type == "inprogress")
            
            if is_live:
                home_score = event.get('homeScore', {}).get('current', 0)
                away_score = event.get('awayScore', {}).get('current', 0)
                score_str = f"{home_score} - {away_score}"
                
                status_desc = event.get('status', {}).get('description', 'Đang đá')
                if status_desc == "1st half": status_vn = "Hiệp 1"
                elif status_desc == "2nd half": status_vn = "Hiệp 2"
                elif status_desc == "Halftime": status_vn = "Nghỉ HT"
                elif status_desc == "Extra time": status_vn = "Hiệp phụ"
                elif status_desc == "Penalties": status_vn = "Luân lưu"
                else: status_vn = "Đang đá"
            else:
                score_str = "vs"
                status_vn = "Sắp diễn ra"
            
            # Lấy thông tin giải đấu
            tournament_info = event.get('tournament', {})
            league_name = tournament_info.get('name', 'Giải đấu khác')
            category_name = tournament_info.get('category', {}).get('name', '')
            full_league_name = f"{category_name} - {league_name}" if category_name else league_name
            
            # CHỌN ĐÚNG DICTIONARY ĐỂ THÊM VÀO
            target_dict = live_leagues_dict if is_live else upcoming_leagues_dict
            
            if full_league_name not in target_dict:
                target_dict[full_league_name] = {
                    "name": full_league_name,
                    "priority": get_priority(league_name),
                    "matches": []
                }
                
            target_dict[full_league_name]["matches"].append({
                "time": time_str,
                "home": home_team,
                "away": away_team,
                "score": score_str,
                "status": status_vn,
                "is_live": is_live
            })

        # Hàm trợ giúp để sắp xếp trận đấu theo giờ bên trong từng giải
        def sort_matches(leagues_dict):
            for league in leagues_dict.values():
                league["matches"] = sorted(league["matches"], key=lambda x: x["time"])
            return sorted(leagues_dict.values(), key=lambda x: (x['priority'], x['name']))

        # SẮP XẾP ĐỘC LẬP CHO CẢ 2 NHÓM THEO THỨ TỰ ƯU TIÊN GIẢI ĐẤU
        sorted_live = sort_matches(live_leagues_dict)
        sorted_upcoming = sort_matches(upcoming_leagues_dict)

        print(f"Thành công: {len(sorted_live)} giải đang đá | {len(sorted_upcoming)} giải sắp đá")

        # CẤU TRÚC JSON MỚI
        final_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (UTC)",
            "live_leagues": sorted_live,
            "upcoming_leagues": sorted_upcoming
        }
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    fetch_sofascore_api()
