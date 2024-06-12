import re
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

        titulo = soup.find("h1", class_="entry-title").text
        ingredientes = soup.find("h2", class_="wp-block-heading", string=re.compile("Ingredientes")).find_next_sibling("ul").find_all("li")
        elaboracion = soup.find("h2", class_="wp-block-heading", string=re.compile("Cómo hacer")).find_next_siblings("p")

        
        receta = Receta(
            titulo=titulo,
            categoria=event.get("category"),
            ingredientes=[i.text for i in ingredientes],
            elaboracion="\n".join([ p.text for p in elaboracion])
        )

        recetas.append(receta)
    #TODO store the data in a csv in bucket
    return {
        "recetas": recetas
    }

# lambda_handler({
#     "category": "postres",
#     "links": ['https://recetasdecocina.elmundo.es/2023/12/naranjas-confitadas-receta-facil-casera-navidad.html', 'https://recetasdecocina.elmundo.es/2023/12/mantecados-receta-facil-casera.html']
# }, None)