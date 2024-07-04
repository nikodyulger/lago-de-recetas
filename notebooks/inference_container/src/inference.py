import os
import joblib
import numpy as np


def load_model(model_dir):
    """
    Load the model from the specified directory.
    """
    return joblib.load(os.path.join(model_dir, "model.joblib"))


def load_label_encoder():
    return joblib.load("label_encoder.joblib")


def get_top_3_predictions(probabilities, class_labels):
    top_3 = np.argsort(probabilities)[-3:][::-1]
    return {class_labels[i]: probabilities[i] for i in top_3}


def predict(body, model):
    """
    Generate predictions for the incoming request using the model.
    """
    label_encoder = load_label_encoder()
    ingrs = body.get("ingredientes")

    class_pred = model.predict([ingrs])
    prediction = label_encoder.inverse_transform(class_pred).tolist().pop()

    probabilities = model.predict_proba([ingrs]).flatten()
    best_proba = np.argsort(probabilities)[-3:][::-1]
    top_predictions = dict(
        zip(label_encoder.inverse_transform(best_proba), probabilities[best_proba])
    )

    return {"prediction": prediction, "top_predictions": top_predictions}
