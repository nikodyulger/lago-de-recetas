import json
import requests
import time

from bs4 import BeautifulSoup

WEBSITE = "https://www.hogarmania.com"
URL = "https://www.hogarmania.com/cocina/recetas"

response = requests.get(URL)
print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

a_tags = soup.select("h2.m-titulo a[href]")
all_links = [link.get("href") for link in a_tags]
all_links = [link if "https" in link else f"{WEBSITE}{link}" for link in all_links]
categories = [l.strip("/").rsplit("/", 1)[-1] for l in all_links]
print(categories)


def get_num_pages(link, page, visited_pages):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    relative_href = soup.select("ul.pagination li a")[-2].get("href")
    page = soup.select("ul.pagination li a")[-2].get_text()
    last_page_href = f"{WEBSITE}{relative_href}"
    if int(page) not in visited_pages:
        visited_pages.add(int(page))
        time.sleep(3)
        return get_num_pages(last_page_href, page, visited_pages)

    return max(visited_pages)


init_data = []
for category, link in zip(categories, all_links):
    print(link)
    visited_pages = set()
    num_pages = get_num_pages(link, 1, visited_pages)
    print(num_pages)
    init_data.append({"category": category, "pages": [*range(1, int(num_pages) + 1)]})
    print(init_data)
    with open("init_data_hogar_mania.json", "w") as f:
        json.dump(init_data, f)
    time.sleep(5)
