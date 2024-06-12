import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup


BASE_URL = "https://www.antena3.com/programas/karlos-arguinano/recetas/{category}/"
PAGE_URL = "https://www.antena3.com/programas/karlos-arguinano/recetas/{category}-{page}/"

def lambda_handler(event, context):

    category = event.get("category")
    page = event.get("page")
    url = PAGE_URL.format(category=category, page=page) if page else BASE_URL.format(category=category)
    response = requests.get(url)
    print(f"GET - {response.status_code} - {url}")

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all("h2", class_="article__title")
    links = [a.find("a").get("href") for a in articles]

    print(f"Found {len(links)} links")
    print(links)
    return {
        "links": links,
        "category": category
    }

lambda_handler({
    "category": "entrantes",
    "page": 2
}, None)