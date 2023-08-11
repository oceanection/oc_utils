from oc_crawler import Crawler, Downloader
import os

def main():
    save_path = '/Users/yousukeyamamoto/Pictures/raw_data'
    url = 'https://mabui-onna.com/blog-entry-9.html'
    
    sample_urls = ['https://blog-imgs-101.fc2.com/g/m/8/gm8j46mpp36s/cooltext351950364688987.jpg', 
     'https://blogthumbnail.fc2.com/r72/143/g/m/8/gm8j46mpp36s/2021021413431000b.jpg']
    
      
    d = Downloader(sample_urls,save_path)
    d.download()

if __name__ == "__main__":
    main()