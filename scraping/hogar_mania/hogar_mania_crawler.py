import json
import requests

from bs4 import BeautifulSoup

WEBSITE_URL = "https://www.hogarmania.com/"
PAGE_URL = "https://www.hogarmania.com/cocina/recetas/{category}/pagina/{page}"


def lambda_handler(event, context):

    category = event.get("category")
    pages = event.get("pages")
    links = []
    for page in pages:
        try:
            url = PAGE_URL.format(category=category, page=page)
            response = requests.get(url)
            print(f"GET - {response.status_code} - {url}")
        except requests.exceptions.HTTPError:
            continue

        try:
            soup = BeautifulSoup(response.text, "html.parser")

            titulos = soup.find_all("h2", class_="m-titulo")
            links += [WEBSITE_URL + t.find("a").get("href") for t in titulos]
        except (AttributeError, ValueError, TypeError):
            continue

    print(json.dumps(links, indent=4))
    print(f"Found {len(links)} links")

    return {"links": links, "category": category}
