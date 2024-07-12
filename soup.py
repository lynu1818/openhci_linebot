import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
from webdriver_manager.chrome import ChromeDriverManager
import re
import model
import subprocess

# Function to install Google Chrome
def install_chrome():
    try:
        subprocess.run("apt-get update", shell=True, check=True)
        subprocess.run("apt-get install -y wget gnupg2", shell=True, check=True)
        subprocess.run("wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -", shell=True, check=True)
        subprocess.run("sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'", shell=True, check=True)
        subprocess.run("apt-get update", shell=True, check=True)
        subprocess.run("apt-get install -y google-chrome-stable", shell=True, check=True)
        print("install chrome")
    except subprocess.CalledProcessError as e:
        print(f"Error during Chrome installation: {e}")
        raise



def fetch_date_data():
    print("fetch date data")
    url = "https://ecal.click108.com.tw"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=9222")

    chromedriver_path = "./chromedriver_linux64/chromedriver"
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    page_content = driver.page_source

    driver.implicitly_wait(25)

    
    driver.quit()
    
    soup = BeautifulSoup(page_content, 'html.parser')

    # 找到農曆日期
    lunar_pattern = r"農曆：(.*?)年.*?((?:十[一二]|[一二三四五六七八九十])月[初十廿三]+[一二三四五六七八九十]*)"
    lunar_container = soup.find('div', class_='Gday_lunar').text.strip()
    lunar_match = re.search(lunar_pattern, lunar_container)
    if lunar_match:
        ganzhi = lunar_match.group(1).strip()
        lunar_date = lunar_match.group(2).strip()
        print("干支: ", ganzhi)
        print("農曆日期: ", lunar_date)
    else:
        print("未找到農曆日期")
    
    # 找到宜忌
    yi_ji = { "宜": [], "忌": [] }
    # 查找宜的元素
    yi_container = soup.find('div', id='oughtThings')
    if yi_container:
        yi_items = yi_container.find_all('li')
        for item in yi_items:
            a_tag = item.find('a')
            if a_tag:
                yi_ji["宜"].append(a_tag.text.strip())
    
    # 查找忌的元素
    ji_container = soup.find('div', id='avoidThings')
    if ji_container:
        ji_items = ji_container.find_all('li')
        for item in ji_items:
            a_tag = item.find('a')
            if a_tag:
                yi_ji["忌"].append(a_tag.text.strip())
    
    # 找到吉時、節氣、煞
    jieqi_pattern = r"所處節氣：([^\(]+)\("
    jieqi_container = soup.find('div', class_='Gday_terms').text.strip()
    jieqi_match = re.search(jieqi_pattern, jieqi_container)
    if jieqi_match:
        jieqi = jieqi_match.group(1).strip()
    else:
        print("未找到節氣")
    
    sha_container = soup.find('div', class_='Gday_icon04_cont')
    sha = sha_container.text.strip() if sha_container else ""
    good_times_container = soup.find('div', class_='Gday_icon05_cont')
    good_times = good_times_container.text.strip().split('、') if good_times_container else []

    data = {
        'lunar_date': lunar_date,
        'ganzhi': ganzhi,
        'yi': yi_ji["宜"],
        'ji': yi_ji["忌"],
        'good_times': good_times,
        'jieqi': jieqi,
        'sha': sha
    }

    model.write_date_info(data)


    



