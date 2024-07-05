import os
import boto3
import json
import awswrangler as wr
import pandas as pd
import streamlit as st

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

RECIPE_DATA_S3_URI = os.getenv("RECIPE_DATA_S3_URI")
MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT")

runtime = boto3.client(service_name="sagemaker-runtime")


@st.cache_data
def load_data():
    df = wr.s3.read_csv(path=RECIPE_DATA_S3_URI)
    return df


@st.cache_resource
def get_vectorizer():
    df = load_data()
    vectorizer = TfidfVectorizer()
    doc_term_matrix = vectorizer.fit_transform(df["ingredientes_limpios"])
    return vectorizer, doc_term_matrix


def predict(payload):
    response = runtime.invoke_endpoint(
        EndpointName=MODEL_ENDPOINT,
        Body=json.dumps(payload),
        ContentType="application/json",
    )
    results = json.loads(response.get("Body").next().decode())
    return results


def find_similar_recipes(ingredients, top_n=3):
    features = ["titulo_link", "link", "ingredientes", "elaboracion", "categoria"]
    vectorizer, doc_term_matrix = get_vectorizer()
    recipe_vec = vectorizer.transform([ingredients])
    similarities = cosine_similarity(recipe_vec, doc_term_matrix).flatten()
    indices = similarities.argsort()[-top_n:][::-1]
    df = load_data()
    return df.iloc[indices][features]


st.title("Recetas 🍽️")
with st.form("query-receta"):
    ingredients = st.text_input(
        "Escribe ingredientes👇", placeholder="Tomate pepino aceituna"
    )
    submit_button = st.form_submit_button("Buscar")
