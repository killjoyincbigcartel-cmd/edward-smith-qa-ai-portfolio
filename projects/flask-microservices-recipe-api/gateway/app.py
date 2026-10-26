import os

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["USERS_SERVICE_URL"] = os.getenv("USERS_SERVICE_URL", "http://127.0.0.1:5001")
    app.config["RECIPES_SERVICE_URL"] = os.getenv("RECIPES_SERVICE_URL", "http://127.0.0.1:5002")
    if test_config:
        app.config.update(test_config)

    def proxy(base_url, path):
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            upstream = requests.request(
                method=request.method,
                url=url,
                params=request.args,
                data=request.get_data(),
                headers={
                    key: value
                    for key, value in request.headers
                    if key.lower() in {"authorization", "content-type", "accept"}
                },
                timeout=5,
            )
        except requests.RequestException:
            return jsonify(error="Upstream service unavailable"), 502
        excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
        headers = [(k, v) for k, v in upstream.headers.items() if k.lower() not in excluded]
        return Response(upstream.content, status=upstream.status_code, headers=headers)

    @app.get("/health")
    def health():
        return jsonify(service="gateway", status="ok"), 200

    @app.route("/api/auth/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def auth_proxy(path):
        return proxy(app.config["USERS_SERVICE_URL"], f"api/auth/{path}")

    @app.route("/api/recipes", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    @app.route("/api/recipes/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def recipes_proxy(path):
        suffix = f"api/recipes/{path}" if path else "api/recipes"
        return proxy(app.config["RECIPES_SERVICE_URL"], suffix)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
