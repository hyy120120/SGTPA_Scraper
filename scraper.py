import re
import time
import random
import requests
import pandas as pd

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE = "https://www.sgtpa.com"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}


session = requests.Session()
session.headers.update(HEADERS)


retry = Retry(
    total=5,
    backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)


adapter = HTTPAdapter(max_retries=retry)

session.mount(
    "https://",
    adapter
)

session.mount(
    "http://",
    adapter
)



def clean(t):
    return re.sub(r"\s+", " ", t or "").strip()



def soup(url):

    for attempt in range(3):

        try:

            time.sleep(
                random.uniform(3, 6)
            )

            r = session.get(
                url,
                timeout=60
            )


            if r.status_code == 403:

                print(
                    "403 blocked:",
                    url
                )

                time.sleep(20)
                continue


            r.raise_for_status()


            if "403 Forbidden" in r.text:

                print(
                    "Blocked page:",
                    url
                )

                time.sleep(20)
                continue


            return BeautifulSoup(
                r.text,
                "lxml"
            )


        except requests.exceptions.RequestException as e:

            print(
                f"Retry {attempt + 1}/3:",
                url
            )

            time.sleep(10)



    return None




def parse_detail(url):

    s = soup(url)


    if s is None:
        return None


    if s.find(
        "h1",
        string=re.compile("403")
    ):
        return None



    d = {
        "Company Name": "",
        "Contact Person": "",
        "Phone": "",
        "Mobile": "",
        "Email": "",
        "Website": "",
        "Address": "",
        "Description": "",
        "Category": "",
        "Profile URL": url
    }



    # Company Name extract

    h = s.find("h1")


    if h:

        name = clean(
            h.get_text()
        )


        if name and name.lower() not in [
            "403",
            "categories"
        ]:

            d["Company Name"] = name



    # Fallback: URL se company name lena

    if not d["Company Name"]:

        slug = url.split("/")[-1]

        slug = re.sub(
            r"_\d+\.html",
            "",
            slug
        )

        slug = slug.replace(
            "-",
            " "
        )

        d["Company Name"] = slug.title()




    for li in s.select(
        "ul.details li"
    ):

        c = " ".join(
            li.get("class", [])
        )


        txt = clean(
            li.get_text(
                " ",
                strip=True
            )
        )



        if "member_contact_person_icon" in c:

            d["Contact Person"] = txt


        elif "member_phone_icon" in c:

            d["Phone"] = txt


        elif "member_mobile_icon" in c:

            d["Mobile"] = txt


        elif "member_address_icon" in c:

            d["Address"] = txt


        elif "member_email_icon" in c:

            d["Email"] = txt


        elif "member_website_icon" in c:

            a = li.find("a")

            if a:

                d["Website"] = a.get(
                    "href",
                    ""
                )




    pg = s.select_one(
        ".page_content"
    )


    if pg:

        d["Description"] = clean(
            pg.get_text(
                " ",
                strip=True
            )
        )



    if not d["Email"]:

        emails = re.findall(
            r'[\w\.-]+@[\w\.-]+\.\w+',
            s.get_text(
                " ",
                strip=True
            )
        )


        if emails:

            d["Email"] = ", ".join(
                sorted(
                    set(emails)
                )
            )



    return d




def scrape_list(url):

    s = soup(url)


    if s is None:

        return []



    rows = []


    links = s.select(
        "h3 a"
    )



    for a in tqdm(
        links,
        leave=False
    ):

        try:


            detail_url = urljoin(
                BASE,
                a.get("href")
            )


            data = parse_detail(
                detail_url
            )


            if data:

                rows.append(
                    data
                )


            time.sleep(
                random.uniform(3,6)
            )


        except Exception as e:

            print(
                "Detail failed:",
                e
            )



    return rows





def main():

    data = []

    start = 1


    while True:


        if start == 1:

            url = BASE + "/members/"

        else:

            url = f"{BASE}/members/view/All/{start}"



        print(
            "\nScraping:",
            url
        )



        try:

            result = scrape_list(
                url
            )


            # agar page par koi record nahi mila
            # to scraping stop

            if not result:

                print(
                    "No more records found. Stopping..."
                )

                break



            data.extend(
                result
            )


            print(
                "Records:",
                len(data)
            )



            # next page offset

            start += 10



        except Exception as e:


            print(
                "Page failed:",
                e
            )


            start += 10





    print(
        "\nTotal records:",
        len(data)
    )



    df = pd.DataFrame(
        data
    )



    df = df.drop_duplicates()



    df.to_excel(
        "SGTPA_Members.xlsx",
        index=False
    )



    print(
        "Excel created successfully"
    )




if __name__ == "__main__":
    main()
