# producer.py
from kafka import KafkaProducer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import urllib.parse
import json
import time

def crawl_titles(query):
    chromedriver_autoinstaller.install()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    encoded_query = urllib.parse.quote(query)
    url = f"https://biz.chosun.com/nsearch/?query={encoded_query}&siteid=chosunbiz&website=chosunbiz&opt_chk=true"

    driver.get(url)
    time.sleep(3)  # JS 로딩 대기

    titles = []
    elements = driver.find_elements(By.CSS_SELECTOR, "a.story-card__headline")
    for elem in elements[:10]:
        title = elem.text
        link = elem.get_attribute("href")
        titles.append({"title": title, "link": link})

    driver.quit()
    return titles

def send_to_kafka(data):
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for item in data:
        producer.send('chosunbiz-news', value=item)
    producer.flush()
    producer.close()

if __name__ == "__main__":
    news_data = crawl_titles("두산")
    if news_data:
        send_to_kafka(news_data)
        print("✅ 뉴스 제목을 Kafka에 전송했습니다.")
    else:
        print("❌ 뉴스 제목을 찾지 못했습니다.")
