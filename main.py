from flask import Flask, request, Response
from cryptography.fernet import Fernet
import os
import requests

app = Flask(__name__)

FERNET_KEY = os.getenv("FERNET_KEY")
GITHUB_USERS = os.getenv("GITHUB_USERS", "").split(",")

cipher = Fernet(FERNET_KEY.encode())


@app.route("/")
def home():
    return {"status": "running"}


@app.route("/decrypt", methods=["POST"])
def decrypt_file():
    auth = request.headers.get("Authorization")
    if not auth:
        return {"error": "Missing token"}, 401

    token = auth.replace("Bearer ", "")

    user = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {token}"}
    )

    if user.status_code != 200:
        return {"error": "invalid token"}, 403

    username = user.json()["login"]
    if username not in GITHUB_USERS:
        return {"error": "Subscription inactive"}, 403

    file = request.files["file"]
    lines = file.read().decode("utf-8").splitlines()

    output = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            output.append(cipher.decrypt(line.encode()).decode())
        except:
            pass

    return Response("\n".join(output), mimetype="text/plain")
