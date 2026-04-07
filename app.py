from flask import Flask, render_template, request, redirect
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# PATH DATABASE BIAR PERMANEN
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    return sqlite3.connect(DB_PATH)


@app.route("/")
def index():
    conn = get_db()

    tabungan = conn.execute("SELECT * FROM tabungan").fetchall()
    riwayat = conn.execute("SELECT * FROM riwayat ORDER BY tanggal DESC").fetchall()

    conn.close()
    return render_template("index.html", tabungan=tabungan, riwayat=riwayat)


@app.route("/tambah", methods=["POST"])
def tambah():
    nama = request.form.get("nama")
    target = request.form.get("target")

    if not nama or not target:
        return redirect("/")

    conn = get_db()
    conn.execute(
        "INSERT INTO tabungan (nama, target, terkumpul) VALUES (?, ?, 0)",
        (nama, int(target))
    )
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/nabung/<int:id>", methods=["POST"])
def nabung(id):
    jumlah = request.form.get("jumlah")

    if not jumlah:
        return redirect("/")

    conn = get_db()

    # update tabungan
    conn.execute(
        "UPDATE tabungan SET terkumpul = terkumpul + ? WHERE id = ?",
        (int(jumlah), id)
    )

    # simpan riwayat
    conn.execute(
        "INSERT INTO riwayat (tabungan_id, jumlah, tanggal) VALUES (?, ?, ?)",
        (id, int(jumlah), datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/hapus/<int:id>")
def hapus(id):
    conn = get_db()
    conn.execute("DELETE FROM tabungan WHERE id = ?", (id,))
    conn.execute("DELETE FROM riwayat WHERE tabungan_id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=5001)