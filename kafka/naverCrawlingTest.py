from kafka import KafkaProducer
import requests
import urllib.parse
import json

# ✅ 네이버 Open API 인증
client_id = "M8dgVAY2wYMpK9KI5mc_"
client_secret = "g9UlamZAcu"

# ✅ Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

# ✅ 네이버 뉴스 검색 + Kafka 전송
def search_and_send_news(company_name, display=5):
    encoded_query = urllib.parse.quote(company_name)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display={display}&start=1&sort=date"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("❌ API 호출 오류:", response.status_code)
        return

    items = response.json()['items']
    for item in items:
        article = {
            "company": company_name,
            "title": item['title'],
            "date": item['pubDate'],
            "link": item['link'],
            "originallink": item.get('originallink', ''),
            "summary": item['description']
        }
        producer.send("news-raw", article)
        print(f"📤 전송됨: {article['title']}")

    producer.flush()
    print("✔ Kafka 전송 완료!")

# ✅ 실행
search_and_send_news("삼성전자", display=5)
