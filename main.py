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
    """특정 아티스트를 검색하여 '재고가 있는' 상품만 반환"""
    url = f"https://gimbabrecords.com/product/search.html?keyword={artist_name.replace(' ', '+')}&cate_no=44"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 상품 리스트의 각 항목을 선택
        items = soup.select('.prdList > li')
        
        found_for_this_artist = []
        for item in items:
            # 1. 품절 여부 체크 (다양한 방식을 모두 검사)
            # - 이미지 태그에 soldout이 포함된 경우
            # - 클래스명에 soldout이나 stock_out이 포함된 경우
            # - 아이콘 영역에 '품절' 텍스트가 있는 경우
            icon_text = item.select_one('.icon')
            is_soldout_text = icon_text and ("품절" in icon_text.text or "SOLDOUT" in icon_text.text.upper())
            is_soldout_img = item.select_one('img[alt*="품절"], img[src*="soldout"]')
            
            if is_soldout_text or is_soldout_img:
                continue # 품절이면 다음 상품으로 넘어감
                
            # 2. 상품명 및 링크 추출
            name_tag = item.select_one('.name a')
            if not name_tag:
                continue
                
            name = name_tag.text.strip()
            link = "https://gimbabrecords.com" + name_tag['href']
            
            # 3. 아티스트 이름 포함 여부 확인
            if artist_name.lower() in name.lower():
                found_for_this_artist.append(f"💿 {name}\n🔗 바로가기: {link}")
        
        return found_for_this_artist
    except Exception as e:
        print(f"{artist_name} 검색 중 에러: {e}")
        return []

def main():
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
        print("현재 판매 중인 재고가 없습니다.")

if __name__ == "__main__":
    main()
