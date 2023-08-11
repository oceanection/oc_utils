from bs4 import BeautifulSoup 
import requests
from PIL import Image
import face_recognition
from chardet import detect

from io import BytesIO
import os
import re
from urllib.parse import urlparse

def _base_url(url):
    r = urlparse(url)
    return f'{r[0]}://{r[1]}'

class Crawler:
    def __init__(self, url):
        self.url = url
        self.base_url = _base_url(url)
        self.internal_urls = []
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br"}
        self.session = requests.Session()
            
    def get_bs(self):
        try:
            session = self.session
            req = session.get(self.url, headers=self.headers, allow_redirects=True)
            enc = detect(req.content)
            if enc['encoding'] is None:
                return BeautifulSoup(req.content, 'html.parser', from_encoding='utf-8')
            else:
                return BeautifulSoup(req.content, 'html.parser', from_encoding=enc['encoding'])
        except requests.exceptions.RequestException:
            return None
        
    def get_links(self):
        """ページ内のURLを返す
        Args:
            No args.
        Returns:
            Pages(List['str',]) | []
        """
        bs = self.get_bs()
        if bs is None:
            print("ERROR: bs object is None.")
            return None
        
        pages = []
        for link in bs.find_all('a', href=re.compile(f'^(http|https).*$')):
            if link.attrs['href'] is not None:
                pages.append(link.attrs['href'])
        return list(set(pages))
    
    def get_img(self):
        """ページ内に<img>タグの"src"属性の値を返す
        Args:
            No args.
        Returns:
            srcs(List['str',])
        """
        bs = self.get_bs()
        if bs is None:
            print("ERROR: bs object is None.")
            return None
        srcs = []
        for img in bs.find_all('img', src=re.compile(f'^(http|https).*$')):
            if img.attrs['src'] is not None:
                srcs.append(img.attrs['src'])
        return srcs

    def get_internal_urls(self, urls):
        """
        Args:
            urls (List['str',]):
        Returns:
            internal_urls (List['str',]):
        """
        internal_urls = [l for l in urls if l.find(self.base_url) != -1]
        return internal_urls

    def crawl(self):
        while True:
            pass

def _is_person(data):
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


def _save(img, url, path, x, y, min_x, min_y):
    if (x >= min_x and y >= min_y):
        filename = url.split('/')[-1]
        img.save(os.path.join(path, filename))
        print('Download: {}'.format(filename))
     
class Downloader:
    def __init__(self, urls, save_path):
        self.urls = [l for l in urls if l.find('.jpg') != -1]
        self.save_path = save_path
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br"}
        self.session = requests.Session()
    
    def download(self, min_x=25, min_y=25, person=True):
        """指定のフォルダにダウンロードする。
        Args:
            min_x (int):最小の画像の高さの指定
            min_y (int):最小の画像の幅の指定
            person (bool):顔認識で人が写っている場合にダウンロードする.初期値はTrue
        Returns:
        
        """
        for url in self.urls:
            try:
                req = self.session.get(url, headers=self.headers)
                if req.content is None:
                    continue
                elif person:
                    r = _is_person(BytesIO(req.content))
                    if r:
                        img = Image.open(BytesIO(req.content))
                        x, y = img.size
                        _save(img, url, self.save_path, x, y, min_x, min_y)
                    else:
                        continue
                else:
                    _save(img, url, self.save_path, x, y, min_x, min_y)            
                            
            except requests.exceptions.RequestException:
                continue
        