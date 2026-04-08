from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# koneksi DB
def get_db():
    return sqlite3.connect("database.db")

# init DB
def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS tabungan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT,
        target INTEGER,
        terkumpul INTEGER,
        user_id INTEGER
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS riwayat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabungan_id INTEGER,
        jumlah INTEGER,
        tanggal TEXT
    )
    """)

    try:
        conn.execute("ALTER TABLE tabungan ADD COLUMN user_id INTEGER")
    except:
        pass

    conn.commit()
    conn.close()

init_db()

# ================= LOGIN =================

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Login gagal!"

    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username,password) VALUES (?,?)",
                (username,password)
            )
            conn.commit()
        except:
            return "Username sudah ada!"

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
    tabungan = conn.execute(
        "SELECT * FROM tabungan WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("index.html", tabungan=tabungan)


# tambah tabungan
@app.route("/tambah", methods=["POST"])
def tambah():
    if "user_id" not in session:
        return redirect("/login")

    nama = request.form["nama"]
    target = request.form["target"]

    conn = get_db()
    conn.execute(
        "INSERT INTO tabungan (nama,target,terkumpul,user_id) VALUES (?,?,0,?)",
        (nama,int(target),session["user_id"])
    )
    conn.commit()
    conn.close()

    return redirect("/")


# nabung + riwayat
@app.route("/nabung/<int:id>", methods=["POST"])
def nabung(id):
    jumlah = request.form["jumlah"]

    conn = get_db()

    conn.execute(
        "UPDATE tabungan SET terkumpul = terkumpul + ? WHERE id=?",
        (int(jumlah),id)
    )

    conn.execute(
        "INSERT INTO riwayat (tabungan_id,jumlah,tanggal) VALUES (?,?,?)",
        (id,int(jumlah),datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    conn.commit()
    conn.close()

    return redirect("/")


# hapus
@app.route("/hapus/<int:id>")
def hapus(id):
    conn = get_db()
    conn.execute("DELETE FROM tabungan WHERE id=?", (id,))
    conn.execute("DELETE FROM riwayat WHERE tabungan_id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


# riwayat per tabungan
@app.route("/riwayat/<int:id>")
def riwayat(id):
    conn = get_db()

    tabungan = conn.execute(
        "SELECT * FROM tabungan WHERE id=?",(id,)
    ).fetchone()

    riwayat = conn.execute(
        "SELECT * FROM riwayat WHERE tabungan_id=? ORDER BY tanggal DESC",
        (id,)
    ).fetchall()

    conn.close()

    return render_template("riwayat.html", tabungan=tabungan, riwayat=riwayat)


if __name__ == "__main__":
    app.run(debug=True, port=5001)