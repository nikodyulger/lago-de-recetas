import requests
import pandas as pd
import awswrangler as wr

from datetime import datetime
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup

BUCKET_PATH = "s3://raw-recipe-data-bucket/saber_vivir/recetas_{timestamp}.parquet"


@dataclass
class Receta:
    titulo: str
    categoria: str
    ingredientes: str
    elaboracion: str
    link: str


def lambda_handler(event, context):

    links = event.get("links")
    recetas = []
    for link in links:
        response = requests.get(link)
        print(f"GET - {response.status_code} - {link}")

        soup = BeautifulSoup(response.content, "html.parser")

        titulo = soup.find("h1", class_="itemTitle").text
        categoria = soup.find(class_="itemCategory").text
        ingredientes = (
            soup.find("h2", string="Ingredientes:")
            .find_next_sibling("ul")
            .find_all("li")
        )
        elaboracion = (
            soup.find("h2", string="Preparación:")
            .find_next_sibling("ol")
            .find_all("li")
        )

        receta = Receta(
            titulo=titulo.strip(),
            categoria=categoria.strip(),
            ingredientes=[i.text for i in ingredientes],
            elaboracion="\n".join([p.text for p in elaboracion]),
            link=link,
        )

        print(receta)
        recetas.append(asdict(receta))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df = pd.DataFrame(recetas)
    wr.s3.to_parquet(df=df, path=BUCKET_PATH.format(timestamp=timestamp), index=False)

    return {"recetas": recetas}
