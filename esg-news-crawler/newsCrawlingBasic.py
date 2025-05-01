from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import pandas as pd
import time

chromedriver_autoinstaller.install()

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

driver.get("https://www.yna.co.kr")
time.sleep(5)  # 충분히 로딩 대기

links = driver.find_elements(By.TAG_NAME, "a")

titles = []

for link in links:
    text = link.text.strip()
    if text and len(text) > 10:
        titles.append(text)

driver.quit()

# ✅ CSV로 저장
df = pd.DataFrame(titles, columns=["title"])
df.to_csv("news_titles.csv", index=False, encoding="utf-8-sig")

print(f"✅ 총 {len(titles)}개의 제목을 news_titles.csv 파일로 저장했습니다.")
