import aiosqlite
import json
from typing import List, Tuple

DB_NAME = "kindergarten.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS educators (id INTEGER PRIMARY KEY AUTOINCREMENT, group_name TEXT, educator_id TEXT)''')
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                phone TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        # Eski bazani yangilash uchun
        try:
            await db.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        except:
            pass
        try:
            await db.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'pending'")
        except:
            pass

        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS gallery_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                media_type TEXT,
                media_id TEXT,
                caption TEXT
            )
        """)
        await db.execute("""
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY,
                name TEXT,
                url TEXT,
                is_active BOOLEAN DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_messages (
                broadcast_id INTEGER,
                user_id INTEGER,
                message_id INTEGER,
                FOREIGN KEY(broadcast_id) REFERENCES broadcasts(id)
            )
        """)
        async with db.execute("SELECT count(*) FROM cameras") as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                for i in range(1, 11):
                    await db.execute("INSERT INTO cameras (id, name, url, is_active) VALUES (?, ?, ?, 0)", (i, f"Kamera {i}", ""))
                
        await db.execute("""
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT
            )
        """)
        async with db.execute("SELECT count(*) FROM faqs") as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                default_faqs = [
                    ("Qabul yoshi necha?", "Biz 2 yoshdan 7 yoshgacha bo'lgan bolalarni qabul qilamiz."),
                    ("Bog'cha qaysi kunlari ishlaydi?", "Dushanbadan Juma kunigacha, soat 08:00 dan 18:00 gacha."),
                    ("Qanday hujjatlar kerak?", "Bola metrikasi, ota-ona pasport nusxasi va tibbiy ma'lumotnoma (086-forma).")
                ]
                for q, a in default_faqs:
                    await db.execute("INSERT INTO faqs (question, answer) VALUES (?, ?)", (q, a))
                
        await db.commit()

async def add_user(user_id: int, username: str, full_name: str) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
        
        if user is None:
            from config import ADMIN_ID
            status = 'approved' if str(user_id) == str(ADMIN_ID) else 'pending'
            await db.execute(
                "INSERT INTO users (user_id, username, full_name, is_active, status) VALUES (?, ?, ?, 1, ?)",
                (user_id, username, full_name, status)
            )
            await db.commit()
            return True
        else:
            await db.execute("UPDATE users SET is_active = 1 WHERE user_id = ?", (user_id,))
            from config import ADMIN_ID
            if ADMIN_ID and str(user_id) == str(ADMIN_ID):
                await db.execute("UPDATE users SET status = 'approved' WHERE user_id = ?", (user_id,))
            await db.commit()
            return False

async def get_user(user_id: int) -> dict:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username, full_name, is_active, phone, status FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
        if row:
            return {
                "user_id": row[0], "username": row[1], "full_name": row[2],
                "is_active": row[3], "phone": row[4], "status": row[5] or 'pending'
            }
        return None

async def update_user_auth_status(user_id: int, status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
        await db.commit()

async def update_user_info(user_id: int, full_name: str, phone: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET full_name = ?, phone = ? WHERE user_id = ?", (full_name, phone, user_id))
        await db.commit()

async def get_users_by_status(status: str = 'approved') -> list:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username, full_name, is_active, phone FROM users WHERE status = ?", (status,)) as cursor:
            rows = await cursor.fetchall()
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

async def update_user_status(user_id: int, is_active: bool):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (int(is_active), user_id))
        await db.commit()

async def get_all_users() -> List[Tuple]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username, full_name, is_active FROM users") as cursor:
            users = await cursor.fetchall()
        return users

async def get_setting(key: str, default_value: str = "") -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            result = await cursor.fetchone()
        if result:
            return result[0]
        return default_value

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO settings (key, value) 
            VALUES (?, ?) 
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        await db.commit()

async def set_setting_media(key: str, media_type: str, media_id: str, text: str):
    data = {"type": media_type, "media_id": media_id, "text": text}
    await set_setting(key, json.dumps(data))

async def get_setting_media(key: str, default_text: str = "") -> dict:
    val = await get_setting(key, "")
    if not val:
        return {"type": "text", "media_id": None, "text": default_text}
    try:
        data = json.loads(val)
        return data
    except json.JSONDecodeError:
        return {"type": "text", "media_id": None, "text": val}

async def add_gallery_media(category: str, media_type: str, media_id: str, caption: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO gallery_media (category, media_type, media_id, caption) 
            VALUES (?, ?, ?, ?)
        """, (category, media_type, media_id, caption))
        await db.commit()

async def get_gallery_media(category: str, media_type: str) -> List[Tuple]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT id, media_id, caption FROM gallery_media 
            WHERE category = ? AND media_type = ?
            ORDER BY id ASC
        """, (category, media_type)) as cursor:
            media = await cursor.fetchall()
        return media

async def delete_gallery_media(media_db_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM gallery_media WHERE id = ?", (media_db_id,))
        await db.commit()

async def add_payment(user_id: int, amount: int, currency: str, payload: str, provider_payment_charge_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO payments (user_id, amount, currency, payload, provider_payment_charge_id)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, currency, payload, provider_payment_charge_id))
        await db.commit()

async def get_all_cameras() -> List[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, name, url, is_active FROM cameras ORDER BY id ASC") as cursor:
            rows = await cursor.fetchall()
        return [{"id": r[0], "name": r[1], "url": r[2], "is_active": bool(r[3])} for r in rows]

async def get_active_cameras() -> List[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, name, url, is_active FROM cameras WHERE is_active = 1 ORDER BY id ASC") as cursor:
            rows = await cursor.fetchall()
        return [{"id": r[0], "name": r[1], "url": r[2], "is_active": bool(r[3])} for r in rows]

async def get_camera(camera_id: int) -> dict:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, name, url, is_active FROM cameras WHERE id = ?", (camera_id,)) as cursor:
            row = await cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "url": row[2], "is_active": bool(row[3])}
        return None

async def update_camera_url(camera_id: int, url: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE cameras SET url = ? WHERE id = ?", (url, camera_id))
        await db.commit()

async def toggle_camera_status(camera_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE cameras SET is_active = NOT is_active WHERE id = ?", (camera_id,))
        await db.commit()

async def get_all_faqs() -> List[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, question, answer FROM faqs ORDER BY id ASC") as cursor:
            rows = await cursor.fetchall()
        return [{"id": r[0], "question": r[1], "answer": r[2]} for r in rows]

async def get_faq(faq_id: int) -> dict:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, question, answer FROM faqs WHERE id = ?", (faq_id,)) as cursor:
            row = await cursor.fetchone()
        if row:
            return {"id": row[0], "question": row[1], "answer": row[2]}
        return None

async def add_faq(question: str, answer: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO faqs (question, answer) VALUES (?, ?)", (question, answer))
        await db.commit()

async def delete_faq(faq_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
        await db.commit()

async def create_broadcast() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("INSERT INTO broadcasts DEFAULT VALUES")
        await db.commit()
        return cursor.lastrowid

async def add_broadcast_message(broadcast_id: int, user_id: int, message_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO broadcast_messages (broadcast_id, user_id, message_id) VALUES (?, ?, ?)",
            (broadcast_id, user_id, message_id)
        )
        await db.commit()

async def get_broadcast_messages(broadcast_id: int) -> List[Tuple[int, int]]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT user_id, message_id FROM broadcast_messages WHERE broadcast_id = ?", 
            (broadcast_id,)
        ) as cursor:
            rows = await cursor.fetchall()
        return rows

async def get_latest_broadcast_id() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id FROM broadcasts ORDER BY id DESC LIMIT 1") as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            return None


async def get_all_educators():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT id, group_name, educator_id FROM educators') as cursor:
            results = await cursor.fetchall()
            return [{"id": r[0], "group_name": r[1], "educator_id": r[2]} for r in results]

async def get_educator(educator_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT id, group_name, educator_id FROM educators WHERE id=?', (educator_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                return {"id": result[0], "group_name": result[1], "educator_id": result[2]}
            return None

async def add_educator(group_name: str, educator_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO educators (group_name, educator_id) VALUES (?, ?)', (group_name, educator_id))
        await db.commit()

async def delete_educator(db_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM educators WHERE id=?', (db_id,))
        await db.commit()
