from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import pandas as pd
import time
import urllib.parse

chromedriver_autoinstaller.install()

query = "삼성전자"
encoded_query = urllib.parse.quote(query)
url = f"https://www.chosun.com/nsearch/?query={encoded_query}"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

# 1. 검색 결과 페이지 접속
driver.get(url)
time.sleep(3)  # JS 렌더링 시간 확보

# 2. 기사 제목 추출
titles = []
articles = driver.find_elements(By.CSS_SELECTOR, "a.story-card__headline")

for a in articles:
    text = a.text.strip()
    if text:
        titles.append(text)

driver.quit()

# 3. 저장

df = pd.DataFrame(titles, columns=["title"])
df.to_csv(f"{query}_chosun_final.csv", index=False, encoding="utf-8-sig")

print(f"✅ 총 {len(titles)}개 기사 제목 저장 완료!")
