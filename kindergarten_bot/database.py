import sqlite3
import json

DB_NAME = "database.db"

async def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gallery_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT,
            media_type TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS educators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            educator_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

async def get_setting(key: str, default: str = "") -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key=?', (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default

async def set_setting(key: str, value: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

async def get_setting_media(key: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key=?', (key,))
    result = cursor.fetchone()
    conn.close()
    if result:
        try:
            return json.loads(result[0])
        except:
            return None
    return None

async def set_setting_media(key: str, file_id: str, media_type: str, caption: str = ""):
    data = json.dumps({"file_id": file_id, "media_type": media_type, "caption": caption})
    await set_setting(key, data)

async def add_gallery_media(file_id: str, media_type: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO gallery_media (file_id, media_type) VALUES (?, ?)', (file_id, media_type))
    conn.commit()
    conn.close()

async def get_all_gallery_media():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, file_id, media_type FROM gallery_media')
    results = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "file_id": r[1], "media_type": r[2]} for r in results]

async def delete_gallery_media(media_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gallery_media WHERE id=?', (media_id,))
    conn.commit()
    conn.close()

async def get_all_educators():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, group_name, educator_id FROM educators')
    results = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "group_name": r[1], "educator_id": r[2]} for r in results]

async def get_educator(educator_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, group_name, educator_id FROM educators WHERE id=?', (educator_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"id": result[0], "group_name": result[1], "educator_id": result[2]}
    return None

async def add_educator(group_name: str, educator_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO educators (group_name, educator_id) VALUES (?, ?)', (group_name, educator_id))
    conn.commit()
    conn.close()

async def delete_educator(db_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM educators WHERE id=?', (db_id,))
    conn.commit()
    conn.close()
