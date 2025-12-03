import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")
BALE_TOKEN = os.getenv("BALE_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

res = requests.post(
    f"https://tapi.bale.ai/bot{BALE_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)
print(res.json())
