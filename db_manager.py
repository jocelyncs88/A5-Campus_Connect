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

    conn.commit()
    conn.close()


# =========================
# UPSERT EVENT
# =========================
def upsert_event(event):
    # Buka koneksi untuk menyimpan data event baru.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # TAMBAHAN: Menangkap status. Jika tidak ada, anggap "pending" (untuk form EO)
    status_event = event.get("status", "pending")

    # Insert event baru, atau ignore jika event sudah ada berdasarkan UNIQUE constraint.
    cursor.execute("""
    INSERT OR IGNORE INTO events
    (event_id, nama_event, deskripsi_singkat, gambar_poster,
     jenis_event, tanggal_waktu, source, kategori, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event.get("event_id"),
        event.get("nama_event"),
        event.get("deskripsi_singkat"),
        event.get("gambar_poster"),
        event.get("jenis_event"),
        event.get("tanggal_waktu"),
        event.get("source"),
        event.get("kategori"),
        status_event
    ))

    # Commit agar data benar-benar tersimpan, lalu tutup koneksi.
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
# UPDATE EVENT STATUS (FUNGSI BARU)
# =========================
def update_event_status(event_id, new_status):
    """Mengubah status validasi event (Approve/Decline)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET status = ? WHERE event_id = ?", (new_status, event_id))
    conn.commit()
    conn.close()


# =========================
# TEST MANUAL
# =========================
if __name__ == "__main__":
    # Inisialisasi database untuk memastikan tabel events tersedia.
    init_db()

    # Contoh data event yang akan dimasukkan ke database untuk pengujian.
    # Karena ini dummy untuk ngetes Homepage, kita set statusnya "approved"
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

    # Simpan data contoh ke database.
    upsert_event(dummy_event)

    # Tampilkan ke terminal
    print("Daftar Event Approved:")
    for e in get_events_by_status("approved"):
        print(e)