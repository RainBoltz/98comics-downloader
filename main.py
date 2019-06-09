import requests_html
import os, sys, time
import urllib.request
import requests as req
import configparser


class Downloader:
    def __init__(self, save_dir="save"):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.save_dir = save_dir
        
    def _download_image(self, url, fname):
        with open(os.path.join(self.curr_save_dir,fname), 'wb') as f:
            n_retry = int(self.config["settings"]["err_n_retry"])
            while n_retry:
                try:
                    browser = requests_html.HTMLSession()
                    this_image = browser.get(url, stream=True)
                    break
                except Exception as e:
                    browser.close()
                    n_retry -= 1
                    time.sleep(int(self.config["settings"]["err_s_delay"]))
                    print('img_%s err'%fname, str(e))
            for i in this_image.iter_content(1024):
                if not i:
                    break
                else:
                    f.write(i)
            #print('DONE!')
            browser.close()
                
        
    def _scrape_pages(self, start_url, title):
        image_url = "none"
        print("crawling %s..."%title)
        for page in range(1,int(self.config["settings"]["max_pages"])+1):
            n_retry = int(self.config["settings"]["err_n_retry"])
            while n_retry:
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
                    
                    if "集" in title:
                        if '.' not in title:
                            img_fname = "%03d_%03d.jpg"%(int(title.split('集')[0]),page)
                        else:
                            print("not a good comic ... (\"%s\" is a wrong format)"%title)
                            sys.exit(0)
                    elif "卷" in title:
                        img_fname = "%03d_%03d.jpg"%(int(title.split('卷')[0]),page)
                    else:
                        print("not a good comic ... (\"%s\" is a wrong format)"%title)
                            
                    self._download_image(img_url, img_fname)
                    break
                except Exception as e:
                    browser.close()
                    n_retry -= 1
                    time.sleep(int(self.config["settings"]["err_s_delay"]))
                    print('page#%03d err:'%page, str(e))
            if img_url == image_url:
                break
            else:
                image_url = img_url
    
    def _scrape_episodes(self, main_page, main_url, title, start_episode=1):
        print(":: start crawling %s ::"%title)
        els = main_page.html.xpath('//div[@class="chapter-list cf mt10"]//a')
        for i_el in range(start_episode-1, len(els)):
            el = els[i_el]
            first_page_title = el.attrs['title']
            first_page_url = main_url + el.attrs['href'].split(r'/')[-1]
            self._scrape_pages(first_page_url, first_page_title)
        
    
    def _scrape_comics(self):
        for url in self.config["comics"]:
            browser = requests_html.HTMLSession()
            main_page = browser.get(url)
            main_page.encoding = "utf-8"
            comic_title = main_page.html.xpath('//title/text()')[0].split('漫畫')[0]
            browser.close()
            
            self.curr_save_dir = os.path.join(self.save_dir, comic_title)
            if not os.path.exists(self.curr_save_dir):
                os.makedirs(self.curr_save_dir)
                self._scrape_episodes(main_page, url, comic_title)
            else:
                imgs = os.listdir(self.curr_save_dir)
                if len(imgs) == 0:
                    self._scrape_episodes(main_page, url, comic_title)
                else:
                    sorted_imgs = sorted(imgs)
                    last_episode = int(sorted_imgs[-1].split(r'_')[0])
                    self._scrape_episodes(main_page, url, comic_title, last_episode)
                
            
    
    def start(self, comics=None):
        if comics == None:
            print('NO CONFIG_FILE GIVEN!')
            sys.exit(0)
        elif not os.path.exists(comics):
            print('NO CONFIG_FILE DETECTED!')
            sys.exit(0)
        
        self.config = configparser.ConfigParser(allow_no_value=True, delimiters=("="), inline_comment_prefixes=(";"))
        self.config.read(comics, encoding="utf-8-sig")
        
        print('Target Comics Loaded! (total: %d comics)'%len(self.config['comics']))
        
        self._scrape_comics()
        

if __name__ == "__main__":
    d = Downloader(save_dir="save")
    d.start(comics="config.ini")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        