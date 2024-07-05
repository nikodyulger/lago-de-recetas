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


def predict(payload):
    response = runtime.invoke_endpoint(
        EndpointName=MODEL_ENDPOINT,
        Body=json.dumps(payload),
        ContentType="application/json",
    )
    results = json.loads(response.get("Body").next().decode())
    return results
