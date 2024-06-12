import requests

from bs4 import BeautifulSoup

# 47 paginas, el start empieza en 0 y va de 10 en 10, ejemplo pagina 2 sería start = 10
BASE_URL = "https://www.sabervivir.es/nutricion-y-cocina/recetas-de-cocina?start={page}"
WEBSITE_URL = "https://www.sabervivir.es/"

def lambda_handler(event, context):

    page = event.get("page")
    url = BASE_URL.format(page=page)
    response = requests.get(url)
    print(f"GET - {response.status_code} - {url}")

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all("h3", class_="catItemTitle")
    links = [WEBSITE_URL + a.find("a").get("href") for a in articles]

    print(f"Found {len(links)} links")
    print(links)
    return {
        "links": links
    }

lambda_handler({
    "page": 0
}, None)