import requests

from bs4 import BeautifulSoup


BASE_URL = "https://recetasdecocina.elmundo.es/recetas/{category}"
PAGE_URL = "https://recetasdecocina.elmundo.es/recetas/{category}/page/{page}"

def lambda_handler(event, context):

    category = event.get("category")
    page = event.get("page")
    url = PAGE_URL.format(category=category, page=page) if page else BASE_URL.format(category=category)
    response = requests.get(url)
    print(f"GET - {response.status_code} - {url}")

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all("h3", class_="entry-title")
    links = [a.find("a").get("href") for a in articles]

    print(links)
    print(f"Found {len(links)} links")

    return {
        "links": links,
        "category": category
    }

# lambda_handler({
#     "category": "postres",
#     "page": 2
# }, None)