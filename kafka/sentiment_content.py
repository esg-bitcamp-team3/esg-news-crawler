import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from kobert_transformers import get_kobert_model, get_tokenizer
import torch
import tensorflow as tf
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset, random_split
from sklearn.model_selection import train_test_split
from transformers import get_linear_schedule_with_warmup
from torch.optim import AdamW
import glob
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as pl
from sklearn.metrics import pairwise_distances_argmin_min
import matplotlib.pyplot as plt
import math
import re
import matplotlib.pyplot as plt

df_E = pd.read_csv("./ESG_keywords/E_Environment_Keywords_Unique.csv", header=0)
df_S = pd.read_csv("./ESG_keywords/G_Governance_Keywords_Unique.csv", header=0)
df_G = pd.read_csv("./ESG_keywords/S_Social_Keywords_Unique.csv", header=0)

Environment_keywords = pd.DataFrame(df_E)
Social_keywords = pd.DataFrame(df_S)
Governance_keywords = pd.DataFrame(df_G)

folder_path = ""
file_pattern = "*.csv"  # 예: 파일 이름에 '.csv'가 포함된 경우

# 파일 경로 리스트 불러오기
csv_files = glob.glob(os.path.join(folder_path, file_pattern))
print(csv_files)

model = BertForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment', num_labels=5)
tokenizer = BertTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

model2 = get_kobert_model()
tokenizer2 = get_tokenizer()

# 감성 분석
def classify_sentiment(text):
    # 텍스트를 토큰화
    inputs = tokenizer(text, padding=True, truncation=True, max_length=64, return_tensors='pt')

    # 입력 데이터를 GPU로 이동
    inputs = {key: val.to(device) for key, val in inputs.items()}

    # 모델 실행 (예측)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).item()  # 0: 매우 부정, 4: 매우 긍정

    return prediction

# 문장 나누기
def split_into_sentences(text):
    # 정규 표현식으로 문장 구분자 기준 분리
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # 공백 제거 및 빈 문장 제거
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

# 제목 벡터화
def vectorize_title(text):
    token = tokenizer2(text, return_tensors='pt', padding=True,
    truncation=True)
    model.eval()
    with torch.no_grad():
        vector = model2(**token)
    print(type(vector))
    print(vector)

    # "title_vector"라는 칼럼명으로 추가
    df["title_vector"] = vector["pooler_output"].tolist()
    print(df.head())
    
    


for file in csv_files:
    try:
        df = pd.read_csv(file, encoding='utf-8-sig', header=0)
        
        # 데이터가 없는 경우 (헤더만 존재)
        if df.empty:
            print(f"헤더만 있고 데이터가 없어 건너뜀: {file}")
            continue

    except pd.errors.EmptyDataError:
        print(f"파일이 완전히 비어 있어 건너뜀: {file}")
        continue

    df = df.dropna()
    df_list = df["title"].tolist()

    vectorize_title(df_list)

    for index, content in enumerate(df["content"]):

        content_no_space = content.replace(" ", "")
        # 환경 키워드 개수 계산
        e_count = sum((kw in content or kw.replace(" ", "") in content_no_space)
            for kw in Environment_keywords["Keyword"])
    
        # 사회 키워드 개수 계산
        s_count = sum((kw in content or kw.replace(" ", "") in content_no_space)
            for kw in Social_keywords["Keyword"])
    
        # 지배구조 키워드 개수 계산
        g_count = sum((kw in content or kw.replace(" ", "") in content_no_space)
            for kw in Governance_keywords["Keyword"])

        # 데이터프레임에 값 추가
        df.at[index, "E_value"] = e_count
        df.at[index, "S_value"] = s_count
        df.at[index, "G_value"] = g_count

        sentiment_list = []
        sentences = split_into_sentences(content)
        if len(sentences) < 4:
            for sentence in sentences[:2]:
                entiment = classify_sentiment(sentence)
                sentiment_list.append(sentiment)
        else:
            for sentence in sentences[:2] + sentences[-2:]:
                sentiment = classify_sentiment(sentence)
                sentiment_list.append(sentiment)
        
        sentiment_avg = sum(sentiment_list) / len(sentiment_list)
        # "title_vector"라는 칼럼명으로 추가
        df.at[index, "content_sentiment"] = sentiment_avg

    output_file = file  # 기존 파일에 덮어쓰기
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"저장 완료: {output_file}")

