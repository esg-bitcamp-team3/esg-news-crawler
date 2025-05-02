# consumer.py
from kafka import KafkaConsumer
import json
import pandas as pd

consumer = KafkaConsumer(
    'chosunbiz-news',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

news_list = []
for message in consumer:
    news = message.value
    news_list.append(news)
    print(f"📥 수신한 뉴스: {news['title']}")
    if len(news_list) >= 10:
        break

df = pd.DataFrame(news_list)
df.to_csv("chosunbiz_samsung_news.csv", index=False, encoding="utf-8-sig")
print("✅ CSV 파일로 저장 완료: chosunbiz_samsung_news.csv")
