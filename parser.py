"""
parser.py - Parse SGTPA member detail pages.
"""
import re,logging,requests
from bs4 import BeautifulSoup

HEADERS={"User-Agent":"Mozilla/5.0"}

class Parser:
    def __init__(self):
        self.s=requests.Session()
        self.s.headers.update(HEADERS)

    def _clean(self,t):
        return re.sub(r"\s+"," ",t or "").strip()

    def parse(self,url):
        r=self.s.get(url,timeout=30)
        r.raise_for_status()
        soup=BeautifulSoup(r.text,"lxml")
        data={
            "Company Name":"","Contact Person":"","Phone":"","Mobile":"",
            "Email":"","Website":"","Address":"","Description":"",
            "Category":"","Profile URL":url
        }
        h=soup.find("h1")
        if h:data["Company Name"]=self._clean(h.get_text())

        cat=soup.select_one(".arrowlistmenu li a[href*='category']")
        if cat and "All Categories" not in cat.get_text():
            data["Category"]=self._clean(cat.get_text())

        for li in soup.select("ul.details li"):
            cls=" ".join(li.get("class",[]))
            txt=self._clean(li.get_text(" ",strip=True))
            if "contact_person" in cls:
                data["Contact Person"]=txt
            elif "phone" in cls:
                data["Phone"]=txt
            elif "mobile" in cls:
                data["Mobile"]=txt
            elif "address" in cls:
                data["Address"]=txt
            elif "email" in cls:
                data["Email"]=txt
            elif "website" in cls:
                a=li.find("a")
                if a:data["Website"]=a.get("href","")

        page=soup.select_one(".page_content")
        if page:
            data["Description"]=self._clean(page.get_text(" ",strip=True).replace("Description::",""))

        if not data["Email"]:
            emails=sorted(set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+',soup.get_text(" ",strip=True))))
            data["Email"]=", ".join(emails)

        if not data["Website"]:
            m=re.findall(r'https?://[^\s<>"\']+',str(soup))
            if m:
                data["Website"]=", ".join(sorted(set(m)))
        return data

if __name__=="__main__":
    import sys,pprint
    pprint.pp(Parser().parse(sys.argv[1]))
