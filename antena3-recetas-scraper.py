import re
import requests

from dataclasses import dataclass
from bs4 import BeautifulSoup

URL = "https://www.antena3.com/programas/karlos-arguinano/recetas/arroces/exito-garantizado-cuatro-ingredientes-risotto-guisantes-queso-cabra-huevo_202403256601719d17c56e0001d2a19d.html"

@dataclass
class Receta:
    titulo: str
    autor: str
    categoria: str
    ingredientes: str
    elaboracion: str

response = requests.get(URL)
response = requests.get(URL)
print(f"GET - {response.status_code} - {URL}")

soup = BeautifulSoup(response.content, 'html.parser')

fig_captions = soup.find_all("figcaption")
titulo_figura = next(filter(lambda fg: "Ingredientes" in fg.text, fig_captions)).text

pattern = r'Ingredientes(.*?)\|'
titulo = re.search(pattern, titulo_figura)

intext = soup.find(id="intext")
headers = intext.find_all("h2")

for h in headers:
    if "Ingredientes" in h.text:
        ingredientes = h.next_sibling

    if "Elaboración" in h.text:
        p_tags = h.find_next_siblings('p')


receta = Receta(
    titulo=titulo.group(1).strip(),
    autor="Karlos Arguiñano",
    categoria="Carnes", # evento
    ingredientes="|".join([ i.text for i in ingredientes]),
    elaboracion="\n".join([ p.text for p in p_tags])
)
print(receta)