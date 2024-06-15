import json
import requests
import time

from bs4 import BeautifulSoup

URL = "https://recetasdecocina.elmundo.es/"
PAGE_URL = "https://recetasdecocina.elmundo.es/recetas/{category}/page/{page}"

response = requests.get(URL)

print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

a_tags = soup.find_all("a", class_="td-pulldown-size")
all_links = [link.get("href") for link in a_tags]
categories = [l.strip("/").rsplit("/", 1)[-1] for l in all_links]
print(categories)

init_data = []
for category, link in zip(categories, all_links):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        num_pages = soup.find("a", class_="last").get_text()
    except AttributeError:
        num_pages = soup.find("span", class_="pages").get_text().split()[-1]
    print(num_pages)

    init_data.append({"category": category, "pages": [*range(1, int(num_pages) + 1)]})
    print(init_data)
    with open("init_data_el_mundo.json", "w") as f:
        json.dump(init_data, f)
    time.sleep(5)
