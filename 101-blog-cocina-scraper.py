import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup


URL = "https://101blogdecocina.com/receta/canelones-de-boletos-trufa-y-foie-2609"

@dataclass
class Receta:
    titulo: str
    autor: str
    categoria: str
    ingredientes: str
    elaboracion: str


response = requests.get(URL)
print(f"GET - {response.status_code} - {URL}")

soup = BeautifulSoup(response.content, 'html.parser')

titulo = soup.find("h1").text
autor = "101blog"
categoria = soup.find(class_="categoria").find("a").text
ingredientes = soup.find(class_="feature-title").find_next_siblings("ul")
p_tags = soup.find('h2', string='Elaboración').find_next_siblings("p")

receta = Receta(
    titulo=titulo,
    autor=autor,
    categoria=categoria,
    ingredientes="|".join([ i.text for i in ingredientes]),
    elaboracion="\n".join([ p.text for p in p_tags])
)

print(receta)