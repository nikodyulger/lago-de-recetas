import os
import boto3
import json
import awswrangler as wr
import streamlit as st

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

RECIPE_DATA_S3_URI = os.getenv("RECIPE_DATA_S3_URI")
MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT")
FEATURES = [
    "titulo",
    "link",
    "ingredientes",
    "elaboracion",
    "categoria",
    "similar",
]
print(RECIPE_DATA_S3_URI)
print(MODEL_ENDPOINT)

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

    vectorizer, doc_term_matrix = get_vectorizer()
    recipe_vec = vectorizer.transform([ingredients])
    similarities = cosine_similarity(recipe_vec, doc_term_matrix).flatten()
    indices = similarities.argsort()[-top_n:][::-1]
    df = load_data()
    df["similar"] = similarities * 100
    df["similar"] = df["similar"].round(2).apply(lambda value: f"{value}%")
    return df.iloc[indices][FEATURES]


def transpose_and_rename(df):
    transposed_df = df[FEATURES[1:]].T
    transposed_df.columns = df["titulo"].values
    return transposed_df


st.title("Recetas 🍽️")
with st.form("query-receta"):
    ingredients = st.text_input(
        "Escribe ingredientes👇", placeholder="Tomate pepino aceituna"
    )
    submit_button = st.form_submit_button("Buscar")

if ingredients:
    payload = {"ingredientes": ingredients}
    prediction_results = predict(payload)
    df_similar_recipes = find_similar_recipes(ingredients)

    st.markdown(
        f"Tú receta tiene pinta que sea **{prediction_results.get('prediction').upper()}**"
    )
    top_predictions = prediction_results.get("top_predictions")
    values = list(
        zip(
            [":first_place_medal:", ":second_place_medal:", ":third_place_medal:"],
            top_predictions.items(),
        )
    )
    for emoji, item in values:
        st.progress(
            round(item[1], 3), text=f"{item[0]} {emoji} \t {round(item[1]*100, 3)}%"
        )

    df_transposed = transpose_and_rename(df_similar_recipes)
    st.write("")
    st.write("¡Quizás estas recetas te gusten 👀!")
    for column in df_transposed.columns:
        st.dataframe(df_transposed[column], use_container_width=True)
