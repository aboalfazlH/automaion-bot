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

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.post("/webhook")
def webhook():
    """
    Webhook endpoint to receive updates from Bale.
    Forwards text messages and attached files to Rubika & Eitaa.
    """

    update = request.json
    message = bot.parse_update(update)

    if not message:
        return {"ok": True}

    text_to_forward = message.text or ""

    files_to_send = []

    if message.photo:
        for photo in message.photo:
            file_path = bot.download_file_sync(photo.file_id, DOWNLOAD_DIR)
            files_to_send.append(file_path)

    if message.document:
        file_path = bot.download_file_sync(message.document.file_id, DOWNLOAD_DIR)
        files_to_send.append(file_path)

    if message.video:
        file_path = bot.download_file_sync(message.video.file_id, DOWNLOAD_DIR)
        files_to_send.append(file_path)

    if message.voice:
        file_path = bot.download_file_sync(message.voice.file_id, DOWNLOAD_DIR)
        files_to_send.append(file_path)

    if message.sticker:
        file_path = bot.download_file_sync(message.sticker.file_id, DOWNLOAD_DIR)
        files_to_send.append(file_path)

    for fpath in files_to_send:
        with open(fpath, "rb") as f:
            requests.post(
                f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendFile",
                files={"file": f},
                data={"chat_id": RUBIKA_CHAT_ID, "caption": text_to_forward}
            )
        os.remove(fpath)

    if text_to_forward and not files_to_send:
        requests.post(
            f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendMessage",
            json={"chat_id": RUBIKA_CHAT_ID, "text": text_to_forward}
        )

    for fpath in files_to_send:
        with open(fpath, "rb") as f:
            requests.post(
                f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendFile",
                files={"file": f},
                data={"chat_id": EITAA_CHANNEL, "caption": text_to_forward}
            )
        if os.path.exists(fpath):
            os.remove(fpath)

    if text_to_forward and not files_to_send:
        requests.get(
            f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage?chat_id={EITAA_CHANNEL}&text={text_to_forward}&date=0&pin=off"
        )

    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
