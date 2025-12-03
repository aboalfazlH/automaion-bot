from io import BytesIO
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


@app.post("/webhook/")
def webhook():
    """
    Webhook endpoint to receive updates from Bale.
    Forwards text messages and attached files to Rubika & Eitaa.
    """
    update = request.json
    message = update.get("message")

    if not message:
        return {"ok": True}

    text_to_forward = message.get("text", "")
    files_to_send = []

    # Handle photo
    if "photo" in message:
        for photo in message["photo"]:
            file_bytes = bot.download_file(photo["file_id"])
            files_to_send.append(("photo.jpg", BytesIO(file_bytes)))

    if "document" in message:
        doc = message["document"]
        file_bytes = bot.download_file(doc["file_id"])
        files_to_send.append((doc.get("file_name", "document"), BytesIO(file_bytes)))

    if "video" in message:
        video = message["video"]
        file_bytes = bot.download_file(video["file_id"])
        files_to_send.append(("video.mp4", BytesIO(file_bytes)))

    if "voice" in message:
        voice = message["voice"]
        file_bytes = bot.download_file(voice["file_id"])
        files_to_send.append(("voice.ogg", BytesIO(file_bytes)))

    if "sticker" in message:
        sticker = message["sticker"]
        file_bytes = bot.download_file(sticker["file_id"])
        files_to_send.append(("sticker.webp", BytesIO(file_bytes)))

    for filename, file_stream in files_to_send:
        requests.post(
            f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendFile",
            files={"file": (filename, file_stream)},
            data={"chat_id": RUBIKA_CHAT_ID, "caption": text_to_forward}
        )

    for filename, file_stream in files_to_send:
        requests.post(
            f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendFile",
            files={"file": (filename, file_stream)},
            data={"chat_id": EITAA_CHANNEL, "caption": text_to_forward}
        )

    if text_to_forward and not files_to_send:
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
