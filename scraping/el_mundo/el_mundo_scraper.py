import re
import requests
import pandas as pd
import awswrangler as wr

from datetime import datetime
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup

BUCKET_PATH = "s3://raw-recipe-data-bucket/el_mundo/recetas_{timestamp}.parquet"


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

        titulo = soup.find("h1", class_="entry-title").text
        ingredientes = (
            soup.find(
                "h2", class_="wp-block-heading", string=re.compile("Ingredientes")
            )
            .find_next_sibling("ul")
            .find_all("li")
        )
        elaboracion = soup.find(
            "h2", class_="wp-block-heading", string=re.compile("Cómo hacer")
        ).find_next_siblings("p")

        receta = Receta(
            titulo=titulo,
            categoria=event.get("category"),
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


lambda_handler(
    {
        "category": "postres",
        "links": [
            "https://recetasdecocina.elmundo.es/2023/12/naranjas-confitadas-receta-facil-casera-navidad.html",
            "https://recetasdecocina.elmundo.es/2023/12/mantecados-receta-facil-casera.html",
        ],
    },
    None,
)
