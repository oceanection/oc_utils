from crawler import Crawler
import os

def main():
    test_url = 'http://blog.livedoor.jp/ele01/archives/17198881.html'
    download_path = os.path.join(os.getenv('HOME'), 'Pictures', 'raw_data')
    print(download_path)
    crawler = Crawler(test_url)
    links = crawler.get_links(end='jpg')
    
def scrape():
    pass

def insert():
    pass

def dump():
    pass

def init_db():
    pass

if __name__ == "__main__":
    main()