import requests_html
import os, sys, time
import urllib.request
import requests as req
from tqdm import tqdm, trange


class Downloader:
    def __init__(self, save_dir="save"):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.save_dir = save_dir
        
    def _download_image(self, url, fname):
        with open(os.path.join(self.curr_save_dir,fname), 'wb') as f:
            n_retry = 3
            while n_retry:
                try:
                    browser = requests_html.HTMLSession()
                    this_image = browser.get(url, stream=True)
                    break
                except Exception as e:
                    browser.close()
                    n_retry -= 1
                    time.sleep(10)
                    #print('err', str(e))
            for i in this_image.iter_content(1024):
                if not i:
                    break
                else:
                    f.write(i)
            #print('DONE!')
            browser.close()
                
        
    def _scrape_pages(self, start_url, title):
        image_url = "none"
        for page in trange(1,50,ascii=True, desc=title):
            n_retry = 3
            while n_retry:
                #print("\t\tprogress page %02d..."%page, end='')
                try:
                    browser = requests_html.HTMLSession()
                    this_page = browser.get(start_url + '?p=%d'%page)
                    this_page.html.render()
                    this_page.encoding = "utf-8"
                    img_url = this_page.html.xpath('//img[@id="manga"]')[0].attrs['src']
                    browser.close()
                    browser = requests_html.HTMLSession()
                    this_page = browser.get("https:" + img_url)
                    this_page.html.render()
                    this_page.encoding = "utf-8"
                    img_url = this_page.html.xpath('//img')[0].attrs['src']
                    browser.close()
                    if img_url == image_url:
                        break
                    self._download_image(img_url, "%03d_%03d.jpg"%(int(title.split('集')[0]),page))
                    break
                except Exception as e:
                    browser.close()
                    n_retry -= 1
                    time.sleep(10)
                    #print('err', str(e))
            if img_url == image_url:
                break
            else:
                image_url = img_url
    
    def _scrape_episodes(self, main_page, main_url, title):
        print("start crawling %s"%title)
        els = main_page.html.xpath('//div[@class="chapter-list cf mt10"]//a')
        for el in els:
            first_page_title = el.attrs['title']
            first_page_url = main_url + el.attrs['href'].split(r'/')[-1]
            self._scrape_pages(first_page_url, first_page_title)
        
    
    def _scrape_comics(self):
        for url in self.comic_mainpage:
            browser = requests_html.HTMLSession()
            main_page = browser.get(url)
            main_page.encoding = "utf-8"
            comic_title = main_page.html.xpath('//title/text()')[0].split('漫畫')[0]
            browser.close()
            
            self.curr_save_dir = os.path.join(self.save_dir, comic_title)
            if not os.path.exists(self.curr_save_dir):
                os.makedirs(self.curr_save_dir)
            
            self._scrape_episodes(main_page, url, comic_title)
    
    def start(self, comics="comics.txt"):
        if not os.path.exists(comics):
            print('NO COMICS_FILE DETECTED!')
            sys.exit(0)
        with open(comics,'r') as f:
            self.comic_mainpage = f.readlines()
        self.comic_mainpage = [x.strip() for x in self.comic_mainpage]
        print('Target Comics Loaded! (total: %d comics)'%len(self.comic_mainpage))
        
        self._scrape_comics()
        

if __name__ == "__main__":
    d = Downloader(save_dir="save")
    d.start(comics="comics.txt")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        