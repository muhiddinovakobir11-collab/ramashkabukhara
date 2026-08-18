import sqlite3
conn = sqlite3.connect('kindergarten.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM settings WHERE key LIKE 'late_btn_%'")
print(cursor.fetchall())
conn.close()
