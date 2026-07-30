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
            is_active BOOLEAN DEFAULT 1,
            phone TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    # Eski bazani yangilash uchun try-except ishlatamiz
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'pending'")
    except sqlite3.OperationalError:
        pass # Ustunlar allaqachon bor bo'lsa xato bermasligi uchun
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY,
            name TEXT,
            url TEXT,
            is_active BOOLEAN DEFAULT 0
        )
    """)
    # Insert 10 default cameras if not exists
    cursor.execute("SELECT count(*) FROM cameras")
    if cursor.fetchone()[0] == 0:
        for i in range(1, 11):
            cursor.execute("INSERT INTO cameras (id, name, url, is_active) VALUES (?, ?, ?, 0)", (i, f"Kamera {i}", ""))
            
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT
        )
    """)
    # Insert default FAQs if empty
    cursor.execute("SELECT count(*) FROM faqs")
    if cursor.fetchone()[0] == 0:
        default_faqs = [
            ("Qabul yoshi necha?", "Biz 2 yoshdan 7 yoshgacha bo'lgan bolalarni qabul qilamiz."),
            ("Bog'cha qaysi kunlari ishlaydi?", "Dushanbadan Juma kunigacha, soat 08:00 dan 18:00 gacha."),
            ("Qanday hujjatlar kerak?", "Bola metrikasi, ota-ona pasport nusxasi va tibbiy ma'lumotnoma (086-forma).")
        ]
        for q, a in default_faqs:
            cursor.execute("INSERT INTO faqs (question, answer) VALUES (?, ?)", (q, a))
            
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str, full_name: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user is None:
        from config import ADMIN_ID
        status = 'approved' if str(user_id) == str(ADMIN_ID) else 'pending'
        cursor.execute(
            "INSERT INTO users (user_id, username, full_name, is_active, status) VALUES (?, ?, ?, 1, ?)",
            (user_id, username, full_name, status)
        )
        conn.commit()
        conn.close()
        return True
    else:
        cursor.execute("UPDATE users SET is_active = 1 WHERE user_id = ?", (user_id,))
        # Adminni avtomatik tasdiqlash uchun kafolat
        from config import ADMIN_ID
        if ADMIN_ID and str(user_id) == str(ADMIN_ID):
            cursor.execute("UPDATE users SET status = 'approved' WHERE user_id = ?", (user_id,))
            
        conn.commit()
        conn.close()
        return False

def get_user(user_id: int) -> dict:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, full_name, is_active, phone, status FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0], "username": row[1], "full_name": row[2],
            "is_active": row[3], "phone": row[4], "status": row[5] or 'pending'
        }
    return None

def update_user_auth_status(user_id: int, status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
    conn.commit()
    conn.close()

def update_user_info(user_id: int, full_name: str, phone: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET full_name = ?, phone = ? WHERE user_id = ?", (full_name, phone, user_id))
    conn.commit()
    conn.close()

def get_users_by_status(status: str = 'approved') -> list:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, full_name, is_active, phone FROM users WHERE status = ?", (status,))
    rows = cursor.fetchall()
    conn.close()
    users = []
    for row in rows:
        users.append({
            "user_id": row[0],
            "username": row[1],
            "full_name": row[2],
            "is_active": row[3],
            "phone": row[4]
        })
    return users

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

def get_all_cameras() -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url, is_active FROM cameras ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "url": r[2], "is_active": bool(r[3])} for r in rows]

def get_active_cameras() -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url, is_active FROM cameras WHERE is_active = 1 ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "url": r[2], "is_active": bool(r[3])} for r in rows]

def get_camera(camera_id: int) -> dict:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url, is_active FROM cameras WHERE id = ?", (camera_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "url": row[2], "is_active": bool(row[3])}
    return None

def update_camera_url(camera_id: int, url: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE cameras SET url = ? WHERE id = ?", (url, camera_id))
    conn.commit()
    conn.close()

def toggle_camera_status(camera_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE cameras SET is_active = NOT is_active WHERE id = ?", (camera_id,))
    conn.commit()
    conn.close()

def get_all_faqs() -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer FROM faqs ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "question": r[1], "answer": r[2]} for r in rows]

def get_faq(faq_id: int) -> dict:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer FROM faqs WHERE id = ?", (faq_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "question": row[1], "answer": row[2]}
    return None

def add_faq(question: str, answer: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faqs (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

def delete_faq(faq_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
    conn.commit()
    conn.close()
