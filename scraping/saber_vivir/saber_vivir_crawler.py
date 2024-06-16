import json
import requests

from bs4 import BeautifulSoup

BASE_URL = "https://www.sabervivir.es/nutricion-y-cocina/recetas-de-cocina?start={page}"
WEBSITE_URL = "https://www.sabervivir.es/"


def lambda_handler(event, context):

    pages = event.get("pages")
    links = []
    for page in pages:
        try:
            url = BASE_URL.format(page=page)
            response = requests.get(url)
            print(f"GET - {response.status_code} - {url}")
        except requests.exceptions.HTTPError:
            continue

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("h3", class_="catItemTitle")
            links += [WEBSITE_URL + a.find("a").get("href") for a in articles]
        except (AttributeError, ValueError, TypeError):
            continue

    print(json.dumps(links, indent=4))
    print(f"Found {len(links)} links")

    return {"links": links}
