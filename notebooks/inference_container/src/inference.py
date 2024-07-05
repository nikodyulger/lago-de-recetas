import os
import joblib
import numpy as np


def load_model_and_encoder(model_dir):
    """
    Load the model from the specified directory.
    """
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    label_encoder = joblib.load(os.path.join(model_dir, "label_encoder.joblib"))
    return (
        model,
        label_encoder,
    )


def get_top_3_predictions(probabilities, class_labels):
    top_3 = np.argsort(probabilities)[-3:][::-1]
    return {class_labels[i]: probabilities[i] for i in top_3}


def predict(body, model, label_encoder):
    """
    Generate predictions for the incoming request using the model.
    """
    ingrs = body.get("ingredientes")

    class_pred = model.predict([ingrs])
    prediction = label_encoder.inverse_transform(class_pred).tolist().pop()

    probabilities = model.predict_proba([ingrs]).flatten()
    best_proba = np.argsort(probabilities)[-3:][::-1]
    top_predictions = dict(
        zip(label_encoder.inverse_transform(best_proba), probabilities[best_proba])
    )

    return {"prediction": prediction, "top_predictions": top_predictions}
