import re

with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
_settings_cache = {}

async def get_setting(key: str, default_value: str = "") -> str:
    if key in _settings_cache:
        return _settings_cache[key]
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            result = await cursor.fetchone()
        if result:
            _settings_cache[key] = result[0]
            return result[0]
        return default_value

async def set_setting(key: str, value: str):
    _settings_cache[key] = value
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO settings (key, value) 
            VALUES (?, ?) 
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        await db.commit()
'''

content = re.sub(
    r'async def get_setting.*?await db\.commit\(\)', 
    replacement.strip(), 
    content, 
    flags=re.DOTALL
)

with open('database.py', 'w', encoding='utf-8') as f:
    f.write(content)
