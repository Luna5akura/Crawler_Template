import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logging.basicConfig(level=logging.INFO)

# region INIT

false = False
true = True
LINK = "https://zh.moegirl.org.cn/zh-hans/TAKUMI3/%E6%9B%B2%E7%9B%AE%E5%88%97%E8%A1%A8"
cookies = []

for cookie in cookies:
    cookie["sameSite"] = "None"
pattern_pos = re.compile(r"\d+,\d+")
DRIVER = None


def init():
    global DRIVER
    print("INITIALIZING")
    # 设置浏览器驱动和选项
    options = Options()
    options.headless = True  # 无界面模式
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    # options.add_argument(
    #     "Accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
    # options.add_argument("Accept-Encoding=gzip, deflate, br, zstd")
    # options.add_argument("Accept-Language=zh-CN,zh;q=0.9,en;q=0.8")
    # options.add_argument("Sec-Fetch-Dest=document")
    # options.add_argument("Sec-Fetch-User=?1")
    # options.add_argument("Sec-Fetch-Mode=navigate")
    # options.add_argument("Sec-Fetch-Site=none")
    # options.add_argument("Upgrade-Insecure-Requests=1")
    # options.add_argument('sec-ch-ua-platform="Windows"')
    # options.add_argument("sec-ch-ua-mobile=?0")
    # options.add_argument('sec-ch-ua="Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"')
    DRIVER = webdriver.Chrome(options=options)
    #
    # DRIVER.get("https://wikiwiki.jp/takumi_game")
    #
    # for cookie in cookies:
    #     print(cookie)
    #     DRIVER.add_cookie(cookie)

    DRIVER.get(LINK)
    return DRIVER


def get_soup_from_driver(driver, waited_element):
    # time.sleep(10)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, waited_element))
    )

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    print(f"{soup = }")
    return soup


def get_links_from_soup(soup, *args, **kwargs) -> list:
    links = soup.find_all(*args, **kwargs)
    hrefs = [link.get('href') for link in links if link.get('href')]
    print(f"Found links: {hrefs}")
    return hrefs


def get_tables_from_soup(soup):
    tables = []
    for table in soup.find_all('table'):
        # Get the table headers
        headers = []
        for th in table.find_all('th'):
            col_span = int(th.get('colspan', 1))
            row_span = int(th.get('rowspan', 1))
            header = th.get_text(strip=True)
            for _ in range(row_span):
                headers.append([header] * col_span)

        logging.info(f"Headers: {headers}")

        # Get the table data
        data = []
        for row in table.find_all('tr'):
            row_data = []
            for td in row.find_all(['td', 'th']):
                row_data.append(td.get_text(strip=True))
            if any(row_data):
                data.append(row_data)

        logging.info(f"Data: {data}")

        # Create a DataFrame
        header_df = pd.DataFrame(headers).fillna('')
        data_df = pd.DataFrame(data)
        df = pd.concat([header_df, data_df], ignore_index=True)

        # Set multi-level column names if headers exist
        if headers:
            df.columns = pd.MultiIndex.from_arrays(df.iloc[:len(headers)].values)
            df = df.iloc[len(headers):]

        tables.append(df)

    return tables


def save_dfs_as_csv(dfs, output_dir):
    for i, df in enumerate(dfs):
        df.to_csv(os.path.join(output_dir, f'table_{i}.csv'), index=False)


def main():
    global DRIVER
    print("MAIN")
    DRIVER = init()
    print("Cookies are set and page is refreshed.")
    soup = get_soup_from_driver(DRIVER, '.wikitable.moe-wide-table')
    tables = get_tables_from_soup(soup)
    save_dfs_as_csv(tables, '.\output')
    print(tables)
    # get_links_from_soup(soup,class_='rel-wiki-page')
    while True:
        time.sleep(10)
        # Print the status code and response data
        print("running")
        pass


if __name__ == '__main__':
    main()
