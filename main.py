from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import PlainTextResponse
from cryptography.fernet import Fernet
import os
import requests

app = FastAPI()

# السر بيتاخد من Render مش من الكود
FERNET_KEY = os.getenv("FERNET_KEY")
GITHUB_USERS = os.getenv("GITHUB_USERS", "").split(",")

if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY is missing")

cipher = Fernet(FERNET_KEY.encode())


def verify_user(token: str):
    user = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {token}"}
    )

    if user.status_code != 200:
        return None

    username = user.json()["login"]

    if username not in GITHUB_USERS:
        return None

    return username


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/decrypt")
async def decrypt_file(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(401, "Missing token")

    token = authorization.replace("Bearer ", "")
    user = verify_user(token)

    if not user:
        raise HTTPException(403, "Subscription inactive")

    content = await file.read()
    lines = content.decode("utf-8").splitlines()

    output = []
    errors = []

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        try:
            text = cipher.decrypt(line.encode()).decode(errors="ignore")
            output.append(text)
        except Exception as e:
            errors.append(f"Line {i}: {str(e)}")

    return PlainTextResponse("\n".join(output))
