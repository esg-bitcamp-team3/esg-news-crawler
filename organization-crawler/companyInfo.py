from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# ✅ 기업 상세정보 파싱 함수 (XPath 없이 유연하게)
def parse_company_info(driver, company_name):
    info = {"기업명": company_name}
    target_fields = ["산업", "사원수", "기업구분", "설립일", "자본금", "매출액", "대표자",
                     "대졸초임", "주요사업", "4대보험", "주소", "홈페이지", "계열사"]

    try:
        table = driver.find_element(By.CSS_SELECTOR, "div.company-infomation-container table.table-basic-infomation-primary")
        rows = table.find_elements(By.TAG_NAME, "tr")
    except:
        print(f"[경고] {company_name}: 기업 정보 테이블을 찾을 수 없음")
        for field in target_fields:
            info[field] = "N/A"
        return info

    for row in rows:
        try:
            ths = row.find_elements(By.TAG_NAME, "th")
            tds = row.find_elements(By.TAG_NAME, "td")
            for th, td in zip(ths, tds):
                label = th.text.strip().replace(" ", "").replace("\n", "")
                value = td.text.strip().replace("\n", " ").replace("  ", " ")
                if label in target_fields:
                    info[label] = value
        except:
            continue

    for field in target_fields:
        if field not in info:
            info[field] = "N/A"

    return info

# ✅ 각 회사 이름으로 검색 및 상세정보 크롤링
def get_company_info(company_name):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 3)
    driver.get("https://www.jobkorea.co.kr")

    try:
        search_input = driver.find_element(By.ID, "stext")
        search_input.send_keys(company_name)

        search_button = driver.find_element(By.ID, "common_search_btn")
        search_button.click()

        corp_tab_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-target="corp"]')))
        corp_tab_button.click()
        time.sleep(1)

        first_result = driver.find_element(By.XPATH, '//*[@id="dev-content-wrap"]/article/section[2]/article[2]/article[1]/div[1]/a')
        first_result.click()
        time.sleep(1)

        driver.switch_to.window(driver.window_handles[-1])

        info = parse_company_info(driver, company_name)
        return info

    except Exception as e:
        print(f"[오류] {company_name}: {e}")
        return None

    finally:
        driver.quit()

# ✅ CSV에서 기업명 불러오기
df = pd.read_csv("../data/companyNameTest1.csv")
print("CSV에서 불러온 컬럼:", df.columns)

company_names = df["기업명"].dropna().unique().tolist()

# ✅ 크롤링 결과 저장
results = []
for name in company_names:
    info = get_company_info(name)
    if info:
        results.append(info)

# ✅ CSV 저장
result_df = pd.DataFrame(results)
result_df.to_csv("companyInfo.csv", index=False, encoding='utf-8-sig')
print("✅ 크롤링 완료! companyInfo.csv 저장됨.")
