import requests
from bs4 import BeautifulSoup
import os

def send_telegram_msg(text):
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': text,
        'disable_web_page_preview': 'false'
    }
    requests.get(url, params=params)

def check_gimbab(artist_name):
    """특정 아티스트를 검색하여 '품절되지 않은' 바이닐 목록만 반환"""
    url = f"https://gimbabrecords.com/product/search.html?keyword={artist_name.replace(' ', '+')}&cate_no=44"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 각 상품 아이템을 감싸고 있는 박스를 찾습니다.
        # 김밥레코즈는 보통 'description' 클래스 안에 상품 정보가 있습니다.
        items = soup.select('.prdList > li')
        
        found_for_this_artist = []
        for item in items:
            # 1. 품절 여부 확인 (품절 아이콘/이미지가 있는지 체크)
            is_soldout = item.select_one('img[src*="soldout"]') or item.select_one('.icon__stock_out')
            if is_soldout:
                continue
                
            # 2. 상품명과 링크 추출
            name_tag = item.select_one('.name a')
            if not name_tag:
                continue
                
            name = name_tag.text.strip()
            link = "https://gimbabrecords.com" + name_tag['href']
            
            # 3. 검색어가 상품명에 포함되어 있는지 확인 (대소문자 무시)
            if artist_name.lower() in name.lower():
                found_for_this_artist.append(f"💿 {name}\n🔗 바로가기: {link}")
        
        return found_for_this_artist
    except Exception as e:
        print(f"{artist_name} 검색 중 오류 발생: {e}")
        return []

def main():
    # 추적하고 싶은 아티스트 리스트
    target_artists = ["Nina Simone", "Dijon"]
    
    total_found = []
    
    for artist in target_artists:
        results = check_gimbab(artist)
        if results:
            total_found.extend(results)
    
    if total_found:
        msg = "🎺 [김밥레코즈] 바로 구매 가능!\n\n" + "\n\n".join(total_found)
        send_telegram_msg(msg)
    else:
        print("현재 등록된 아티스트들의 구매 가능한 바이닐이 없습니다.")

if __name__ == "__main__":
    main()
