import requests
from bs4 import BeautifulSoup
import numpy as np

from PIL import Image
import face_recognition
from chardet import detect

from io import BytesIO
import os
import re
from urllib.parse import urlparse
import time

# スクレイピング対象のURL
url = 'https://mabui-onna.com/blog-entry-9.html'

# 保存先
save_path = '/Users/yousukeyamamoto/Pictures/raw_data'
dump_path = '/Users/yousukeyamamoto/Pictures'

# 保存する最低サイズ
min_width = 25
min_height = 25

r = urlparse(url)
base_url = f'{r[0]}://{r[1]}'

session = requests.Session()

scraped_urls = []
downloaded_urls = []
jpeg_urls = []
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

def add_jpeg_urls(url):
    if url not in jpeg_urls:
        jpeg_urls.append(url)

def add_internal_urls(url):
    if url not in internal_urls:
        internal_urls.append(url)

def add_external_urls(url):
    if url not in external_urls:
        external_urls.append(url)

def summary():
    print(f'Internal URLs: {len(internal_urls)}')
    print(f'External URLs: {len(external_urls)}')
    print(f'Jpeg URLs: {len(jpeg_urls)}')
    print(f'Downloaded URLs {len(downloaded_urls)}')
    print(f'Scraped URLs: {len(scraped_urls)}')

def dump():
    d = np.array(internal_urls).reshape((-1, 1))
    np.savetxt(os.path.join(dump_path, 'internal_urls.csv'), d)


def download(url):
    """指定のフォルダにダウンロードする。
    Args:
        url (str):
    Returns:
        1 | -1
    """
    if url not in downloaded_urls:
        try:
            add_downloaded_urls(url)
            
            req = session.get(url, headers=HEADERS)
            if req.content is None:
                return -1
            r = is_person(BytesIO(req.content))
            
            if r:
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

def is_person(data):
    """人の顔かどうかを判定する
    Args:
        data:
    Returns:
        bool:
    """
    image = face_recognition.load_image_file(data)
    face_locations = face_recognition.face_locations(image)    
    if len(face_locations) != 0:
        return True
    else:
        return False

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

def is_internal_url(url):
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

def get_urls(bs):
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
            if is_internal_url(url) and url not in scraped_urls:
                add_internal_urls(url)
            
            else:
                add_external_urls(url)

    summary()

def get_img(bs):
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
                download(img_url)
    else:
        return

# 最初のページをスクレイピング
bs = get_bs(url)
get_urls(bs)

dump()

try:
    while len(internal_urls) != 0:
        time.sleep(1)
        
        url = internal_urls.pop(0)
        bs = get_bs(url)
        if bs is not None:
            get_img(bs)
            get_urls(bs)
            
            
except KeyboardInterrupt:
    print(f'End scraping. Downloaded {len(downloaded_urls)}. Scraped {scraped_urls} site.')