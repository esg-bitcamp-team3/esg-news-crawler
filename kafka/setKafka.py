from kafka import KafkaConsumer
from pymongo import MongoClient
import json
from kobert_transformer import predict_esg_scores  # 당신이 만든 KoBERT 예측 함수

# MongoDB 연결
mongo_client = MongoClient("mongodb+srv://jinpang97:MONGOsj!0122@cluster0.bxnwcsi.mongodb.net/CompanyInfo")
db = mongo_client["esg_db"]
collection = db["esg_predictions"]

# Kafka consumer 설정
consumer = KafkaConsumer(
    'news-raw',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='esg-consumer-group',
    value_serializer=lambda m: json.loads(m.decode('utf-8'))
)

for msg in consumer:
    news = json.loads(msg.value.decode('utf-8'))
    print(f"📥 수신 뉴스: {news['title']}")

    # KoBERT 기반 예측 (가정: 리턴값이 dict)
    result = predict_esg_scores(news["content"])  # 예: {'E': 72, 'S': 58, 'G': 81}

    news_with_score = {
        **news,
        "esg_score": result
    }

    collection.insert_one(news_with_score)
    print(f"✔ 저장 완료: {news_with_score}")
