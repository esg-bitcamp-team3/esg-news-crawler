from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import pandas as pd
import time
import urllib.parse

# 기본 세팅
chromedriver_autoinstaller.install()
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

# 검색어 세팅
query = "삼성전자"
encoded_query = urllib.parse.quote(query)
url = f"https://www.chosun.com/nsearch/?query={encoded_query}"

titles = []

# 1. 검색 결과 페이지 열기
driver.get(url)
time.sleep(3)

# 2. 기사 제목 가져오기
articles = driver.find_elements(By.CSS_SELECTOR, "a.story-card__headline")

for a in articles:
    title = a.text.strip()
    # ✅ 제목에 검색어 포함된 것만 저장
    if query in title:
        titles.append(title)

driver.quit()

# 3. CSV 저장
df = pd.DataFrame(titles, columns=["title"])
df.to_csv(f"{query}_chosun_filtered.csv", index=False, encoding="utf-8-sig")

print(f"✅ '{query}' 포함된 제목만 {len(titles)}개 저장 완료!")
