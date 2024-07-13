import re
import json
import requests
import time

from bs4 import BeautifulSoup

URL = "https://www.sabervivir.es/nutricion-y-cocina/"

response = requests.get(URL)
print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")
last_a_tag = soup.find("a", attrs={"title": "Final"})
href = last_a_tag.get("href")
print(href)
last_starter = re.search(r"\d+", href).group()
print(last_starter)
pages = [*range(0, int(last_starter) + 1, 10)]
print(pages)
with open("init_data_saber_vivir.json", "w") as f:
    json.dump({"pages": pages}, f)
