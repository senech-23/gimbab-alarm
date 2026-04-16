Python
import requests
from bs4 import BeautifulSoup
import os

def send_telegram_msg(text):
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
    requests.get(url)

def check_album():
    url = "https://gimbabrecords.com/product/search.html?keyword=nina+simone"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 상품 이름 추출 (김밥레코즈의 상품명 태그 기준)
    products = soup.select('.name a')
    found_albums = [p.text.strip() for p in products if "Nina Simone" in p.text or "니나 시몬" in p.text]
    
    if found_albums:
        msg = "🎵 김밥레코즈 Nina Simone 입고 알림!\n\n" + "\n".join(found_albums)
        send_telegram_msg(msg)
    else:
        print("아직 새로운 앨범이 없습니다.")

if __name__ == "__main__":
    check_album()
