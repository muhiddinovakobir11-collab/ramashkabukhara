import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID") # Bu yozilgandan so'ng, adminga xabarlar yuborilishi mumkin
START_VIDEO_ID = os.getenv("START_VIDEO_ID") # Telegram video file_id
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")
