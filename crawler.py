"""
crawler.py - SGTPA crawler
Discovers member URLs with pagination, retry, resume and logging.
"""
import json,random,time,logging
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE="https://www.sgtpa.com"
START_URL=BASE+"/members/"
HEADERS={"User-Agent":"Mozilla/5.0"}
WORKERS=5
RETRY=3

logging.basicConfig(filename="crawler.log",level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

class Crawler:
    def __init__(self):
        self.s=requests.Session()
        self.s.headers.update(HEADERS)

    def get(self,url):
        for i in range(RETRY):
            try:
                r=self.s.get(url,timeout=30)
                r.raise_for_status()
                return BeautifulSoup(r.text,"lxml")
            except Exception:
                if i==RETRY-1: raise
                time.sleep((2**i)+random.random())

    def detect_pages(self):
        soup=self.get(START_URL)
        starts={1}
        for a in soup.select(".pagination a"):
            href=a.get("href","")
            if "/view/All/" in href:
                try:
                    starts.add(int(href.rstrip("/").split("/")[-1]))
                except: pass
        if len(starts)==1:
            starts.update(range(11,301,10))
        return sorted(starts)

    def member_links(self,page_url):
        soup=self.get(page_url)
        links=set()
        for a in soup.select("h3 a[href]"):
            links.add(urljoin(BASE,a["href"]))
        return links

    def crawl(self):
        pages=self.detect_pages()
        urls=set()
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs=[]
            for st in pages:
                u=START_URL if st==1 else f"{BASE}/members/view/All/{st}"
                futs.append(ex.submit(self.member_links,u))
            for f in as_completed(futs):
                try:
                    urls|=f.result()
                except Exception as e:
                    logging.exception(e)
        lst=sorted(urls)
        with open("member_urls.json","w",encoding="utf-8") as fp:
            json.dump(lst,fp,indent=2)
        print(f"Discovered {len(lst)} member URLs.")
        return lst

if __name__=="__main__":
    Crawler().crawl()
