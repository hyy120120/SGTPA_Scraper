import re,time,random,requests,pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
BASE="https://www.sgtpa.com"
HEADERS={"User-Agent":"Mozilla/5.0"}
session=requests.Session();session.headers.update(HEADERS)
def clean(t): return re.sub(r"\s+"," ",t or "").strip()
def soup(url):
    r=session.get(url,timeout=30);r.raise_for_status();return BeautifulSoup(r.text,"lxml")
def parse_detail(url):
    s=soup(url)
    d={"Company Name":"","Contact Person":"","Phone":"","Mobile":"","Email":"","Website":"","Address":"","Description":"","Profile URL":url}
    h=s.find("h1")
    if h:d["Company Name"]=clean(h.get_text())
    for li in s.select("ul.details li"):
        c=" ".join(li.get("class",[]));txt=clean(li.get_text(" ",strip=True))
        if "member_contact_person_icon" in c:d["Contact Person"]=txt
        elif "member_phone_icon" in c:d["Phone"]=txt
        elif "member_mobile_icon" in c:d["Mobile"]=txt
        elif "member_address_icon" in c:d["Address"]=txt
        elif "member_email_icon" in c:d["Email"]=txt
        elif "member_website_icon" in c:
            a=li.find("a")
            if a:d["Website"]=a.get("href","")
    pg=s.select_one(".page_content")
    if pg:d["Description"]=clean(pg.get_text(" ",strip=True).replace("Description::",""))
    if not d["Email"]:
        m=re.findall(r'[\w\.-]+@[\w\.-]+\.\w+',s.get_text(" ",strip=True))
        if m:d["Email"]=", ".join(sorted(set(m)))
    return d
def scrape_list(url):
    s=soup(url);rows=[]
    for a in tqdm(s.select("h3 a"),leave=False):
        try:
            rows.append(parse_detail(urljoin(BASE,a["href"])))
            time.sleep(random.uniform(.3,.8))
        except Exception as e: print(e)
    return rows
def main():
    data=[]
    for start in tqdm(range(1,301,10)):
        url=BASE+"/members/" if start==1 else f"{BASE}/members/view/All/{start}"
        data.extend(scrape_list(url))
    df=pd.DataFrame(data).drop_duplicates()
    df.to_excel("SGTPA_Members.xlsx",index=False)
    print("Done")
if __name__=="__main__":main()
