import json
import requests
import time

from bs4 import BeautifulSoup

URL = "https://www.antena3.com/programas/karlos-arguinano/"
PAGE_URL = (
    "https://www.antena3.com/programas/karlos-arguinano/recetas/{category}-{page}/"
)

del_hrefs = ["trucos", "noticias"]
response = requests.get(URL)

print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

items = soup.find("div", class_="items")
a_tags = items.find_all("a")
all_links = [link.get("href") for link in a_tags]
category_links = [
    link
    for link in all_links
    if not any(exclude in link for exclude in ["trucos", "noticias"])
    and not link.endswith("/recetas/")
]
categories = [l.strip("/").rsplit("/", 1)[-1] for l in category_links]

print(categories)
init_data = []
for category in categories:
    pages = []
    for page in range(2, 100):
        response = requests.get(
            f"https://www.antena3.com/programas/karlos-arguinano/recetas/{category}-{page}/"
        )
        print(page)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            next_link = soup.select_one("li.pagination__item--next a[href]")
            print(next_link)
            if next_link:
                pages.append(page)
            else:
                break
    init_data.append({"category": category, "pages": pages})
    print(init_data)
    with open("init_data_antena3.json", "w") as f:
        json.dump(init_data, f)
    time.sleep(5)
