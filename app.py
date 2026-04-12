from flask import Flask
from routes.auth import auth_bp
from routes.tabungan import tabungan_bp

app = Flask(__name__)
app.secret_key = "secret123"

# daftar blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(tabungan_bp)

if __name__ == "__main__":
    app.run(debug=True)