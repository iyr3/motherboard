import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from functools import wraps
from io import BytesIO
from pathlib import Path

from flask import Flask, g, jsonify, make_response, request, send_file, send_from_directory
from waitress import serve

ROOT = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", ROOT / "data" / "memar.sqlite3"))
SESSION_COOKIE = "memar_session"
SESSION_TTL = 60 * 60 * 24 * 7
PASSWORD_ITERATIONS = 260_000

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


def connect_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=30, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction(connection):
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield
        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise


def initialize_database():
    connection = connect_database()
    try:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS records (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL CHECK (type IN ('cpu', 'ram', 'gpu')),
                name TEXT NOT NULL,
                generation TEXT NOT NULL,
                summary TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                specs_json TEXT NOT NULL DEFAULT '[]',
                use_case TEXT NOT NULL DEFAULT '',
                image TEXT NOT NULL DEFAULT '',
                score INTEGER NOT NULL DEFAULT 2,
                updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                password_algo TEXT NOT NULL DEFAULT 'pbkdf2-sha256',
                role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS sessions_expiry_idx ON sessions(expires_at);
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(users)")}
        if "password_algo" not in columns:
            connection.execute(
                "ALTER TABLE users ADD COLUMN password_algo TEXT NOT NULL DEFAULT 'pbkdf2-sha256'"
            )
    finally:
        connection.close()


initialize_database()


def get_database():
    if "database" not in g:
        g.database = connect_database()
    return g.database


@app.teardown_appcontext
def close_database(_error=None):
    connection = g.pop("database", None)
    if connection is not None:
        connection.close()


def error(message, status):
    return jsonify({"error": message}), status


def public_user(row):
    return {"id": row["id"], "username": row["username"], "role": row["role"]}


def current_user():
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return get_database().execute(
        """SELECT users.id, users.username, users.role
           FROM sessions JOIN users ON users.id = sessions.user_id
           WHERE sessions.token_hash = ? AND sessions.expires_at > ?""",
        (token_hash, int(time.time())),
    ).fetchone()


def require_user(admin=False, owner=False):
    def decorator(handler):
        @wraps(handler)
        def wrapped(*args, **kwargs):
            user = current_user()
            if user is None:
                return error("تسجيل الدخول مطلوب.", 401)
            if admin and user["role"] != "admin":
                return error("هذه العملية متاحة للمدير فقط.", 403)
            if owner and (user["role"] != "admin" or user["username"].casefold() != "iyr3"):
                return error("إدارة الحسابات متاحة للحساب iyr3 فقط.", 403)
            g.current_user = user
            return handler(*args, **kwargs)

        return wrapped

    return decorator


def password_digest(password, salt, algorithm="pbkdf2-sha256"):
    if algorithm == "web-sha256":
        return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PASSWORD_ITERATIONS
    ).hex()


def issue_session(user_id):
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    connection = get_database()
    connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (int(time.time()),))
    connection.execute(
        "INSERT INTO sessions(token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (token_hash, user_id, int(time.time()) + SESSION_TTL),
    )
    return token


def set_session_cookie(response, token):
    secure = request.is_secure or request.headers.get("X-Forwarded-Proto") == "https"
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_TTL,
        httponly=True,
        secure=secure,
        samesite="Lax",
        path="/",
    )
    return response


def record_from_row(row):
    return {
        "id": row["id"],
        "type": row["type"],
        "name": row["name"],
        "generation": row["generation"],
        "summary": row["summary"],
        "details": row["details"],
        "specs": json.loads(row["specs_json"]),
        "use": row["use_case"],
        "image": row["image"],
        "score": row["score"],
    }


def validate_record(item):
    if not isinstance(item, dict):
        raise ValueError("صيغة سجل القطعة غير صحيحة.")
    record_type = item.get("type")
    if record_type not in ("cpu", "ram", "gpu"):
        raise ValueError("نوع المكون غير صحيح.")
    values = {}
    for key, maximum in (("id", 120), ("name", 120), ("generation", 120), ("summary", 500)):
        value = str(item.get(key, "")).strip()
        if not value or len(value) > maximum:
            raise ValueError("تأكد من الاسم والجيل والنبذة ومعرّف السجل.")
        values[key] = value
    specs = item.get("specs", [])
    if not isinstance(specs, list) or len(specs) > 30:
        raise ValueError("قائمة المواصفات غير صحيحة.")
    return {
        **values,
        "type": record_type,
        "details": str(item.get("details", ""))[:5000],
        "specs_json": json.dumps([str(value)[:200] for value in specs], ensure_ascii=False),
        "use_case": str(item.get("use", ""))[:300],
        "image": str(item.get("image", ""))[:1000],
        "score": max(1, min(3, int(item.get("score", 2)))),
        "updated_at": int(time.time()),
    }


def save_record(connection, record):
    connection.execute(
        """INSERT INTO records
           (id, type, name, generation, summary, details, specs_json, use_case, image, score, updated_at)
           VALUES (:id, :type, :name, :generation, :summary, :details, :specs_json, :use_case, :image, :score, :updated_at)
           ON CONFLICT(id) DO UPDATE SET type=excluded.type, name=excluded.name,
           generation=excluded.generation, summary=excluded.summary, details=excluded.details,
           specs_json=excluded.specs_json, use_case=excluded.use_case, image=excluded.image,
           score=excluded.score, updated_at=excluded.updated_at""",
        record,
    )


def validate_backup_user(item):
    username = str(item.get("username", "")).strip()
    salt = str(item.get("salt", ""))
    password_hash = str(item.get("passwordHash", item.get("password_hash", "")))
    password_algorithm = str(item.get("passwordAlgorithm", item.get("password_algo", "pbkdf2-sha256")))
    role = item.get("role")
    if not username or len(username) > 32 or role not in ("admin", "user"):
        raise ValueError("بيانات أحد الحسابات في النسخة الاحتياطية غير صحيحة.")
    if len(salt) != 32 or len(password_hash) != 64:
        raise ValueError("تجزئة كلمة مرور أحد الحسابات غير مكتملة.")
    int(salt, 16)
    int(password_hash, 16)
    if password_algorithm not in ("pbkdf2-sha256", "web-sha256"):
        raise ValueError("خوارزمية كلمة مرور غير مدعومة في النسخة الاحتياطية.")
    return username, password_hash, salt, password_algorithm, role


@app.get("/")
def homepage():
    return send_from_directory(ROOT, "index.html")


@app.get("/motherboards.html")
def motherboards_page():
    return send_from_directory(ROOT, "motherboards.html")


@app.get("/budgets.html")
def budgets_page():
    return send_from_directory(ROOT, "budgets.html")


@app.get("/guides.css")
def guide_stylesheet():
    return send_from_directory(ROOT, "guides.css", mimetype="text/css")


@app.get("/api/records")
def list_records():
    rows = get_database().execute("SELECT * FROM records ORDER BY rowid").fetchall()
    return jsonify([record_from_row(row) for row in rows])


@app.post("/api/admin/seed")
@require_user(admin=True)
def seed_records():
    payload = request.get_json(silent=True) or {}
    incoming = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(incoming, list) or not incoming:
        return error("بيانات التهيئة غير صحيحة.", 400)
    try:
        records = [validate_record(item) for item in incoming]
        connection = get_database()
        with transaction(connection):
            if connection.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 0:
                for record in records:
                    save_record(connection, record)
    except (ValueError, TypeError) as exception:
        return error(str(exception), 400)
    return jsonify({"ok": True})


@app.get("/api/auth/status")
def auth_status():
    user = current_user()
    owner = get_database().execute(
        "SELECT id FROM users WHERE username = 'iyr3' COLLATE NOCASE AND role = 'admin'"
    ).fetchone()
    return jsonify({"user": public_user(user) if user else None, "setupRequired": owner is None})


@app.post("/api/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    if len(username) < 3 or len(username) > 32 or len(password) < 8:
        return error("اسم المستخدم أو كلمة المرور لا يطابق الشروط.", 400)
    salt = secrets.token_hex(16)
    digest = password_digest(password, salt)
    connection = get_database()
    try:
        with transaction(connection):
            owner = connection.execute(
                "SELECT id FROM users WHERE username = 'iyr3' COLLATE NOCASE AND role = 'admin'"
            ).fetchone()
            if owner is None:
                if username.casefold() != "iyr3":
                    return error("اسم حساب المدير الأول يجب أن يكون iyr3.", 403)
                setup_token = os.environ.get("ADMIN_SETUP_TOKEN", "")
                supplied_token = str(payload.get("setupToken", ""))
                if len(setup_token) < 16 or not hmac.compare_digest(setup_token, supplied_token):
                    return error("رمز تهيئة المدير غير مضبوط أو غير صحيح.", 403)
                role = "admin"
            else:
                if username.casefold() == "iyr3":
                    return error("اسم iyr3 محجوز لحساب المالك.", 403)
                role = "user"
            cursor = connection.execute(
                "INSERT INTO users(username, password_hash, salt, password_algo, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (username, digest, salt, "pbkdf2-sha256", role, int(time.time())),
            )
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return error("اسم المستخدم مستخدم بالفعل.", 409)
    token = issue_session(user_id)
    user = connection.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,)).fetchone()
    return set_session_cookie(jsonify({"user": public_user(user)}), token)


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    connection = get_database()
    row = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if row is None or not hmac.compare_digest(
        password_digest(password, row["salt"], row["password_algo"]), row["password_hash"]
    ):
        return error("اسم المستخدم أو كلمة المرور غير صحيحة.", 401)
    if row["password_algo"] == "web-sha256":
        salt = secrets.token_hex(16)
        digest = password_digest(password, salt)
        connection.execute(
            "UPDATE users SET password_hash = ?, salt = ?, password_algo = 'pbkdf2-sha256' WHERE id = ?",
            (digest, salt, row["id"]),
        )
    token = issue_session(row["id"])
    return set_session_cookie(jsonify({"user": public_user(row)}), token)


@app.post("/api/auth/logout")
def logout():
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        get_database().execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
    response = make_response(jsonify({"ok": True}))
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="Lax")
    return response


@app.put("/api/admin/records")
@require_user(admin=True)
def replace_records():
    payload = request.get_json(silent=True) or {}
    incoming = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(incoming, list) or len(incoming) > 5000:
        return error("قائمة القطع غير صحيحة.", 400)
    try:
        records = [validate_record(item) for item in incoming]
        if len({record["id"] for record in records}) != len(records):
            return error("توجد معرّفات مكررة في السجلات.", 400)
        connection = get_database()
        with transaction(connection):
            connection.execute("DELETE FROM records")
            for record in records:
                save_record(connection, record)
    except (ValueError, TypeError) as exception:
        return error(str(exception), 400)
    return jsonify({"ok": True, "count": len(records)})


@app.get("/api/admin/users")
@require_user(admin=True, owner=True)
def list_users():
    rows = get_database().execute("SELECT id, username, role, created_at FROM users ORDER BY id").fetchall()
    return jsonify([
        {"id": row["id"], "username": row["username"], "role": row["role"], "createdAt": row["created_at"]}
        for row in rows
    ])


@app.put("/api/admin/users/<int:user_id>/role")
@require_user(admin=True, owner=True)
def change_user_role(user_id):
    payload = request.get_json(silent=True) or {}
    role = payload.get("role")
    if role not in ("admin", "user"):
        return error("الصلاحية غير صحيحة.", 400)
    if user_id == g.current_user["id"]:
        return error("لا يمكن تغيير صلاحية الحساب الحالي.", 400)
    connection = get_database()
    target = connection.execute("SELECT id, role FROM users WHERE id = ?", (user_id,)).fetchone()
    if target is None:
        return error("الحساب غير موجود.", 404)
    target_name = connection.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()["username"]
    if target_name.casefold() == "iyr3":
        return error("لا يمكن تغيير صلاحية الحساب iyr3.", 400)
    if target["role"] == "admin" and role == "user":
        admins = connection.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]
        if admins <= 1:
            return error("يجب الاحتفاظ بمدير واحد على الأقل.", 400)
    connection.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    return jsonify({"ok": True})


@app.delete("/api/admin/users/<int:user_id>")
@require_user(admin=True, owner=True)
def delete_user(user_id):
    if user_id == g.current_user["id"]:
        return error("لا يمكن حذف الحساب الحالي.", 400)
    connection = get_database()
    target = connection.execute("SELECT id, role FROM users WHERE id = ?", (user_id,)).fetchone()
    if target is None:
        return error("الحساب غير موجود.", 404)
    target_name = connection.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()["username"]
    if target_name.casefold() == "iyr3":
        return error("لا يمكن حذف الحساب iyr3.", 400)
    if target["role"] == "admin":
        admins = connection.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]
        if admins <= 1:
            return error("لا يمكن حذف آخر مدير.", 400)
    connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return jsonify({"ok": True})


@app.get("/api/admin/backup")
@require_user(admin=True, owner=True)
def download_backup():
    connection = get_database()
    records = [record_from_row(row) for row in connection.execute("SELECT * FROM records ORDER BY rowid")]
    users = [
        {
            "username": row["username"],
            "role": row["role"],
            "salt": row["salt"],
            "passwordHash": row["password_hash"],
            "passwordAlgorithm": row["password_algo"],
        }
        for row in connection.execute("SELECT username, role, salt, password_hash, password_algo FROM users ORDER BY id")
    ]
    backup = {
        "format": "memar-database-backup",
        "version": 1,
        "createdAt": int(time.time()),
        "records": records,
        "users": users,
    }
    content = json.dumps(backup, ensure_ascii=False, indent=2).encode("utf-8")
    return send_file(
        BytesIO(content),
        mimetype="application/json",
        as_attachment=True,
        download_name="memar-database-backup.json",
    )


@app.post("/api/admin/restore")
@require_user(admin=True, owner=True)
def restore_backup():
    payload = request.get_json(silent=True) or {}
    if payload.get("format") != "memar-database-backup" or payload.get("version") != 1:
        return error("صيغة النسخة الاحتياطية غير مدعومة.", 400)
    incoming_records = payload.get("records")
    incoming_users = payload.get("users")
    if not isinstance(incoming_records, list) or not isinstance(incoming_users, list):
        return error("ملف النسخة الاحتياطية غير مكتمل.", 400)
    try:
        records = [validate_record(item) for item in incoming_records]
        if len({record["id"] for record in records}) != len(records):
            return error("توجد معرّفات مكررة في النسخة الاحتياطية.", 400)
        users = [validate_backup_user(item) for item in incoming_users]
        if users and not any(user[4] == "admin" for user in users):
            return error("يجب أن تحتوي النسخة على حساب مدير واحد على الأقل.", 400)
        if users and not any(user[0].casefold() == "iyr3" and user[4] == "admin" for user in users):
            return error("يجب أن تحتفظ النسخة بحساب iyr3 كمدير.", 400)
        if len({user[0].casefold() for user in users}) != len(users):
            return error("توجد أسماء مستخدمين مكررة.", 400)
        connection = get_database()
        with transaction(connection):
            connection.execute("DELETE FROM records")
            for record in records:
                save_record(connection, record)
            if users:
                connection.execute("DELETE FROM sessions")
                connection.execute("DELETE FROM users")
                for username, password_hash, salt, password_algorithm, role in users:
                    connection.execute(
                        "INSERT INTO users(username, password_hash, salt, password_algo, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (username, password_hash, salt, password_algorithm, role, int(time.time())),
                    )
    except (ValueError, TypeError, sqlite3.IntegrityError) as exception:
        return error(f"تعذر استعادة النسخة: {exception}", 400)
    return jsonify({"ok": True, "records": len(records), "users": len(users), "signedOut": bool(users)})


@app.errorhandler(413)
def request_too_large(_exception):
    return error("حجم الملف أكبر من الحد المسموح.", 413)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    serve(app, host="0.0.0.0", port=port)
