import requests
from bs4 import BeautifulSoup
import numpy as np

import typing
import uuid

from PIL import Image
from chardet import detect

from io import BytesIO
import os
import re
from urllib.parse import urlparse, urljoin
import time
from glob import glob

import zipfile
import shutil


CHECK = 'Git success. created by oceanection.'

session = requests.Session()

scraped_urls = []
downloaded_urls = []
internal_urls = []
external_urls = []

download_count = 0

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                        }

def add_scraped_urls(url:str):
    if url not in scraped_urls:
        scraped_urls.append(url)

def add_downloaded_urls(url:str):
    if url not in downloaded_urls:
        downloaded_urls.append(url)

def add_internal_urls(url:str):
    if url not in internal_urls:
        internal_urls.append(url)

def add_external_urls(url:str):
    if url not in external_urls:
        external_urls.append(url)

def summary():
    global download_count
    print("\n===========================================================================")
    print(f'Internal URLs: {len(internal_urls)}, Scraped URLs: {len(scraped_urls)}')
    print('\n')
    print(f'Downloaded URLs {len(downloaded_urls)},  Downloaded {download_count}')
    print(f'External URLs: {len(external_urls)}')
    print('===========================================================================')
    time.sleep(1)

def init_directory(save_path:str):
    """ダウンロード先のフォルダにraw_data_1フォルダを作成する。
    raw_data_?がすでに作成されているときは、数字が最後のフォルダパスを返す。
    
    Args:
        save_path (str): ダウンロード指定フォルダ
    Returns:
        save_detail_path (str): ダウンロード指定フォルダ内のうち, JPGファイルをダウンロードするフォルダパス
    """
    dirs = glob(f'{save_path}/raw_data_*')
    dirs = sorted(dirs)
    if len(dirs) == 0:
        os.makedirs(os.path.join(save_path, 'raw_data_1'))
        save_detail_path = os.path.join(save_path, 'raw_data_1')
        return save_detail_path
    else:
        save_detail_path = dirs[-1]
        return save_detail_path

def chane_directory(save_detail_path:str, save_path:str, limit_jpg_files:int):
    """1フォルダあたりのダウンロード数が指定の数を超えた場合、ダウンロードフォルダを切り替える。
    Args:
        save_detail_path (str): ダウンロード指定フォルダのうち,JPGファイルをダウンロードするフォルダパス
        save_path (str): ダウンロード先
        limit_jpg_files (int): 1フォルダあたりのJPGファイル上限数
    Returns:
        save_detail_path (str): ダウンロード指定フォルダå
    """
    # 直近のダウンロードフォルダ内のファイル数
    count_jpg_files = len(glob(f'{save_detail_path}/*jpg'))   
        
    if count_jpg_files > limit_jpg_files:
        # ダウンロードフォルダの数
        save_detail_dirs = glob(f'{save_path}/raw_data_*')
        dirs_count = len(save_detail_dirs)
        
        # 新しいダウンロードフォルダの作成
        os.mkdir(f'{save_path}/raw_data_{dirs_count+1}')
        save_detail_path = f'{save_path}/raw_data_{dirs_count+1}'
        return save_detail_path    
    else:
        return save_detail_path

def get_bs(url:str):
    """Beautifulsoupオブジェクトとurlを返す
    Args:
        url (str): 
    Returns:
        bs, url (BeautifulSoup, str): 
    """
    add_scraped_urls(url)
    print(f'Scraping... {url}')
        
    try:
        res = session.get(url, headers=HEADERS, allow_redirects=True)
        enc = detect(res.content)
        if enc['encoding'] is None:
            bs = BeautifulSoup(res.content, 'html.parser')
            return (bs, url)
        else:
            bs = BeautifulSoup(res.content, 'html.parser', from_encoding=enc['encoding'])
            return (bs, url)
    except Exception as e:
        print(f'Error: {e}')
        return (None, None)

def is_png(b: bytes) -> bool:
    """バイナリの先頭部分からPNGファイルかどうかを判定する。"""
    return bool(re.match(b"^\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", b[:8]))

def is_jpg(b: bytes) -> bool:
    """バイナリの先頭部分からJPEGファイルかどうかを判定する。"""
    return bool(re.match(b"^\xff\xd8", b[:2]))

def img_resize(img, size:int):
    """画像のリサイズ
    Args:
        img: Pillow
        size (int): 拡大縮小サイズの指定.
    """
    w_ratio = size / img.width
    h_ratio = size / img.height

    if w_ratio < h_ratio:
        resize_size = (size, round(img.height * w_ratio))
    else:
        resize_size = (round(img.width * h_ratio), size)

    img_r = img.resize(resize_size)
    return img_r

def download(url:str, data:bytes, save_detail_path:str, resize:int, min_size:tuple):
    """指定のフォルダにダウンロードする。
    Args:
        url (str): ダウンロードURL
        data (bytes):バイナリデータ
        save_path (str): 保存先パス
        resize (int): 画像のリサイズ指定
        min_size (tuple(int, int)):
    Returns:
        1 | -1
    """
    global download_count   
    if url not in downloaded_urls:
        try:
            add_downloaded_urls(url)
            
            if data is None:          
                req = session.get(url, headers=HEADERS)
                if req.status_code == 200:
                    data = req.content
            
            ext = ''
            if is_jpg(data):
                ext = 'jpg'
            elif is_png(data):
                ext = 'png'
            else:
                ext = 'jpg'      

            filename = f'{uuid.uuid4()}.{ext}'

            img = Image.open(BytesIO(data))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            x, y = img.size
            x_min, y_min = min_size
            if (x >= x_min and y >= y_min):
                if resize > 1:
                    img_r = img_resize(img, resize)
                    img_r.save(os.path.join(save_detail_path, filename))
                    print('  Download: {}'.format(filename))
                    download_count += 1
                    return 1    
                else:
                    img.save(os.path.join(save_detail_path, filename))
                    print(' Download: {}'.format(filename))
                    download_count += 1
                    return 1                 
        except Exception as e:
            print(f' Download Error: {e}')
            print(f'  Url: {url}')
            return -1

def download_raw_data(url):
    r = requests.get(url)
    if r.status_code == 200:
        return (url, r.content)
    else:
        return (url, None)

def get_img(bs:BeautifulSoup, url:str, save_path:str, resize:int, min_size:(int, int)):
    """ページ内に<img>タグの"src"属性の値を返す.
    jpgファイルがあるときはダウンロードする.
    
    Args:
        bs (BeautifulSoup): BeautifulSoupオブジェクト
        url (str): URL 
        save_path (str):保存先パス
        resize (int): 画像のリサイズ指定
        min_size (tuple(int, int)): 画像の大きさ指定
    Returns:
    """
    if bs is None:
        print("ERROR: BeautifulSoup object is None.")
        return
    
    else:
        for img_tag in bs.find_all('img'):
            img_url = img_tag.get('src')
            
            data = None
            p = urlparse(img_url)
            if p.query != '':
                if p.scheme != '':
                    img_url, data, = download_raw_data(img_url)
                elif p.scheme == '' and p.netloc == '':
                    _ = urlparse(url)
                    img_url, data = download_raw_data(f'{_.scheme}://{_.netloc}{p.path}{p.query}')
                elif p.scheme == '':
                    _ = urlparse(url)
                    img_url, data = download_raw_data(f'{_.scheme}://{p.netloc}{p.path}{p.query}')
            
            download(img_url, data, save_path, resize, min_size)

def get_urls(bs:BeautifulSoup, url:str):
    """ページ内のhref属性のURLを返す
    Args:
        bs (BeautifulSoup): BeautifulSoupオブジェクト
        url (str): netloc 
    Returns:
        Pages(List['str',]) | []
    """
    if bs is None:
        print("ERROR: BeautifulSoup object is None.")
        return
    
    for a_tag in bs.find_all('a'):
        try:
            if a_tag.attrs['href'] is not None:
                a_tag_url = urljoin(url, a_tag.get("href"))
                
                r = urlparse(url)
                # 同じドメイン内のURLかの判定
                if a_tag_url.find(r.netloc) != -1 and re.search(r'^http.*', a_tag_url):
                    #スクレイピング済でないかの判定 
                    if a_tag_url not in scraped_urls:
                        add_internal_urls(a_tag_url)
                else:
                    if re.search(r'^http.*', a_tag_url):
                        add_external_urls(a_tag_url) 
        except Exception as e:
            pass 

    summary()
    return (internal_urls, external_urls)

def dump(urls:list):
    urls_np = np.array(urls)
    np.savetxt('downloaded.txt', urls_np, fmt='%s')

def load(dump_path:str):
    urls_np = np.loadtxt(dump_path, dtype='str')
    return urls_np.tolist()

def crawl(url:str, save_path:str, limit_jpg_files=5000, resize=300, min_size=(50,50), epoch=1000000):
    """JPGファイルをダウンロードするMain関数
    Args:
        url (str): スプレイピング先のURLパス
        save_path (str): 保存先パス
        limit_jpg_files (int): 1フォルダあたりのJPGファイル上限数. 初期値5000
        resize (int): 画像のリサイズ指定. 初期値300.リサイズしないときは0を渡す.
        min_size (tuple(int, int)): ダウンロードする画像の大きさ制限. 初期値50.
        epoch (int): クロールするWebページ数.初期値1000000.
    """
    
    if os.path.exists(os.path.join(os.getcwd(),'downloaded.txt')):
        dump_path = os.path.join(os.getcwd(),'downloaded.txt')
        global downloaded_urls
        downloaded_urls = load(dump_path)

    save_detail_path = init_directory(save_path)
    
    # 最初のページをスクレイピング
    bs, url = get_bs(url)
    get_urls(bs, url)
    get_img(bs, url, save_detail_path, resize, min_size)

    num_epochs = 1
    while len(internal_urls) != 0:
        if num_epochs == epoch:
            break
        time.sleep(1)
        
        # ドメイン内のURLから1つ取り出し、Beautifulオブジェクトを取得
        url = internal_urls.pop(0)
        bs, url = get_bs(url)
        
        # フォルダの保存上限を超えた場合のフォルダの切り替え
        save_detail_path = chane_directory(save_detail_path, save_path, limit_jpg_files)
        get_img(bs, url, save_detail_path, resize, min_size)
        
        # ダウンロードを試みたURLの出力
        dump(downloaded_urls)
        
        # ページ内のURLの取得, internal_urlsに追加
        get_urls(bs, url)
        
        # スクレイピング回数の更新
        num_epochs += 1