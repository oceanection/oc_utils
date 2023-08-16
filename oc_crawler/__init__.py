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
    """指定のフォルダにJPG, PNGファイルをダウンロードする。
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
                # JPG, PNGファイルでないときはダウンロードされない
                print("Download error: No jpg or png file.")
                print(f'  URL: {url}')
                return -1

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
            print(f'  URL: {url}')
            return -1

def download_raw_data(url):
    """<img>タグのsrc属性にクエリパラメータが含まれるURLの場合, RequestsライブラリでHEADERをセットしたSessionではデータをちゃんと受けとれない？ので、
    Sessionを外してデータを受け取る.
    クエリを含むURLがdownloaded_urls, scraped_urlsに含まれるときはダウンロードしない。
    また、external_urlsに含まれる時も同じくダウンロードされない.
    
    
    Args:
        url (str): 
    Returns:
        url, content (str, Requests.response) | (url, None):
    """
    if (url not in scraped_urls) and (url not in downloaded_urls) and (url not in external_urls):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return r.content
            else:
                return
        except Exception as e:
            print(e)
            return
    else:
        return

def is_jpg_url(img_url):
    '''jpgの絶対パスかどうかを判定する
    Args:
        img_url (str):
    Returns:
        bool
    '''
    try:
        if bool(re.match(r'^http.*\.jpg$', img_url)):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def is_png_url(img_url):
    '''pngの絶対パスかどうかを判定する
    Args:
        img_url (str):
    Returns:
        bool
    '''
    try:
        if bool(re.match(r'^http.*\.png$', img_url)):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def url_analysis(img_url, url):
    """相対パスの分析. <img>タグのsrc属性には、絶対パスもあれば相対パスもあるので、
    相対パスの場合に元のURLと繋げる処理をする 
    
    Args:
        img_url (str):
        url (str): 
    Return:
        img_url (str | None)
    """
    origin = urlparse(url)
    _ =  urlparse(img_url)
    
    # URLにクエリが含まれるケース
    if _.query != '':
        if _.scheme != '' and _.netloc != '' and _.path != '':
            return img_url
        elif _.netloc != '' and _.path != '':
            return f'{origin.scheme}://{_.netloc}{_.path}?{_.query}'
        elif _.path != '':
            return f'{origin.scheme}://{origin.netloc}{_.path}?{_.query}'
        elif _.netloc != '':
            return f'{origin.scheme}://{_.netloc}/?{_.query}'
        else:
            return f'{origin.scheme}://{origin.netloc}{origin.path}?{_.query}'
    
    # クエリが含まれないケース
    else:
        if _.scheme != '' and _.netloc != '' and _.path != '':
            return f'{_.scheme}://{_.netloc}{_.path}'
        elif  _.netloc != '' and _.path != '':
            return f'{origin.scheme}://{_.netloc}{_.path}'
        elif _.path != '':
            return f'{origin.scheme}://{origin.netloc}{_.path}'
        elif _.scheme != '' and _.netloc != '':
            return f'{_.scheme}://{_.netloc}'
        elif _.netloc != '':
            return f'{origin.scheme}://{_.netloc}'
        else:
            print(f'ERROR: img_urlが正しく分析できない. {img_url}')
            return None

def url_analysis_with_extention(img_url, url):
    original = urlparse(url)
    _ = urlparse(img_url)    

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
        print(f"ERROR: BeautifulSoup object is None. at {url}")
        return
    
    else:
        for img_tag in bs.find_all('img'):
            img_url = img_tag.get('src')
            
            data = None
            
            # 拡張子がjpg, pngのURLのときはdownload関数を呼び出す。
            if is_jpg_url(img_url) or is_png_url(img_url):
                download(img_url, data, save_path, resize, min_size)

            # <img>タグのsrc属性にクエリパラメータが含まれる場合、url_analysis関数を呼び出して、元のURLと繋げる処理をする.
            img_url = url_analysis(img_url, url)
            
            # url_analysis関数でもimg_urlが正しく取得できていないので終了する.
            if img_url is None:
                print(f'ERROR: img_url is incorrect at {url}')
                return
            else:
                # <img>タグのsrc属性にクエリパラメータが含まれるので、download_raw_data関数を呼び出して、コンテンツデータを取得しておいて、download関数へ渡す.
                data = download_raw_data(img_url)
                if data is not None:
                   download(img_url, data, save_path, resize, min_size)
                else:
                    return


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

def dump(urls:list, output_path):
    urls_np = np.array(urls)
    np.savetxt(f'{output_path}/downloaded.txt', urls_np, fmt='%s')

def load(dump_path:str):
    urls_np = np.loadtxt(dump_path, dtype='str')
    return urls_np.tolist()

def crawl(url:str, save_path:str, limit_jpg_files=5000, resize=300, min_size=(151,151), epoch=1000000, output=True, output_path=''):
    """同じドメイン内をスクレイピングし、JPG,PNGファイルをダウンロードする。
    スクレイピング先のURL,保存先は必ず指定する必要がある。
    ページをクロールするごとに実行フォルダに「downloaded.txt」が保存される。成否を問わず、ダウンロードを試みたURLが出力される。
    何らかの原因で、実行中にエラーが発生して止まってしまった場合において、再度、実行したときは、「downloaded.txt」が読み込まれて、記載されたURLにはアクセスしない。
    リサイズの要否などを再度設定して再実行するときは、「download.txt」は削除すること
    
    Args:
        url (str): スプレイピング先のURLパス
        save_path (str): 保存先パス. 画像を保存する場合は下位のフォルダに「raw_data」というフォルダが作成されて、上限数まで保存される。
        limit_jpg_files (int): 1フォルダあたりのJPGファイル上限数. 初期値5000
        resize (int): 画像のリサイズ指定. 初期値300.リサイズしたくないときは0を渡す.
        min_size (tuple(int, int)): ダウンロードする画像の大きさ制限. 初期値151.
        epoch (int): クロールするWebページ数.初期値1000000.
        output (bool): ダウンロードのためアクセスしたURLを出力するかどうか。初期値はFalse
        output_path (str): downloaded.txtの出力先。指定しない場合は、save_pathに格納される
    """
    
    if os.path.exists(f'{save_path}/downloaded.txt'):
        global downloaded_urls
        downloaded_urls = load(f'{save_path}/downloaded.txt')

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
        if output:
            if output_path != '':
                dump(downloaded_urls, output_path)
            else:
                dump(downloaded_urls, save_path)
        
        # ページ内のURLの取得, internal_urlsに追加
        get_urls(bs, url)
        
        # スクレイピング回数の更新
        num_epochs += 1