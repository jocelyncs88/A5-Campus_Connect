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