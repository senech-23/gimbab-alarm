import requests
from bs4 import BeautifulSoup
import os

def send_telegram_msg(text):
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    # URL에 메시지를 전달하며 페이지 미리보기를 활성화합니다.
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': text,
        'disable_web_page_preview': 'false'
    }
    requests.get(url, params=params)

def check_gimbab(artist_name):
    """특정 아티스트를 검색하여 바이닐 목록을 반환하는 함수"""
    # 검색어 공백을 +로 치환하고, 바이닐 카테고리(cate_no=44)만 조회합니다.
    url = f"https://gimbabrecords.com/product/search.html?keyword={artist_name.replace(' ', '+')}&cate_no=44"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        products = soup.select('.name a')
        
        found_for_this_artist = []
        for p in products:
            name = p.text.strip()
            link = "https://gimbabrecords.com" + p['href']
            
            # 검색어가 상품명에 포함되어 있는지 확인 (대소문자 무시)
            if artist_name.lower() in name.lower():
                found_for_this_artist.append(f"💿 {name}\n🔗 바로가기: {link}")
        
        return found_for_this_artist
    except Exception as e:
        print(f"{artist_name} 검색 중 오류 발생: {e}")
        return []

def main():
    # ---------------------------------------------------------
    # 아티스트를 추가하고 싶을 때 아래 리스트에 이름을 추가하세요.
    # ---------------------------------------------------------
    target_artists = ["Nina Simone", "Dijon"]
    
    total_found = []
    
    for artist in target_artists:
        results = check_gimbab(artist)
        if results:
            total_found.extend(results)
    
    if total_found:
        msg = "🎺 [김밥레코즈] 입고 알림!\n\n" + "\n\n".join(total_found)
        send_telegram_msg(msg)
    else:
        print("현재 등록된 아티스트들의 새로운 바이닐 재고가 없습니다.")

if __name__ == "__main__":
    main()
