import re
import time
import urllib.parse
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

ch_opt = Options()
#ch_opt.add_argument('--headless')
ch_opt.add_argument('--no-sandbox')
ch_opt.add_argument('start-maximized')
ch_opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
dr = webdriver.Chrome('chromedriver', options=ch_opt)


def build_custom_link(match):
    url = 'https://5e.tools'
    
    type_dict = {
        'dmg': 'book',
        'phb': 'book',
        'cos': 'adventure',
    }

    manual_subs = {
        'OptionalRuleShadowfellDespair': 'Despair'
    }

    group1 = match.group(1)
    group2_ = match.group(2).replace('-', ' ')

    if group2_ in manual_subs:
        group2_ = manual_subs[group2_]

    group2 = ''
    for word in camel_case_split(group2_):
        word = word + ' '
        group2 += word
    group2 = group2.strip()
    group2_encoded = urllib.parse.quote(group2).lower()
    print(group2)
    href = ''
    
    re1 = f'{url}/book.html#{group1},-1,{group2_encoded},0\\'
    re2 = f'{url}/adventure.html#{group1},-1,{group2_encoded},0\\'

    sub_dict = {
        'book': re1,
        'adventure': re2
    }

    if group1 in type_dict:
        r = sub_dict[type_dict[group1]]
        print(r)
        return r
    else:
        href = get_item(query=group2, category=group1)
        time.sleep(5)
        r2 = f'{url}/{href}\\'
        print(r2)
        return r2


def process_text(document):
    # Replace all occurrences of D&amp;D Beyond with ""
    document = document.replace('D&amp;D Beyond: ', '')
        
    regex_pattern1 = r'https://www.dndbeyond.com/sources\/([^/]+)\/[^/#]+.*?(\w+)\\'
    regex_pattern2 = r'https://www.dndbeyond.com/(\w+)\/([\w-]+)\\'
    
    processed_text = re.sub(regex_pattern1, build_custom_link, document)
    processed_text = re.sub(regex_pattern2, build_custom_link, processed_text)
    return processed_text


def get_item(query, category):
    url = 'https://5etools-mirror-1.github.io' + '/search.html?'
    query = urllib.parse.quote(query)
    dr.get(url + query)
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'omni__lnk-name'))
        WebDriverWait(dr, 5).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load", ' QUERY: ', query)
    bs = BeautifulSoup(dr.page_source, 'html.parser')
    for a in bs.find_all('a', class_='omni__lnk-name'):
        if category == 'basic-rules':
            return a['href']
        for word in a.next.__str__().lower().split(':'):
            if similar(category, word) > 0.85:
                print("href: ", a['href'])
                return a['href']
            else:
                print(a.next.__str__().lower(), " \"Not found \"", word, " in ", category)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def camel_case_split(_str):
    return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', _str)


def main():
    # Load the text document
    with open('data/journal.db', 'r') as file:
        document = file.read()

    # Process the document with the regex replacement
    processed_document = process_text(document)

    # Save the processed document
    with open('data/journal_new.db', 'w') as file:
        file.write(processed_document)


if __name__ == "__main__":
    main()
