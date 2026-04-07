import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

conn = sqlite3.connect(DB_PATH)

# tabel tabungan
conn.execute("""
CREATE TABLE IF NOT EXISTS tabungan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    target INTEGER,
    terkumpul INTEGER
)
""")

# tabel riwayat
conn.execute("""
CREATE TABLE IF NOT EXISTS riwayat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabungan_id INTEGER,
    jumlah INTEGER,
    tanggal TEXT
)
""")

conn.close()
print("Database siap & permanen!")