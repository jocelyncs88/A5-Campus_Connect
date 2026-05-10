import sqlite3
import hashlib

DB_NAME = "accounts.db"


# =========================
# CONNECT DATABASE
# =========================
def connect_db():
    return sqlite3.connect(DB_NAME)


# =========================
# HASH PASSWORD
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# CREATE TABLE
# =========================
def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# =========================
# REGISTER ACCOUNT
# =========================
def register_account(email, password):
    conn = connect_db()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    try:
        cursor.execute("""
        INSERT INTO accounts (email, password)
        VALUES (?, ?)
        """, (email, hashed_pw))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


# =========================
# CHECK LOGIN
# =========================
def check_login(email, password):
    conn = connect_db()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    cursor.execute("""
    SELECT * FROM accounts
    WHERE email = ? AND password = ?
    """, (email, hashed_pw))

    result = cursor.fetchone()

    conn.close()

    return result is not None


# =========================
# CREATE DEMO ACCOUNT
# =========================
def create_demo_account():
    register_account("admin@gmail.com", "123456")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    create_table()
    create_demo_account()

    print("Database dan akun demo berhasil dibuat!")