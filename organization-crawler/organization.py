from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def get_company_info(company_name):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 1)
    driver.get("https://www.jobkorea.co.kr")  # 기업 검색 페이지 직접 접근
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    try:
        # ✅ 검색어 입력
        search_input = driver.find_element(By.ID, "stext")
        search_input.send_keys(company_name)

        # ✅ 검색 버튼 클릭
        search_button = driver.find_element(By.ID, "common_search_btn")
        search_button.click()
        corp_tab_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-target="corp"]')))
        corp_tab_button.click()
        time.sleep(3)

        # # ✅ 첫 번째 검색 결과 클릭\
        first_result = driver.find_element(By.XPATH, '//*[@id="dev-content-wrap"]/article/section[2]/article[2]/article[1]/div[1]/a')
        first_result.click()
        time.sleep(3)

        # 새 탭으로 이동 (기업 상세 페이지가 새 창으로 열릴 수 있음)
        driver.switch_to.window(driver.window_handles[-1])

        # 기업 정보 수집
        # 없을 떄 에러처리
        def safe_xpath(driver, xpath, label):
            try:
                return driver.find_element(By.XPATH, xpath).text
            except:
                print(f"[경고] '{label}' 항목 없음")
                return "N/A"

        #왼쪽 열
        info ={}

        info['기업명'] = company_name
        info['산업'] = safe_xpath(driver,
                                         '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[1]/td[1]/div/div','산업')
        info['기업구분'] = safe_xpath(driver,
                                           '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[2]/td[1]/div/div','기업구분')
        info['자본금'] = safe_xpath(driver,
                                          '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[3]/td[1]/div/div','자본금')
        info['대표자'] = safe_xpath(driver,
                                          '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[4]/td[1]/div/div','대표자')
        info['주요사업'] = safe_xpath(driver,
                                           '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[5]/td[1]/div/div','주요사업')
        info['홈페이지'] = safe_xpath(driver,
                                           '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[6]/td[1]/div/div','홈페이지')
        info['계열사'] = safe_xpath(driver,
                                          '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[7]/td[1]/div/div','계열사')

        # 오른쪽 열
        info['사원수'] = safe_xpath(driver,
                                          '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[1]/td[2]/div/div','사원수')
        info['설립일'] = safe_xpath(driver,
                                          '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[2]/td[2]/div/div','설립일')
        info['매출액'] = safe_xpath(driver,
                                          '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[3]/td[2]/div/div','매출액')
        info['대졸초임'] = safe_xpath(driver,
                                           '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[4]/td[2]/div/div','대졸초임')
        info['4대보험'] = safe_xpath(driver,
                                           '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[5]/td[2]/div/div','4대보험')
        info['주소'] = safe_xpath(driver,
                                         '//*[@id="company-body"]/div[1]/div[1]/div/table/tbody/tr[6]/td[2]/div/div','주소')
        info['영업이익'] = safe_xpath(driver,
                                '//*[@id="company-body"]/div[1]/div[2]/div/div/div[3]/div[2]/div[1]/div[2]/', '영업이익')
        info['당기순이익'] = safe_xpath(driver,
                                  '//*[@id="company-body"]/div[1]/div[2]/div/div/div[4]/div[2]/div[1]/div[2]', '당기순이익')



        return info

    except Exception as e:
        print(f"[오류] {company_name}: {e}")
        return None

    finally:
        driver.quit()

# ✅ CSV 파일에서 기업명 리스트 불러오기
df = pd.read_csv("../data/companyNameTest1.csv")  # 상대경로
print("CSV에서 불러온 컬럼:", df.columns)  # 실제 컬럼명 확인

company_names = df["기업명"].dropna().unique().tolist()

# ✅ 크롤링 결과 저장 리스트
results = []
for name in company_names:
    info = get_company_info(name)
    if info:
        results.append(info)

# ✅ 결과를 CSV로 저장
result_df = pd.DataFrame(results)
result_df.to_csv("기업정보_크롤링결과.csv", index=False, encoding='utf-8-sig')  # Excel에서 한글 깨짐 방지
