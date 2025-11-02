from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.get("/")
def home():
    return "Group Study Scheduler — it works!"

@app.get("/health")
def health():
    # simple 200 OK for container health checks
    return "OK", 200

@app.get("/version")
def version():
    # optional: shows build tag from env (e.g., set by Jenkins)
    return jsonify(version=os.getenv("BUILD_TAG", "unknown"))

if __name__ == "__main__":
    # ensure it binds correctly in Docker/EC2
    app.run(host="0.0.0.0", port=8000)
