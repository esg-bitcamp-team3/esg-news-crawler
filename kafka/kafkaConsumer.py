from kafka import KafkaConsumer
import json

# Kafka Consumer 설정
consumer = KafkaConsumer(
    'news-raw',                           # 소비할 토픽 이름
    bootstrap_servers='localhost:9092',   # Kafka 서버 주소
    auto_offset_reset='earliest',         # 가장 처음 메시지부터 가져오기
    enable_auto_commit=True,              # 자동 offset 저장
    group_id='news-print-group-2',          # consumer 그룹 이름 (고유해야 함)
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # JSON 디코딩
)

print("📡 Kafka consumer 시작됨. 뉴스 기사 수신 대기 중...\n")

for message in consumer:
    article = message.value
    print("📰 [", article['company'], "]", article['date'])
    print("📌 제목:", article['title'])
    print("📝 내용 요약:", article.get('content', article.get('summary', '없음')))
    print("🔗 링크:", article.get('link', article.get('originallink', '없음')))
    print("-" * 80)
