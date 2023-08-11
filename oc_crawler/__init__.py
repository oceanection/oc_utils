import requests
from bs4 import BeautifulSoup
import numpy as np

from PIL import Image
from chardet import detect

from io import BytesIO
import os
import re
from urllib.parse import urlparse
import time


CHECK = 'Git success. created by oceanection.'

session = requests.Session()

scraped_urls = []
downloaded_urls = []
internal_urls = []
external_urls = []

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br"}

def add_scraped_urls(url):
    if url not in scraped_urls:
        scraped_urls.append(url)
    
def add_downloaded_urls(url):
    if url not in downloaded_urls:
        downloaded_urls.append(url)

def add_internal_urls(url):
    if url not in internal_urls:
        internal_urls.append(url)

def add_external_urls(url):
    if url not in external_urls:
        external_urls.append(url)

def summary():
    print("\n========================================================================")
    print(f'Internal URLs: {len(internal_urls)}, Scraped URLs: {len(scraped_urls)}')
    print('\n')
    print(f'Downloaded URLs {len(downloaded_urls)}')
    print(f'External URLs: {len(external_urls)}')
    print('===========================================================================')
    time.sleep(1)

def get_bs(url):
    add_scraped_urls(url)
    print(f'Scraping... {url}')
        
    try:
        req = session.get(url, headers=HEADERS, allow_redirects=True)
        enc = detect(req.content)
        if enc['encoding'] is None:
            return BeautifulSoup(req.content, 'html.parser')
        else:
            return BeautifulSoup(req.content, 'html.parser', from_encoding=enc['encoding'])
    except requests.exceptions.RequestException:
        return None

def is_internal_url(url, base_url):
    """内部URLかどうかの判定
    Args:
        urls (List['str',]):
    Returns:
        internal_urls (List['str',]):
    """
    if url.find(base_url) != -1:
        return True
    else:
        return False

def is_jpg(url):
    if url.find('.jpg') != -1:
        return True
    else:
        return False

def get_urls(bs, base_url):
    """ページ内のhref属性のURLを返す
    Args:
        No args.
    Returns:
        Pages(List['str',]) | []
    """
    if bs is None:
        print("ERROR: bs object is None.")
        return None
    
    for link in bs.find_all('a', href=re.compile(f'^(http|https).*$')):
        if link.attrs['href'] is not None:
            url = link.attrs['href']            
            if is_internal_url(url, base_url) and url not in scraped_urls:
                add_internal_urls(url)
            else:
                if url not in external_urls:
                    add_external_urls(url)
    summary()

def download(url, save_path, min_width, min_height):
    """指定のフォルダにダウンロードする。
    Args:
        url (str): ダウンロードURL
        save_path (str): 保存先パス
        min_width (int):
        min_heigght (int):
    Returns:
        1 | -1
    """
    if url not in downloaded_urls:
        try:
            add_downloaded_urls(url)
            
            req = session.get(url, headers=HEADERS)
            if req.content is not None:
                img = Image.open(BytesIO(req.content))
                x, y = img.size
                if (x >= min_width and y >= min_height):
                    filename = url.split('/')[-1]
                    img.save(os.path.join(save_path, filename))
                    print(' Download: {}'.format(filename))
                    return 1
            else:
                return -1
        except Exception as e:
            print(f' Download Error: {e}')
            print(f'Url: {url}')
            return -1

def get_img(bs, save_path, min_width, min_height):
    """ページ内に<img>タグの"src"属性の値を返す.
    jpgファイルがあるときはダウンロードする.
    
    Args:
        bs (BeautifuleSoup):
    Returns:
        srcs(List['str',])
    """
    if bs is not None:
        for img in bs.find_all('img', src=re.compile(f'^(http|https).*\.jpg$')):
            img_url = img.attrs['src']
            if  img_url is not None:
                download(img_url, save_path, min_width, min_height)
    else:
        return


def crawl(url, save_path, min_width=25, min_height=25):
    r = urlparse(url)
    base_url = f'{r[0]}://{r[1]}'
    
    # 最初のページをスクレイピング
    bs = get_bs(url)
    get_urls(bs, base_url)

    while len(internal_urls) != 0:
        time.sleep(1)
        
        url = internal_urls.pop(0)
        bs = get_bs(url)
        if bs is not None:
            get_img(bs, save_path, min_width, min_height)
            get_urls(bs, base_url)
