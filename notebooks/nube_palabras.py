import awswrangler as wr
from wordcloud import WordCloud

df_recipe_data = wr.s3.read_csv(
    path="s3://recipes-data-models-sagemaker-bucket/data/cleaned_recipes.csv"
)
word_freq = df_recipe_data["categoria"].value_counts().to_dict()
wordcloud = WordCloud(
    width=800, height=400, max_words=200, background_color="white"
).generate_from_frequencies(word_freq)
wordcloud.to_file("wordcloud.png")
