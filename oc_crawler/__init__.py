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
from glob import glob


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
                        "Accept-Encoding": "gzip, deflate, br"}

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
    print("\n=========================================================================")
    print(f'Internal URLs: {len(internal_urls)}, Scraped URLs: {len(scraped_urls)}')
    print('\n')
    print(f'Downloaded URLs {len(downloaded_urls)}')
    print(f'External URLs: {len(external_urls)}')
    print('===========================================================================')
    time.sleep(1)

def get_bs(url:str):
    add_scraped_urls(url)
    print(f'Scraping... {url}')
        
    try:
        req = session.get(url, headers=HEADERS, allow_redirects=True)
        enc = detect(req.content)
        if enc['encoding'] is None:
            return BeautifulSoup(req.content, 'html.parser')
        else:
            return BeautifulSoup(req.content, 'html.parser', from_encoding=enc['encoding'])
    except Exception as e:
        print(f'Error: {e}')
        return None

def is_internal_url(url:str, base_url:str):
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

def is_jpg(url:str):
    if url.find('.jpg') != -1:
        return True
    else:
        return False

def get_urls(bs:BeautifulSoup, base_url:str):
    """ページ内のhref属性のURLを返す
    Args:
        bs (BeautifulSoup): BeautifulSoupオブジェクト
        base_url (str): netloc 
    Returns:
        Pages(List['str',]) | []
    """
    if bs is None:
        print("ERROR: BeautifulSoup object is None.")
        return
    
    # 絶対パスが指定されている場合
    for link in bs.find_all('a', href=re.compile(f'^(http|https).*$')):
        if link.attrs['href'] is not None:
            url = link.attrs['href']
            #内部ページかつスクレイピング済でないかの判定    
            if (is_internal_url(url, base_url)) and (url not in scraped_urls):
                add_internal_urls(url)
            else:
                if url not in external_urls:
                    add_external_urls(url)    
    summary()

def img_resize(img, size:int):
    """画像のリサイズ
    Args:
        img (PIL.JpegImagePlugin.JpegImageFile): Pillow
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

def download(url:str, save_detail_path:str, resize:int, min_size:tuple):
    """指定のフォルダにダウンロードする。
    Args:
        url (str): ダウンロードURL
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
            
            req = session.get(url, headers=HEADERS)
            if req.content is not None:
                img = Image.open(BytesIO(req.content))
                x, y = img.size
                x_min, y_min = min_size
                if (x >= x_min and y >= y_min):
                    if resize > 1:
                        img_r = img_resize(img, resize)
                        filename = url.split('/')[-1]
                        img_r.save(os.path.join(save_detail_path, filename))
                        print('  Download: {}'.format(filename))
                        download_count += 1
                        return 1    
                    else:
                        filename = url.split('/')[-1]
                        img.save(os.path.join(save_detail_path, filename))
                        print(' Download: {}'.format(filename))
                        download_count += 1
                        return 1
            else:
                return -1
        except Exception as e:
            print(f' Download Error: {e}')
            print(f'  Url: {url}')
            return -1

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
        
    

def get_img(bs:BeautifulSoup, save_path:str, resize:int, min_size:(int, int)):
    """ページ内に<img>タグの"src"属性の値を返す.
    jpgファイルがあるときはダウンロードする.
    
    Args:
        bs (BeautifulSoup): BeautifulSoupオブジェクト
        save_path (str):保存先パス
        resize (int): 画像のリサイズ指定
        min_size (tuple(int, int)): 画像の大きさ指定
    Returns:
        srcs(List['str',])
    """
    if bs is not None:
        for img in bs.find_all('img', src=re.compile(f'^(http|https).*\.jpg$')):
            img_url = img.attrs['src']
            if  img_url is not None:
                download(img_url, save_path, resize, min_size)
    else:
        return

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
    r = urlparse(url)
    base_url = f'{r[0]}://{r[1]}'
    
    if os.path.exists(os.path.join(os.getcwd(),'downloaded.txt')):
        dump_path = os.path.join(os.getcwd(),'downloaded.txt')
        global downloaded_urls
        downloaded_urls = load(dump_path)

    save_detail_path = init_directory(save_path)
    
    # 最初のページをスクレイピング
    bs = get_bs(url)
    get_urls(bs, base_url)
    get_img(bs, save_detail_path, resize, min_size)

    num_epochs = 0
    while len(internal_urls) != 0:
        if num_epochs == epoch:
            break
        
        time.sleep(1)
        
        url = internal_urls.pop(0)
        bs = get_bs(url)
        if bs is not None:
            save_detail_path = chane_directory(save_detail_path, save_path, limit_jpg_files)
            get_img(bs, save_detail_path, resize, min_size)
            dump(downloaded_urls)
            get_urls(bs, base_url)
        
        num_epochs += 1 