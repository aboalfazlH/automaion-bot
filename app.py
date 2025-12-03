from flask import Flask, request
from balethon import Client
from dotenv import load_dotenv
import os
import requests

load_dotenv(".env")

app = Flask(__name__)
bot = Client(os.getenv("BALE_TOKEN"))

RUBIKA_CHAT_ID = os.getenv("RUBIKA_CHAT_ID")
EITAA_CHANNEL = os.getenv("EITAA_CHANNEL")
RUBIKA_TOKEN = os.getenv("RUBIKA_TOKEN")
EITAA_TOKEN = os.getenv("EITAA_TOKEN")


@app.post("/webhook/", strict_slashes=False)
def webhook():
    update = request.json
    message = update.get("message")
    if not message:
        return {"ok": True}

    text_to_forward = message.get("text")
    if not text_to_forward:
        return {"ok": True}

    requests.post(
        f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendMessage",
        json={"chat_id": RUBIKA_CHAT_ID, "text": text_to_forward}
    )

    requests.get(
        f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage?chat_id={EITAA_CHANNEL}&text={text_to_forward}&date=0&pin=off"
    )

    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
