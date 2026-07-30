import sqlite3
import json
from typing import List, Tuple

DB_NAME = "kindergarten.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gallery_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            media_type TEXT,
            media_id TEXT,
            caption TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            currency TEXT,
            payload TEXT,
            provider_payment_charge_id TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str, full_name: str) -> bool:
    """
    Foydalanuvchini bazaga qo'shadi. Agar u yangi bo'lsa True, oldin bor bo'lsa False qaytaradi.
    Shuningdek, foydalanuvchi qayta start bossa is_active = 1 qilib qo'yadi.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user is None:
        cursor.execute(
            "INSERT INTO users (user_id, username, full_name, is_active) VALUES (?, ?, ?, 1)",
            (user_id, username, full_name)
        )
        conn.commit()
        conn.close()
        return True
    else:
        cursor.execute("UPDATE users SET is_active = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return False

def update_user_status(user_id: int, is_active: bool):
    """
    Foydalanuvchi botni bloklagan (yoki unblock qilgan) bo'lsa statusni o'zgartiradi.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (int(is_active), user_id))
    conn.commit()
    conn.close()

def get_all_users() -> List[Tuple]:
    """
    Barcha foydalanuvchilarni qaytaradi.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, full_name, is_active FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_setting(key: str, default_value: str = "") -> str:
    """
    Ma'lumotlar bazasidan berilgan kalit bo'yicha matnni oladi.
    Agar topilmasa default_value ni qaytaradi.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return default_value

def set_setting(key: str, value: str):
    """
    Ma'lumotlar bazasiga sozlamani (yoki matnni) saqlaydi yoki yangilaydi.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (key, value) 
        VALUES (?, ?) 
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()

def set_setting_media(key: str, media_type: str, media_id: str, text: str):
    data = {"type": media_type, "media_id": media_id, "text": text}
    set_setting(key, json.dumps(data))

def get_setting_media(key: str, default_text: str = "") -> dict:
    val = get_setting(key, "")
    if not val:
        return {"type": "text", "media_id": None, "text": default_text}
    try:
        data = json.loads(val)
        return data
    except json.JSONDecodeError:
        # Eski matn formatini qo'llab-quvvatlash
        return {"type": "text", "media_id": None, "text": val}

def add_gallery_media(category: str, media_type: str, media_id: str, caption: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO gallery_media (category, media_type, media_id, caption) 
        VALUES (?, ?, ?, ?)
    """, (category, media_type, media_id, caption))
    conn.commit()
    conn.close()

def get_gallery_media(category: str, media_type: str) -> List[Tuple]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, media_id, caption FROM gallery_media 
        WHERE category = ? AND media_type = ?
        ORDER BY id ASC
    """, (category, media_type))
    media = cursor.fetchall()
    conn.close()
    return media

def delete_gallery_media(media_db_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gallery_media WHERE id = ?", (media_db_id,))
    conn.commit()
    conn.close()

def add_payment(user_id: int, amount: int, currency: str, payload: str, provider_payment_charge_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payments (user_id, amount, currency, payload, provider_payment_charge_id)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, currency, payload, provider_payment_charge_id))
    conn.commit()
    conn.close()
