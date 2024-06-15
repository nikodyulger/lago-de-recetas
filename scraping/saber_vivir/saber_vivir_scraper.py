import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup

@dataclass
class Receta:
    titulo: str
    categoria: str
    ingredientes: str
    elaboracion: str

def lambda_handler(event, context):

    links = event.get("links")
    recetas = []
    for link in links:
        response = requests.get(link)
        print(f"GET - {response.status_code} - {link}")

        soup = BeautifulSoup(response.content, 'html.parser')

        titulo = soup.find("h1", class_="itemTitle").text
        categoria = soup.find(class_="itemCategory").text
        ingredientes = soup.find("h2", string="Ingredientes:").find_next_sibling("ul").find_all("li")
        elaboracion = soup.find("h2", string="Preparación:").find_next_sibling("ol").find_all("li")

        receta = Receta(
            titulo=titulo.strip(),
            categoria=categoria.strip(),
            ingredientes=[ i.text for i in ingredientes],
            elaboracion="\n".join([ p.text for p in elaboracion])
        )
        print(receta)
        recetas.append()
    #TODO store the data in a csv in bucket
    return {
        "recetas": recetas
    }