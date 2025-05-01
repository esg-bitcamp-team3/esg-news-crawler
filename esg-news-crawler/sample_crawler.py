import requests
from bs4 import BeautifulSoup
import pandas as pd

data = []

url = "https://www.yna.co.kr/search/index?query=%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90"  # 뉴스 페이지 URL로 바꾸기
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

for article in soup.select('.article-item'):  # 사이트에 맞게 selector 수정
    company = "삼성전자"
    year = 2023
    title = article.select_one('h2').text.strip()
    link = article.select_one('a')['href']

    detail = requests.get(link)
    detail_soup = BeautifulSoup(detail.text, 'html.parser')
    content = detail_soup.select_one('.article-body').text.strip()

    data.append([company, year, title, content])

df = pd.DataFrame(data, columns=['회사명', '년도', 'title', 'contents'])
df.to_csv('news_articles.csv', index=False, encoding='utf-8-sig')
