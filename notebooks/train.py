import os
import argparse
import pandas as pd

from sklearn.externals import joblib
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier


def parse_args():
    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script.
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.05)

    # Data, model, and output directories
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR")
    )
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST"))

    return parser.parse_known_args()


def load_data(file_path):
    """
    Load and preprocess the data.

    Args:
        file_path: Path to the directory containing the data.

    Returns:
        features: Features of the testing dataset.
        label: Labels of the testing dataset.
    """
    df = pd.read_csv(os.path.join(file_path))
    X = df["ingredientes_limpios"]
    y = df["encoded_categoria"]
    return X, y


def fit_model(hyperparameters, X_train, y_train, X_test, y_test):
    """
    Train a Logistic Regression on the provided data.

    Args:
        args: Parsed command-line arguments containing hyperparameters.
        x_train: Features of the training dataset.
        y_train: Labels of the training dataset.
        x_test: Features of the testing dataset.
        y_test: Labels of the testing dataset.

    Returns:
        model: A trained Random Forest Classifier model.
    """
    model = Pipeline(
        [("countvect", TfidfVectorizer(use_idf=True)), ("clf", SGDClassifier())]
    )
    model.fit(X_train, y_train)

    print(f"Training Accuracy: {model.score(X_train, y_train):.3f}")
    print(f"Testing Accuracy: {model.score(X_test, y_test):.3f}")

    y_train_pred = model.predict(y_train)
    y_test_pred = model.predict(y_test)
    print("TRAIN CLASSIFICATION REPORT")
    print(classification_report(y_train, y_train_pred, target_names=le.classes_))
    print("TEST CLASSIFICATION REPORT")
    print(classification_report(y_test, y_test_pred, target_names=le.classes_))
    return model


if __name__ == "__main__":
    # Parse Command-Line Arguments
    args, unknown = parse_args()

    # Load Training and Testing Data
    X_train, y_train = load_data(args.train)
    X_test, y_test = load_data(args.test)

    # Train the Model
    classifier = fit_model(args, X_train, y_train, X_test, y_test)

    # Save the Model
    joblib.dump(classifier, os.path.join(args.model_dir, "model.joblib"))
