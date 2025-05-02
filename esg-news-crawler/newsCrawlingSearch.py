import time
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# 크롬 드라이버 자동 설치
chromedriver_autoinstaller.install()

# 검색어 설정 및 URL 생성
query = "삼성전자"
encoded_query = urllib.parse.quote(query)
url = f"https://biz.chosun.com/nsearch/?query={encoded_query}&siteid=chosunbiz&website=chosunbiz&opt_chk=true"

# Selenium 옵션 설정
options = Options()
options.add_argument("--headless")  # 브라우저를 표시하지 않음
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 웹 드라이버 실행
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(3)  # 페이지 로딩 대기

# 기사 제목 추출
titles = []
articles = driver.find_elements(By.CSS_SELECTOR, "div.search-result-item")

for article in articles:
    try:
        title_element = article.find_element(By.CSS_SELECTOR, "a")
        title = title_element.text.strip()
        if title:
            titles.append(title)
    except:
        continue

driver.quit()

# 결과 확인 및 CSV 저장
if titles:
    df = pd.DataFrame(titles, columns=["title"])
    df.to_csv(f"{query}_chosun_titles.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 총 {len(titles)}개 기사 제목 저장 완료!")
else:
    print("⚠️ 기사 제목을 찾을 수 없습니다. 페이지 구조를 확인해주세요.")
