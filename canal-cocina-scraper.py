import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup


URL = "https://canalcocina.es/receta/ensalada-de-tomate-sandia-y-queso-feta-con-aceite-de-curcuma"

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

titulo = soup.find("h1").text.split('\t')[0]
autor = soup.find(attrs={"itemprop": "author"})
ingredientes = soup.find_all(attrs={"itemprop": "recipeIngredient"})
p_tags = soup.find(attrs={"itemprop":"recipeInstructions"}).find_all("p")

receta = Receta(
    titulo=titulo,
    autor=autor,
    categoria="",
    ingredientes="|".join([ i.text for i in ingredientes]),
    elaboracion="\n".join([ p.text for p in p_tags])
)

print(receta)