import requests

from bs4 import BeautifulSoup

WEBSITE_URL = "https://www.hogarmania.com/"
BASE_URL = "https://www.hogarmania.com/cocina/recetas/{category}"
PAGE_URL = "https://www.hogarmania.com/cocina/recetas/{category}/pagina/{page}"

def lambda_handler(event, context):

    category = event.get("category")
    page = event.get("page")
    url = PAGE_URL.format(category=category, page=page) if page else BASE_URL.format(category=category)
    response = requests.get(url)

    print(f"GET - {response.status_code} - {url}")

    soup = BeautifulSoup(response.text, 'html.parser')

    titulos = soup.find_all("h2", class_="m-titulo")
    links = [WEBSITE_URL + t.find("a").get("href") for t in titulos]
    print(links)
    print(f"Found {len(links)} links")

    return {
        "links": links
    }


# next_link = https://www.hogarmania.com/cocina/recetas/aperitivos/pagina/{i} # 

lambda_handler({
    "category": "aperitivos",
    "page": 2
}, None)