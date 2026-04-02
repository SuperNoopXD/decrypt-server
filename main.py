from flask import Flask, request, Response
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

FERNET_KEY = os.getenv("FERNET_KEY")

if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY is missing")

cipher = Fernet(FERNET_KEY.encode())


@app.route("/")
def home():
    return {"status": "running"}


@app.route("/decrypt", methods=["POST"])
def decrypt_file():
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
