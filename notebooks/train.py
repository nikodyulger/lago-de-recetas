import os
import argparse
import joblib
import awswrangler as wr

from sklearn.metrics import balanced_accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR")
    )
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST"))

    args, _ = parser.parse_known_args()
    return args


def load_data(s3_path):
    df = wr.s3.read_csv(s3_path)
    X = df["ingredientes_limpios"]
    y = df["encoded_categoria"]
    return X, y


def fit_model(hyperparameters, X_train, y_train, X_test, y_test):

    model = Pipeline(
        [("tfidf", TfidfVectorizer(use_idf=True)), ("clf", SGDClassifier())]
    )
    model.fit(X_train, y_train)

    y_train_pred, y_test_pred = model.predict(X_train), model.predict(X_test)
    bal_acc_train = balanced_accuracy_score(y_train, y_train_pred)
    bal_acc_test = balanced_accuracy_score(y_test, y_test_pred)

    print(f"train_balanced_accuracy: {bal_acc_train:.3f}")
    print(f"test_balanced_accuracy: {bal_acc_test:.3f}")

    return model


def save_model(model_dir, clf):
    path = os.path.join(model_dir, "model.joblib")
    joblib.dump(clf, path)
    print(f"Model saved at {path}")


if __name__ == "__main__":
    args = parse_args()

    X_train, y_train = load_data(args.train)
    X_test, y_test = load_data(args.test)

    clf = fit_model(args, X_train, y_train, X_test, y_test)

    save_model(args.model_dir, clf)
