from kafka import KafkaProducer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import json
import time
import urllib.parse

# Kafka producer 설정
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

# 크롬 드라이버 자동 설치
chromedriver_autoinstaller.install()

# 크롤링 함수
def crawl_news(company_name):
    encoded_query = urllib.parse.quote(company_name)
    url = f"https://search.hani.co.kr/search/newslist?searchword={encoded_query}&startdate=2025.01.01&enddate=2025.12.31&sort=desc"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    articles = []

    items = driver.find_elements(By.CSS_SELECTOR, "dl.search")
    for item in items[:5]:  # 앞 5개만 가져오기
        try:
            title = item.find_element(By.CSS_SELECTOR, "dt > a").text
            content = item.find_element(By.CSS_SELECTOR, "dd").text
            date = item.find_element(By.CSS_SELECTOR, ".date").text
            articles.append({
                "company": company_name,
                "title": title,
                "content": content,
                "date": date
            })
        except:
            continue

    driver.quit()
    return articles

# 예시: "삼성전자" 기사 크롤링 후 Kafka로 전송
company_name = "삼성전자"
news_list = crawl_news(company_name)

for article in news_list:
    producer.send("news-raw", article)
    print(f"📤 Kafka로 전송됨: {article['title']}")

producer.flush()
print("✔ 모든 기사 전송 완료")
