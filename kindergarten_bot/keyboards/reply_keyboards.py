from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import ADMIN_ID
from aiogram.types import WebAppInfo

def main_menu(user_id: int):
    webapp_url = "https://ramashkabukhara.onrender.com/webapp"
    buttons = [
        [KeyboardButton(text="📱 Asosiy Menyuni Ochish", web_app=WebAppInfo(url=webapp_url))]
    ]
    if str(user_id) == str(ADMIN_ID):
        buttons.append([KeyboardButton(text="👥 Foydalanuvchilar")])
        buttons.append([KeyboardButton(text="👨‍💻 Admin Panel (Eski usul)")])
        
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

def contact_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)],
            [KeyboardButton(text="⬅️ Bekor qilish")]
        ],
        resize_keyboard=True
    )
    return keyboard

def cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Bekor qilish")]
        ],
        resize_keyboard=True
    )
    return keyboard
