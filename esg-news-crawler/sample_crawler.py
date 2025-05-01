from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import pandas as pd
import time

chromedriver_autoinstaller.install()

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

data = []

search_url = "https://www.yna.co.kr/search/index?query=삼성전자&from=2023-01-01&to=2023-12-31"
driver.get(search_url)
time.sleep(2)

# ✅ 스크롤 강제 실행 → 동적 기사 로딩 유도
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)

# ✅ 다시 기사 리스트 읽기
articles = driver.find_elements(By.CSS_SELECTOR, 'div.section01 dl dt a')

print(f"총 기사 수: {len(articles)}")

for article in articles:
    title = article.text.strip()
    link = article.get_attribute("href")

    if not link.startswith("http"):
        continue

    driver.get(link)
    time.sleep(2)

    try:
        content = driver.find_element(By.CSS_SELECTOR, "#articleWrap").text.strip()
    except:
        content = "본문 없음"

    print(f"[TITLE] {title}\n[LINK] {link}\n[CONTENT] {content[:30]}...\n")

    data.append(["삼성전자", 2023, title, content])

driver.quit()

df = pd.DataFrame(data, columns=["회사명", "년도", "title", "contents"])
df.to_csv("news_articles.csv", index=False, encoding="utf-8-sig")
