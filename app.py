from flask import Flask, jsonify, render_template, request, redirect, make_response
import bcrypt, re, hashlib, requests, secrets, string, datetime, jwt
from database import get_db, create_table
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = "super_secret_key_123"

create_table()

# ---------- PASSWORD STRENGTH ----------
def check_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"\d", password): score += 1
    if re.search(r"[!@#$%^&*()]", password): score += 1

    levels = ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"]
    return levels[score-1] if score else "Very Weak"

# ---------- BREACH CHECK ----------
def is_breached(password):
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
    return suffix in res.text

# ---------- PASSWORD GENERATOR ----------
def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    while True:
        pwd = "".join(secrets.choice(chars) for _ in range(14))
        if check_strength(pwd) in ["Strong", "Very Strong"] and not is_breached(pwd):
            return pwd

# ---------- JWT DECORATOR ----------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect("/")

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except:
            return redirect("/")

        return f(data["user"])
    return decorated

# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate-password")
def generate_password_api():
    return jsonify({"password": generate_password()})

# ---------- REGISTER ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if is_breached(password):
        return jsonify({"error": "Password found in breach"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db = get_db()

    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?,?)",
            (username, hashed)
        )
        db.commit()
    except:
        return jsonify({"error": "Username already exists"}), 400

    return jsonify({"message": "Registered successfully"})

# ---------- LOGIN (UPDATED) ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 401

    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        token = jwt.encode(
            {
                "user": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        response = make_response(jsonify({"redirect": "/loading"}))
        response.set_cookie("token", token, httponly=True)
        return response

    return jsonify({"error": "Invalid credentials"}), 401

# ---------- LOADING PAGE ----------
@app.route("/loading")
def loading():
    return render_template("loading.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
@token_required
def dashboard(username):
    return render_template("dashboard.html", user=username)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    response = redirect("/")
    response.set_cookie("token", "", expires=0)
    return response

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)
