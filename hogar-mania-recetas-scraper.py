import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup

URL = "https://www.hogarmania.com/cocina/recetas/sopas-cremas/sopa-fria-calabaza-naranja-3011.html"

@dataclass
class Receta:
    titulo: str
    autor: str
    categoria: str
    ingredientes: str
    elaboracion: str

response = requests.get(URL)
print(f"GET - {response.status_code} - {URL}")

soup = BeautifulSoup(response.content, 'html.parser')

titulo = soup.find(class_="m-titulo")
autor = soup.find(class_="autor")
ingredientes = soup.find(class_="ingredientes")
section_tag = soup.find(class_="zona-ficha")
p_tags = section_tag.find_all('p')

receta = Receta(
    titulo=titulo.text,
    autor=autor.text,
    categoria="Arroces y cereales", # esto vendrá desde el evento
    ingredientes="|".join([ i.text for i in ingredientes]),
    elaboracion="\n".join([ p.text for p in p_tags])
)
print(receta)


    