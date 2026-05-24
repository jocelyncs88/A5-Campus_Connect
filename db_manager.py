# ==============================================================
# FILE: db_manager.py
# TUGAS: Pengelola database SQLite untuk Event
# ==============================================================

import sqlite3
import re
from datetime import datetime

DB_NAME = "database.db"

# =========================================================
# SQLITE ROW -> DICTIONARY
# =========================================================
def row_to_dict(cursor, row):

    columns = [col[0] for col in cursor.description]

    return dict(zip(columns, row))

_MONTH_TRANSLATIONS = {
    "januari": "January",
    "februari": "February",
    "maret": "March",
    "april": "April",
    "mei": "May",
    "juni": "June",
    "juli": "July",
    "agustus": "August",
    "september": "September",
    "oktober": "October",
    "november": "November",
    "desember": "December",
}


def _normalize_month_names(value):
    text = str(value or "").strip().lower()
    for source, target in _MONTH_TRANSLATIONS.items():
        text = text.replace(source, target)
    return text


def _parse_event_datetime(value):
    text = str(value or "").strip()
    if not text or text.upper() == "TBA":
        return None

    normalized_text = _normalize_month_names(text)

    range_match = re.match(
        r"^(?P<start>\d{1,2})\s*-\s*(?P<end>\d{1,2})\s+(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})(?:\s+(?P<time>\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?))?$",
        normalized_text,
    )
    if range_match:
        start_date = f"{range_match.group('start')} {range_match.group('month')} {range_match.group('year')}"
        time_part = range_match.group('time') or ""
        candidate = f"{start_date} {time_part}".strip()
        for fmt in ("%d %B %Y %H:%M", "%d %B %Y", "%d %b %Y %H:%M", "%d %b %Y"):
            try:
                return datetime.strptime(candidate, fmt)
            except ValueError:
                continue

    formats = (
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d %B %Y %H:%M",
        "%d %B %Y",
        "%d %b %Y %H:%M",
        "%d %b %Y",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    )

    for fmt in formats:
        try:
            return datetime.strptime(normalized_text, fmt)
        except ValueError:
            continue
    return None


def _sort_events(rows):
    parsed_rows = []
    unparsed_rows = []

    for row in rows:
        tanggal_waktu = row.get("tanggal_waktu", "") if isinstance(row, dict) else (row[6] if len(row) > 6 else "")
        parsed = _parse_event_datetime(tanggal_waktu)
        if parsed is None:
            unparsed_rows.append(row)
        else:
            parsed_rows.append((parsed, tanggal_waktu, row))

    parsed_rows.sort(key=lambda item: (item[0], str(item[1]).strip().lower()), reverse=True)
    unparsed_rows.sort(key=lambda row: str(row.get("tanggal_waktu", "")).strip().lower() if isinstance(row, dict) else (str(row[6]).strip().lower() if len(row) > 6 else ""))
    return [row for _, _, row in parsed_rows] + unparsed_rows

def init_db():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # =========================================================
    # TABEL EVENTS
    # =========================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT,
        nama_event TEXT,
        deskripsi_singkat TEXT,
        gambar_poster TEXT,
        jenis_event TEXT,
        tanggal_waktu TEXT,

        tanggal_display TEXT,
        waktu_display TEXT,
        lokasi TEXT,

        tipe_tiket TEXT DEFAULT 'Gratis',
        harga_tiket TEXT DEFAULT '0',

        overview TEXT,

        phone_eo TEXT,
        email_eo TEXT,
        nama_eo TEXT,
        inisial_eo TEXT,

        organizer_id INTEGER,

        source TEXT,
        kategori TEXT,
        status TEXT,

        UNIQUE(nama_event, tanggal_waktu)
    )
    """)

    # =========================================================
    # TABEL USERS
    # =========================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT,
        bio TEXT,
        email TEXT UNIQUE,
        kontak TEXT,
        role TEXT DEFAULT 'mahasiswa',
        inisial TEXT,
        password TEXT
    )
    """)

    # =========================================================
    # TABEL BOOKINGS
    # =========================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_id TEXT,
        created_at TEXT,

        UNIQUE(user_id, event_id)
    )
    """)

    # =========================================================
    # TABEL LIKES
    # =========================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_id TEXT,

        UNIQUE(user_id, event_id)
    )
    """)

    # =========================================================
    # TABEL NOTIFICATIONS  ← TAMBAHAN BARU
    # Menyimpan notifikasi untuk EO saat admin approve/reject event
    # =========================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_user TEXT,
        judul TEXT,
        pesan TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    # =========================================================
    # TABEL EVENT UPDATE REQUESTS
    # Menyimpan permintaan perubahan event dari EO sebelum admin approve
    # =========================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_update_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT,
        requested_by_email TEXT,
        nama_event TEXT,
        deskripsi_singkat TEXT,
        gambar_poster TEXT,
        jenis_event TEXT,
        tanggal_waktu TEXT,
        source TEXT,
        kategori TEXT,
        lokasi TEXT,
        tipe_tiket TEXT DEFAULT 'Gratis',
        harga_tiket TEXT DEFAULT '0',
        nama_eo TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )
    """)

    # ← TAMBAHAN: Migration - tambah kolom baru kalau belum ada
    kolom_baru = [
        ("lokasi",      "TEXT DEFAULT ''"),
        ("tipe_tiket",  "TEXT DEFAULT 'Free'"),
        ("harga_tiket", "TEXT DEFAULT '0'"),
        ("nama_eo",     "TEXT DEFAULT ''"),
    ]
    
    for nama_kolom, tipe in kolom_baru:
        try:
            cursor.execute(f"ALTER TABLE events ADD COLUMN {nama_kolom} {tipe}")
            print(f"[DB] Kolom '{nama_kolom}' berhasil ditambahkan.")
        except Exception:
            pass  # Kolom sudah ada, skip
    
    conn.commit()
    conn.close()


# =========================
# UPSERT EVENT
# =========================
def upsert_event(event):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    status_event = event.get("status", "pending")

    cursor.execute("""
    INSERT OR IGNORE INTO events
    (event_id, nama_event, deskripsi_singkat, gambar_poster,
     jenis_event, tanggal_waktu, source, kategori, status,
     lokasi, tipe_tiket, harga_tiket, nama_eo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event.get("event_id"),
        event.get("nama_event"),
        event.get("deskripsi_singkat"),
        event.get("gambar_poster"),
        event.get("jenis_event"),
        event.get("tanggal_waktu"),
        event.get("source"),
        event.get("kategori"),
        status_event,
        event.get("lokasi", ""),
        event.get("tipe_tiket", "Free"),
        event.get("harga_tiket", "0"),
        event.get("penyelenggara", ""),
    ))

    conn.commit()
    conn.close()


# =========================
# GET ALL EVENTS
# =========================
def get_all_events():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM events
    """)

    rows = cursor.fetchall()

    sorted_rows = _sort_events(rows)

    result = [row_to_dict(cursor, row) for row in sorted_rows]

    conn.close()

    return result

# =========================
# GET EVENTS BY STATUS
# =========================
def get_events_by_status(status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM events
        WHERE status = ?
    """, (status,))

    rows = cursor.fetchall()

    sorted_rows = _sort_events(rows)

    result = [row_to_dict(cursor, row) for row in sorted_rows]

    conn.close()

    return result

# =========================================================
# GET EVENTS BY ORGANIZER
# =========================================================
def get_events_by_organizer(organizer_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM events
        WHERE organizer_id = ?
        ORDER BY tanggal_waktu ASC
    """, (organizer_id,))

    rows = cursor.fetchall()

    result = [row_to_dict(cursor, row) for row in rows]

    conn.close()

    return result


# =========================================================
# GET BOOKED EVENTS
# =========================================================
def get_booked_events(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.* FROM events e
        JOIN bookings b ON e.event_id = b.event_id
        WHERE b.user_id = ?
        ORDER BY e.tanggal_waktu ASC
    """, (user_id,))

    rows = cursor.fetchall()

    result = [row_to_dict(cursor, row) for row in rows]

    conn.close()

    return result


# =========================================================
# GET LIKED EVENTS
# =========================================================
def get_liked_events(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.* FROM events e
        JOIN likes l ON e.event_id = l.event_id
        WHERE l.user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()

    result = [row_to_dict(cursor, row) for row in rows]

    conn.close()

    return result

# =========================
# UPDATE EVENT STATUS
# =========================
def update_event_status(event_id, new_status):
    """Mengubah status validasi event (Approve/Decline)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET status = ? WHERE event_id = ?", (new_status, event_id))
    conn.commit()
    conn.close()


def create_event_update_request(event_data):
    """Menyimpan perubahan event dari EO ke antrean validasi admin."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    event_id = (event_data.get("event_id") or "").strip()
    if not event_id:
        conn.close()
        raise ValueError("event_id wajib diisi untuk membuat request perubahan.")

    # Simpan request terbaru saja untuk satu event agar antrean tidak menumpuk.
    cursor.execute(
        "DELETE FROM event_update_requests WHERE event_id = ? AND status = 'pending'",
        (event_id,)
    )

    cursor.execute("""
        INSERT INTO event_update_requests (
            event_id, requested_by_email, nama_event, deskripsi_singkat,
            gambar_poster, jenis_event, tanggal_waktu, source, kategori,
            lokasi, tipe_tiket, harga_tiket, nama_eo, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    """, (
        event_id,
        (event_data.get("requested_by_email") or event_data.get("email_eo") or "").strip(),
        event_data.get("nama_event", ""),
        event_data.get("deskripsi_singkat", ""),
        event_data.get("gambar_poster", ""),
        event_data.get("jenis_event", ""),
        event_data.get("tanggal_waktu", ""),
        event_data.get("source", "manual"),
        event_data.get("kategori", ""),
        event_data.get("lokasi", ""),
        event_data.get("tipe_tiket", "Free"),
        event_data.get("harga_tiket", "0"),
        event_data.get("nama_eo", event_data.get("penyelenggara", "")),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))

    conn.commit()
    conn.close()


def get_event_update_requests(status="pending"):
    """Mengambil daftar request perubahan event dari EO."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if status:
        cursor.execute(
            "SELECT * FROM event_update_requests WHERE status = ? ORDER BY created_at DESC",
            (status,)
        )
    else:
        cursor.execute("SELECT * FROM event_update_requests ORDER BY created_at DESC")

    rows = cursor.fetchall()
    result = [row_to_dict(cursor, row) for row in rows]
    conn.close()
    return result


def get_event_update_request(request_id):
    """Mengambil satu request perubahan berdasarkan id."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event_update_requests WHERE id = ?", (request_id,))
    row = cursor.fetchone()
    result = row_to_dict(cursor, row) if row else None
    conn.close()
    return result


def apply_event_update_request(request_id, new_status):
    """Menerapkan atau menolak request perubahan event."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM event_update_requests WHERE id = ?", (request_id,))
    request_row = cursor.fetchone()
    if not request_row:
        conn.close()
        return False

    request = row_to_dict(cursor, request_row)
    event_id = request.get("event_id", "")

    if new_status == "approved":
        cursor.execute("""
            UPDATE events SET
                nama_event = ?,
                deskripsi_singkat = ?,
                gambar_poster = ?,
                jenis_event = ?,
                tanggal_waktu = ?,
                source = ?,
                kategori = ?,
                lokasi = ?,
                tipe_tiket = ?,
                harga_tiket = ?,
                nama_eo = ?,
                status = 'approved'
            WHERE event_id = ?
        """, (
            request.get("nama_event", ""),
            request.get("deskripsi_singkat", ""),
            request.get("gambar_poster", ""),
            request.get("jenis_event", ""),
            request.get("tanggal_waktu", ""),
            request.get("source", "manual"),
            request.get("kategori", ""),
            request.get("lokasi", ""),
            request.get("tipe_tiket", "Free"),
            request.get("harga_tiket", "0"),
            request.get("nama_eo", ""),
            event_id,
        ))
        if cursor.rowcount == 0:
            conn.close()
            return False

    cursor.execute(
        "UPDATE event_update_requests SET status = ? WHERE id = ?",
        (new_status, request_id)
    )

    conn.commit()
    conn.close()
    return True


# =========================================================
# NOTIFICATIONS — FUNGSI-FUNGSI BARU
# =========================================================

def simpan_notifikasi(email_user, judul, pesan):
    """
    Menyimpan satu notifikasi baru ke tabel notifications.
    Dipanggil dari main_window.py saat admin approve/reject event.

    Parameter:
        email_user : email EO pemilik event (str)
        judul      : judul singkat notifikasi (str)
        pesan      : isi pesan lengkap (str)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications (email_user, judul, pesan, is_read, created_at)
        VALUES (?, ?, ?, 0, ?)
    """, (
        email_user,
        judul,
        pesan,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    conn.close()


def get_notifikasi(email_user):
    """
    Mengambil semua notifikasi milik seorang EO, diurutkan
    dari yang terbaru (created_at DESC).

    Parameter:
        email_user : email EO yang sedang login (str)

    Return:
        list of dict — setiap dict berisi kolom tabel notifications
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM notifications
        WHERE email_user = ?
        ORDER BY created_at DESC
    """, (email_user,))
    rows = cursor.fetchall()
    result = [row_to_dict(cursor, row) for row in rows]
    conn.close()
    return result


def hitung_notifikasi_belum_dibaca(email_user):
    """
    Menghitung jumlah notifikasi yang belum dibaca (is_read = 0)
    milik EO tertentu. Dipakai untuk angka badge di lonceng navbar.

    Return:
        int — jumlah notifikasi belum dibaca
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM notifications
        WHERE email_user = ? AND is_read = 0
    """, (email_user,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def tandai_notifikasi_dibaca(notif_id):
    """
    Menandai satu notifikasi sebagai sudah dibaca (is_read = 1).
    Dipanggil saat user mengklik item notifikasi di halaman notifikasi.

    Parameter:
        notif_id : id baris di tabel notifications (int)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications SET is_read = 1 WHERE id = ?
    """, (notif_id,))
    conn.commit()
    conn.close()


def tandai_semua_notifikasi_dibaca(email_user):
    """
    Menandai semua notifikasi milik EO sebagai sudah dibaca.
    Opsional — bisa dipanggil saat EO membuka halaman notifikasi.

    Parameter:
        email_user : email EO (str)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications SET is_read = 1
        WHERE email_user = ? AND is_read = 0
    """, (email_user,))
    conn.commit()
    conn.close()

def ensure_user_exists(email_user):
    """Create user in database.db if doesn't exist (called after login)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check if user already exists
    user = cursor.execute("SELECT id FROM users WHERE email = ?", (email_user,)).fetchone()
    
    if user:
        conn.close()
        return user[0]
    
    # User doesn't exist, create new user record
    cursor.execute("""
        INSERT INTO users (email, role)
        VALUES (?, ?)
    """, (email_user, 'mahasiswa'))
    
    conn.commit()
    new_user_id = cursor.lastrowid
    
    conn.close()
    return new_user_id

def book_event(email_user, event_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = cursor.execute("SELECT id FROM users WHERE email = ?", (email_user,)).fetchone()

    if user:
        cursor.execute("""
            INSERT OR IGNORE INTO bookings (user_id, event_id, created_at)
            VALUES (?, ?, ?)
        """, (user[0], event_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        # Verify booking was inserted
        verify = cursor.execute("SELECT * FROM bookings WHERE user_id = ? AND event_id = ?", (user[0], event_id)).fetchone()
    else:
        conn.close()

def unbook_event(email_user, event_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = cursor.execute("SELECT id FROM users WHERE email = ?", (email_user,)).fetchone()
    if user:
        print(f"[unbook_event] Unbooking user_id={user[0]} with event_id={event_id}")
        cursor.execute("DELETE FROM bookings WHERE user_id = ? AND event_id = ?",
                       (user[0], event_id))
        conn.commit()
    conn.close()

def is_event_booked(email_user, event_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = cursor.execute("SELECT id FROM users WHERE email = ?", (email_user,)).fetchone()
    if not user:
        conn.close()
        return False
    result = cursor.execute("""
        SELECT 1 FROM bookings WHERE user_id = ? AND event_id = ?
    """, (user[0], event_id)).fetchone()
    conn.close()
    return result is not None


# =========================
# TEST MANUAL
# =========================
if __name__ == "__main__":
    init_db()

    dummy_event = {
        "event_id": "SCR-TEST",
        "nama_event": "Seminar AI",
        "deskripsi_singkat": "Belajar AI",
        "gambar_poster": "",
        "jenis_event": "Internal",
        "tanggal_waktu": "2026-05-20",
        "source": "test.com",
        "kategori": "Seminar",
        "status": "approved"
    }

    upsert_event(dummy_event)

    print("Daftar Event Approved:")
    for e in get_events_by_status("approved"):
        print(e)

    # Test notifikasi
    simpan_notifikasi("eo@test.com", "Event Disetujui ✅", "Seminar AI telah disetujui admin dan kini tampil di Campus Connect!")
    print("\nNotifikasi EO:")
    for n in get_notifikasi("eo@test.com"):
        print(n)
    print("Belum dibaca:", hitung_notifikasi_belum_dibaca("eo@test.com"))