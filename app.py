from flask import Flask, render_template, request, redirect, session
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DB =================
def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tabungan (
        id SERIAL PRIMARY KEY,
        nama TEXT,
        target INTEGER,
        terkumpul INTEGER,
        user_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS riwayat (
        id SERIAL PRIMARY KEY,
        tabungan_id INTEGER,
        jumlah INTEGER,
        tanggal TEXT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()

# ================= AUTH =================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Login gagal!"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
        except:
            return "Username sudah ada!"

        cur.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= MAIN =================

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM tabungan WHERE user_id=%s",
        (session["user_id"],)
    )
    tabungan = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", tabungan=tabungan)

def bersihin_angka(angka):
    return int(angka.replace(".", ""))

# tambah tabungan
@app.route("/tambah", methods=["POST"])
def tambah():
    if "user_id" not in session:
        return redirect("/login")

    nama = request.form["nama"]
    target = bersihin_angka(request.form["target"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tabungan (nama, target, terkumpul, user_id) VALUES (%s, %s, 0, %s)",
        (nama, int(target), session["user_id"])
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

@app.route("/kurang/<int:id>", methods=["POST"])
def kurang(id):
    jumlah = bersihin_angka(request.form["jumlah"])

    conn = get_db()
    cur = conn.cursor()

    # ambil saldo sekarang
    cur.execute("SELECT terkumpul FROM tabungan WHERE id=%s", (id,))
    sekarang = cur.fetchone()[0]

    # biar gak minus
    if sekarang - jumlah < 0:
        jumlah = sekarang

    cur.execute(
        "UPDATE tabungan SET terkumpul = terkumpul - %s WHERE id=%s",
        (jumlah, id)
    )

    # simpan riwayat minus
    cur.execute(
        "INSERT INTO riwayat (tabungan_id, jumlah, tanggal) VALUES (%s, %s, %s)",
        (id, -jumlah, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")


# nabung + riwayat
@app.route("/nabung/<int:id>", methods=["POST"])
def nabung(id):
    jumlah = bersihin_angka(request.form["jumlah"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tabungan SET terkumpul = terkumpul + %s WHERE id=%s",
        (int(jumlah), id)
    )

    cur.execute(
        "INSERT INTO riwayat (tabungan_id, jumlah, tanggal) VALUES (%s, %s, %s)",
        (id, int(jumlah), datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")


# hapus
@app.route("/hapus/<int:id>")
def hapus(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM tabungan WHERE id=%s", (id,))
    cur.execute("DELETE FROM riwayat WHERE tabungan_id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")


# riwayat
@app.route("/riwayat/<int:id>")
def riwayat(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tabungan WHERE id=%s", (id,))
    tabungan = cur.fetchone()

    cur.execute(
        "SELECT * FROM riwayat WHERE tabungan_id=%s ORDER BY tanggal DESC",
        (id,)
    )
    riwayat = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("riwayat.html", tabungan=tabungan, riwayat=riwayat)

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)