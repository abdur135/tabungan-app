from flask import Blueprint, render_template, request, redirect, session
from models import get_db
from datetime import datetime

tabungan_bp = Blueprint("tabungan", __name__)


# HELPER
def bersihin_angka(angka):
    if not angka:
        return 0

    angka = angka.replace("Rp", "")
    angka = angka.replace(".", "")
    angka = angka.replace(" ", "")

    return int(angka)


# INDEX
@tabungan_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM tabungan WHERE user_id=?",
        (session["user_id"],)
    )
    data = cur.fetchall()

    cur.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    )
    user = cur.fetchone()

    conn.close()
    return render_template("index.html", tabungan=data, user=user)


# TAMBAH
@tabungan_bp.route("/tambah", methods=["POST"])
def tambah():
    if "user_id" not in session:
        return redirect("/login")

    nama = request.form.get("nama", "").strip()
    target_input = request.form.get("target", "")
    target = bersihin_angka(target_input)

    # VALIDASI
    if not nama:
        return "Nama tabungan tidak boleh kosong!"

    if target <= 0:
        return "Target harus lebih dari 0!"

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tabungan (nama, target, terkumpul, user_id) VALUES (?, ?, 0, ?)",
        (nama, target, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect("/")


# NABUNG
@tabungan_bp.route("/nabung/<int:id>", methods=["POST"])
def nabung(id):
    jumlah = bersihin_angka(request.form["jumlah"])

    if jumlah <= 0:
        return "Jumlah tidak valid!"

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tabungan SET terkumpul = terkumpul + ? WHERE id=?",
        (jumlah, id)
    )

    cur.execute(
        "INSERT INTO riwayat (tabungan_id, jumlah, tanggal) VALUES (?, ?, ?)",
        (id, jumlah, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    conn.commit()
    conn.close()

    return redirect("/")


# KURANG
@tabungan_bp.route("/kurang/<int:id>", methods=["POST"])
def kurang(id):
    jumlah = bersihin_angka(request.form["jumlah"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT terkumpul FROM tabungan WHERE id=?", (id,))
    sekarang = cur.fetchone()[0]

    if sekarang - jumlah < 0:
        jumlah = sekarang

    cur.execute(
        "UPDATE tabungan SET terkumpul = terkumpul - ? WHERE id=?",
        (jumlah, id)
    )

    cur.execute(
        "INSERT INTO riwayat (tabungan_id, jumlah, tanggal) VALUES (?, ?, ?)",
        (id, -jumlah, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    conn.commit()
    conn.close()

    return redirect("/")


# HAPUS
@tabungan_bp.route("/hapus/<int:id>")
def hapus(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM tabungan WHERE id=?", (id,))
    cur.execute("DELETE FROM riwayat WHERE tabungan_id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")


# RIWAYAT
@tabungan_bp.route("/riwayat/<int:id>")
def riwayat(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tabungan WHERE id=?", (id,))
    tabungan = cur.fetchone()

    cur.execute(
        "SELECT * FROM riwayat WHERE tabungan_id=? ORDER BY tanggal DESC",
        (id,)
    )
    data = cur.fetchall()

    conn.close()

    return render_template("riwayat.html", tabungan=tabungan, riwayat=data)