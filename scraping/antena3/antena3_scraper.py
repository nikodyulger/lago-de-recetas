import time
import requests
import pandas as pd
import awswrangler as wr

from datetime import datetime
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup

BUCKET_PATH = "s3://raw-recipe-data-bucket/antena3/recetas_{timestamp}.parquet"


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

        try:
            response = requests.get(link)
            print(f"GET - {response.status_code} - {link}")
            response.raise_for_status()

        except requests.exceptions.HTTPError:
            continue

        try:
            soup = BeautifulSoup(response.content, "html.parser")
            titulo = soup.find("h1", class_="article-main__title").get_text()

            intext = soup.find(id="intext")

            ingredientes = []
            elaboracion = []
            current_section = ""
            for tag in intext:
                if "ingredientes" in tag.get_text().lower():
                    current_section = "ingredientes"
                if "Elabor" in tag.get_text():
                    current_section = "elaboracion"

                if current_section == "ingredientes":
                    if tag.name == "ul":
                        ingredientes += [ingr.get_text() for ingr in tag.find_all("li")]
                    if tag.name == "p":
                        ingredientes.append(tag.get_text())
                elif current_section == "elaboracion":
                    elaboracion.append(tag.get_text())

            receta = Receta(
                titulo=titulo,
                categoria=event.get("category"),
                ingredientes=ingredientes[1:],
                elaboracion="\n".join(elaboracion[1:]),
                link=link,
            )
            print(receta)
        except (AttributeError, ValueError, TypeError, StopIteration) as e:
            print(e)
            continue

        recetas.append(asdict(receta))
        time.sleep(5)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df = pd.DataFrame(recetas)
    print(f"STORE DATAFRAME - {BUCKET_PATH.format(timestamp=timestamp)}")
    wr.s3.to_parquet(df=df, path=BUCKET_PATH.format(timestamp=timestamp), index=False)

    return {"recetas": recetas}
