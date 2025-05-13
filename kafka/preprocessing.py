from kafka import KafkaConsumer
import json
import re
import torch
import pandas as pd
from kobert_transformers import get_kobert_model, get_tokenizer
from transformers import BertTokenizer, BertForSequenceClassification
import os
import pandas as pd
from pymongo import MongoClient

# 저장 파일 이름
csv_file = "esg_predictions.csv"

# Atlas URI
# MONGO_URI = "mongodb+srv://jinpang97:MONGOsj!0122@cluster0.bxnwcsi.mongodb.net/CrawlData"
MONGO_URI = "mongodb+srv://jinpang97:MONGOsj!0122@cluster0.bxnwcsi.mongodb.net/?retryWrites=true&w=majority"

# MongoDB 연결 설정
client = MongoClient(MONGO_URI)
db = client["CrawlData"]  # 원하는 DB 이름
collection = db["crawlingPreprocessing"]  # 원하는 collection 이름

def save_result_to_mongo(result):
    try:
        collection.insert_one(result)
        print("🌍 MongoDB 저장 완료!")
    except Exception as e:
        print("❌ MongoDB 저장 실패:", e)


# 파일이 없으면 헤더 포함 저장, 있으면 append
def save_result_to_csv(result):
    df_row = pd.DataFrame([result])
    if not os.path.exists(csv_file):
        df_row.to_csv(csv_file, index=False, encoding='utf-8-sig')
    else:
        df_row.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8-sig')

# 모델 준비
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
kobert_model = get_kobert_model().to(device)
kobert_tokenizer = get_tokenizer()

bert_model = BertForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment', num_labels=5)
bert_tokenizer = BertTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
bert_model.to(device)

# 키워드 로딩
df_E = pd.read_csv("./ESG_keywords/E_Environment_Keywords_Unique.csv")
df_S = pd.read_csv("./ESG_keywords/S_Social_Keywords_Unique.csv")
df_G = pd.read_csv("./ESG_keywords/G_Governance_Keywords_Unique.csv")

env_keywords = df_E["Keyword"].tolist()
soc_keywords = df_S["Keyword"].tolist()
gov_keywords = df_G["Keyword"].tolist()

# 문장 분리
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

# 감성 분석
def classify_sentiment(text):
    inputs = bert_tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=64)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = bert_model(**inputs).logits
        pred = torch.argmax(logits, dim=1).item()
    return pred

# 키워드 카운트
def count_keywords(content, keywords):
    no_space = content.replace(" ", "")
    return sum((kw in content or kw.replace(" ", "") in no_space) for kw in keywords)

# Kafka Consumer
consumer = KafkaConsumer(
    'news-raw',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='esg-analyzer',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("✅ ESG 분석 Consumer 시작됨...\n")

for msg in consumer:
    news = msg.value
    title = news['title']
    content = news.get('content') or news.get('summary') or ''
    company = news.get('company', 'N/A')
    date = news.get('date', 'N/A')

    # 키워드 개수 계산
    e_count = count_keywords(content, env_keywords)
    s_count = count_keywords(content, soc_keywords)
    g_count = count_keywords(content, gov_keywords)

    # 감성 분석
    sentences = split_into_sentences(content)
    selected = sentences[:2] + sentences[-2:] if len(sentences) >= 4 else sentences
    sentiment_scores = [classify_sentiment(s) for s in selected]
    sentiment_avg = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 2  # 중립값

    # 결과 구성
    result = {
        "company": company,
        "date": date,
        "title": title,
        "E_value": e_count,
        "S_value": s_count,
        "G_value": g_count,
        "content_sentiment": sentiment_avg
    }

    print("📊 분석 완료:", result)
    save_result_to_csv(result)  # CSV 저장
    save_result_to_mongo(result) #atlas 저장
    print("저장 완료: esg_predictions.csv")
    print("-" * 80)

    # TODO: MongoDB에 저장하거나 Kafka로 다시 전송 가능

