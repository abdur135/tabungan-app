from flask import Blueprint, render_template, request, redirect, session
from models import get_db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

# LOGIN
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Login gagal!"

    return render_template("login.html")


# REGISTER
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

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


# LOGOUT
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# PROFIL
@auth_bp.route('/profil')
def profil():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    user = c.fetchone()
    conn.close()

    return render_template('profil.html', user=user)


# UBAH USERNAME
@auth_bp.route('/ubah_username', methods=['POST'])
def ubah_username():
    if 'user_id' not in session:
        return redirect('/login')

    username_baru = request.form['username']

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET username=? WHERE id=?",
              (username_baru, session['user_id']))
    conn.commit()
    conn.close()

    return redirect('/profil')


# UBAH PASSWORD
@auth_bp.route('/ubah_password', methods=['POST'])
def ubah_password():
    if 'user_id' not in session:
        return redirect('/login')

    password_baru = generate_password_hash(request.form['password'])

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE id=?",
              (password_baru, session['user_id']))
    conn.commit()
    conn.close()

    return redirect('/profil')