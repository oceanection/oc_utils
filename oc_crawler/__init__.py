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

def img_resize(img, size=300):
    w_ratio = size / img.width
    h_ratio = size / img.height

    if w_ratio < h_ratio:
        resize_size = (size, round(img.height * w_ratio))
    else:
        resize_size = (round(img.width * h_ratio), size)

    img_r = img.resize(resize_size)
    return img_r

def download(url, save_path, resize, min_width, min_height):
    """指定のフォルダにダウンロードする。
    Args:
        url (str): ダウンロードURL
        save_path (str): 保存先パス
        resize (int): 画像のリサイズ指定
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
                    if resize != 0:
                        img_r = resize(img, resize)
                        filename = url.split('/')[-1]
                        img_r.save(os.path.join(save_path, filename))
                        print(' Download: {}'.format(filename))
                        return 1    
                    else:
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

def get_img(bs, save_path, resize, min_width, min_height):
    """ページ内に<img>タグの"src"属性の値を返す.
    jpgファイルがあるときはダウンロードする.
    
    Args:
        bs (BeautifuleSoup): BeautifulSoupオブジェクト
        save_path (str):保存先パス
        resize (int): 画像のリサイズ指定
        min_width (int): 画像の最低幅
        min_height (int): 画像の最低高さ
    Returns:
        srcs(List['str',])
    """
    if bs is not None:
        for img in bs.find_all('img', src=re.compile(f'^(http|https).*\.jpg$')):
            img_url = img.attrs['src']
            if  img_url is not None:
                download(img_url, save_path, resize, min_width, min_height)
    else:
        return

def dump(urls):
    urls_np = np.array(urls)
    np.savetxt('downloaded.txt', urls_np, fmt='%s')

def load(dump_path):
    urls_np = np.loadtxt(dump_path, dtype='str')
    return urls_np.tolist()

def crawl(url, save_path, dump_downloaded_path=None, resize=300, min_width=30, min_height=30):
    """
    Args:
        url (str): URLパス
        save_path (str): 保存先パス
        dump_downloaded_path (str): ダウンロード済URLのtxtファイル
        resize (int): 画像のリサイズ指定. 初期値300.リサイズしないときは0を渡す.
        min_width (int): 画像の最低幅. 初期値30.
        min_height (int): 画像の最低高さ. 初期値30.
    """
    r = urlparse(url)
    base_url = f'{r[0]}://{r[1]}'
    
    if dump_downloaded_path:
        global downloaded_urls 
        downloaded_urls = load(dump_downloaded_path)
    
    # 最初のページをスクレイピング
    bs = get_bs(url)
    get_urls(bs, base_url)

    while len(internal_urls) != 0:
        time.sleep(1)
        
        url = internal_urls.pop(0)
        bs = get_bs(url)
        if bs is not None:
            get_img(bs, save_path, resize, min_width, min_height)
            get_urls(bs, base_url)
            
            if len(scraped_urls) % 10 == 0:
                dump(downloaded_urls)
