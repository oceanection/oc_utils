from bs4 import BeautifulSoup 
import requests
from PIL import Image

from io import BytesIO
import os
import re

class Crawler:
    def __init__(self, url):
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br"}
        self.session = requests.Session()
            
    def get_bs(self):
        try:
            session = self.session
            req = session.get(self.url, headers=self.headers, allow_redirects=True)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.content, 'html.parser')
    
    def get_links(self, end=''):
        bs = self.get_bs()
        if bs is None:
            print("ERROR: bs object is None.")
            return None
        
        pages = []
        for link in bs.find_all('a', href=re.compile(f'^(http|https).*\.{end}$')):
            if link.attrs['href'] is not None:
                pages.append(link.attrs['href'])
        
        return list(set(pages))
     
    def download_images(self, download_path, urls, min_height=25, min_width=25):
        try:
            session = requests.Session()
            for url in urls:
                req = session.get(url, headers=self.headers)
                if req.content is None:
                    continue
                else:
                    img = Image.open(BytesIO(req.content))
                    x, y = img.size
                    if (x >= min_height and y >= min_width):
                        filename = url.split('/')[-1]
                        img.save(os.path.join(download_path, filename))
                        print('Download: {}'.format(filename))    
                
        except requests.exceptions.RequestException:
            return None
     

        