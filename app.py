from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import os

app = Flask(__name__)

REQS = Counter('http_requests_total', 'Total HTTP requests', ['service'])
SERVICE_NAME = os.getenv('SERVICE_NAME', 'user_service')

@app.route("/")
def root():
    REQS.labels(SERVICE_NAME).inc()
    version = os.getenv("APP_VERSION", "v1.0.0")
    color = os.getenv("COLOR", "blue")
    return jsonify(service=SERVICE_NAME, version=version, color=color, status="ok")

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
