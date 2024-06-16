import requests
import json

from bs4 import BeautifulSoup

PAGE_URL = "https://recetasdecocina.elmundo.es/recetas/{category}/page/{page}"


def lambda_handler(event, context):

    category = event.get("category")
    pages = event.get("pages")
    links = []
    for page in pages:
        try:
            url = PAGE_URL.format(category=category, page=page)
            response = requests.get(url)
            print(f"GET - {response.status_code} - {url}")
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            continue

        try:
            soup = BeautifulSoup(response.text, "html.parser")

            articles = soup.find_all("h3", class_="entry-title")
            links += [a.find("a").get("href") for a in articles]
        except (AttributeError, ValueError, TypeError):
            continue

    print(json.dumps(links, indent=4))
    print(f"Found {len(links)} links")

    return {"links": links, "category": category}
