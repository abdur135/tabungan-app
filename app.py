from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DB =================
def get_db():
    return sqlite3.connect("database.db")


# ================= HELPER =================
def bersihin_angka(angka):
    return int(angka.replace(".", ""))


# ================= AUTH =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cur.fetchone()

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
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
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
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM tabungan WHERE user_id=?",
        (session["user_id"],)
    )
    data = cur.fetchall()

    conn.close()
    return render_template("index.html", tabungan=data)


# ================= TAMBAH =================
@app.route("/tambah", methods=["POST"])
def tambah():
    if "user_id" not in session:
        return redirect("/login")

    nama = request.form["nama"]
    target = bersihin_angka(request.form["target"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tabungan (nama, target, terkumpul, user_id) VALUES (?, ?, 0, ?)",
        (nama, target, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ================= NABUNG =================
@app.route("/nabung/<int:id>", methods=["POST"])
def nabung(id):
    jumlah = bersihin_angka(request.form["jumlah"])

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


# ================= KURANG =================
@app.route("/kurang/<int:id>", methods=["POST"])
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


# ================= HAPUS =================
@app.route("/hapus/<int:id>")
def hapus(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM tabungan WHERE id=?", (id,))
    cur.execute("DELETE FROM riwayat WHERE tabungan_id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")


# ================= RIWAYAT =================
@app.route("/riwayat/<int:id>")
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


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)