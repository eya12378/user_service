from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest
import os

app = Flask(__name__)

REQS = Counter('http_requests_total', 'Total HTTP requests', ['service'])
SERVICE_NAME = os.getenv('SERVICE_NAME', 'user-service')

@app.route("/")
def root():
    REQS.labels(SERVICE_NAME).inc()
    version = os.getenv("APP_VERSION", "v1.0.0")
    color = os.getenv("COLOR", "blue")  # for blue/green demo
    return jsonify(service=SERVICE_NAME, version=version, color=color, status="ok")

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
