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

        titulo = soup.find(class_="m-titulo")
        ingredientes = soup.find(class_="ingredientes")
        section_tag = soup.find(class_="zona-ficha")
        p_tags = section_tag.find_all('p')

        receta = Receta(
            titulo=titulo.text,
            categoria=event.get("category"), 
            ingredientes=[i.text for i in ingredientes] if ingredientes else None,
            elaboracion="\n".join([p.text for p in p_tags])
        )
        recetas.append(receta)
        
    print(recetas)
    #TODO store the data in a csv in bucket
    return {
        "recetas": recetas
    }