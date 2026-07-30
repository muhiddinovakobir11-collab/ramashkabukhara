import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = str(os.getenv("ADMIN_ID")).strip() if os.getenv("ADMIN_ID") else None # Bu yozilgandan so'ng, adminga xabarlar yuborilishi mumkin
START_VIDEO_ID = str(os.getenv("START_VIDEO_ID")).strip() if os.getenv("START_VIDEO_ID") else None # Telegram video file_id
PAYMENT_PROVIDER_TOKEN = str(os.getenv("PAYMENT_PROVIDER_TOKEN")).strip() if os.getenv("PAYMENT_PROVIDER_TOKEN") else None
