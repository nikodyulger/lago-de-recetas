import os
import json
import flask

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from src.inference import load_model_and_encoder, predict


app = Flask(__name__)

# Load the model by reading the `SM_MODEL_DIR` environment variable
# which is passed to the container by SageMaker (usually /opt/ml/model).
model, label_encoder = load_model_and_encoder(os.getenv("SM_MODEL_DIR"))

# Since the web application runs behind a proxy (nginx), we need to
# add this setting to our app.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


@app.route("/ping", methods=["GET"])
def ping():
    """
    Healthcheck function.
    """
    health = model is not None and label_encoder is not None
    status = 200 if health else 404
    return flask.Response(response="\n", status=status, mimetype="application/json")


@app.route("/invocations", methods=["POST"])
def invocations():
    """
    Function which responds to the API invocations requests.
    """
    body = flask.request.get_json()
    result = predict(body, model, label_encoder)
    return flask.Response(
        response=json.dumps(result), status=200, mimetype="application/json"
    )
