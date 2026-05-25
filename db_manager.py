# ==============================================================
# FILE: db_manager.py
# TUGAS: Pengelola database SQLite untuk Event
# ==============================================================

import sqlite3
import re
import uuid
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

    # Bersihkan duplikat legacy berdasarkan event_id lama yang belum unik.
    # Simpan row terakhir untuk setiap event_id, termasuk event_id kosong.
    cursor.execute("""
        DELETE FROM events
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM events
            GROUP BY COALESCE(NULLIF(TRIM(event_id), ''), '__EMPTY__')
        )
    """)

    # Index unik untuk event_id agar booking mengarah ke satu event saja.
    try:
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_events_event_id ON events(event_id)")
    except Exception:
        pass

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
        created_at TEXT,
        tipe_notif  TEXT DEFAULT 'EO_APPROVAL',
        event_id_ref TEXT DEFAULT ''
    )
    """)

    # =========================================================
    # TABEL NOTIFICATION_PREFERENCES  ← TAMBAHAN BARU
    # Menyimpan preferensi toggle notifikasi per user.
    # Default ON — kalau row belum ada, dianggap menyala.
    # =========================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_preferences (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        email_user  TEXT NOT NULL,
        nama_setting TEXT NOT NULL,
        is_on       INTEGER DEFAULT 1,
        UNIQUE(email_user, nama_setting)
    )
    """)

    # Migration: tambah kolom baru ke notifications jika belum ada
    notif_kolom_baru = [
        ("tipe_notif",   "TEXT DEFAULT 'EO_APPROVAL'"),
        ("event_id_ref", "TEXT DEFAULT ''"),
    ]
    for nama_kolom, tipe in notif_kolom_baru:
        try:
            cursor.execute(f"ALTER TABLE notifications ADD COLUMN {nama_kolom} {tipe}")
            print(f"[DB] Kolom notifications.'{nama_kolom}' berhasil ditambahkan.")
        except Exception:
            pass  # Kolom sudah ada, skip

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
    event_id = (event.get("event_id") or "").strip() or f"AUTO-{uuid.uuid4().hex[:12].upper()}"

    cursor.execute("""
    INSERT INTO events
    (event_id, nama_event, deskripsi_singkat, gambar_poster,
     jenis_event, tanggal_waktu, source, kategori, status,
     lokasi, tipe_tiket, harga_tiket, nama_eo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(event_id) DO UPDATE SET
        nama_event = excluded.nama_event,
        deskripsi_singkat = excluded.deskripsi_singkat,
        gambar_poster = excluded.gambar_poster,
        jenis_event = excluded.jenis_event,
        tanggal_waktu = excluded.tanggal_waktu,
        source = excluded.source,
        kategori = excluded.kategori,
        status = excluded.status,
        lokasi = excluded.lokasi,
        tipe_tiket = excluded.tipe_tiket,
        harga_tiket = excluded.harga_tiket,
        nama_eo = excluded.nama_eo
    """, (
        event_id,
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
          AND e.id = (
              SELECT MAX(e2.id)
              FROM events e2
              WHERE e2.event_id = e.event_id
          )
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
          AND e.id = (
              SELECT MAX(e2.id)
              FROM events e2
              WHERE e2.event_id = e.event_id
          )
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

# simpan_notifikasi moved above with extended signature


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

# =========================================================
# NOTIFICATION PREFERENCES — FUNGSI BARU
# =========================================================

def get_notif_pref(email_user: str, nama_setting: str) -> bool:
    """
    Mengambil preferensi toggle satu notifikasi milik user.
    Default ON jika row belum pernah disimpan.

    Parameter:
        email_user   : email user (str)
        nama_setting : nama toggle, contoh 'notif_event_reminder' (str)

    Return:
        bool — True = ON, False = OFF
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT is_on FROM notification_preferences
        WHERE email_user = ? AND nama_setting = ?
    """, (email_user, nama_setting)).fetchone()
    conn.close()
    return bool(row[0]) if row is not None else True   # default ON


def set_notif_pref(email_user: str, nama_setting: str, is_on: bool):
    """
    Menyimpan/update preferensi toggle satu notifikasi.
    Menggunakan INSERT OR REPLACE agar idempotent.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO notification_preferences
            (email_user, nama_setting, is_on)
        VALUES (?, ?, ?)
    """, (email_user, nama_setting, 1 if is_on else 0))
    conn.commit()
    conn.close()


# =========================================================
# STUDENT NOTIFICATION TRIGGERS — FUNGSI BARU
# =========================================================

def _get_emails_booked_event(event_id: str) -> list:
    """
    Mengambil semua email student yang sudah booking event tertentu.
    Dipakai sebagai target penerima notif Critical Updates.

    Return: list of str (email)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT u.email FROM users u
        JOIN bookings b ON b.user_id = u.id
        WHERE b.event_id = ? AND u.email IS NOT NULL AND u.email != ''
    """, (event_id,)).fetchall()
    conn.close()
    return [r[0] for r in rows]


def _get_emails_liked_same_category(kategori: str) -> list:
    """
    Mengambil semua email student yang pernah me-like event
    dengan kategori yang sama. Dipakai untuk Interest Match.

    Return: list of str (email), sudah di-deduplicate
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT DISTINCT u.email FROM users u
        JOIN likes l ON l.user_id = u.id
        JOIN events e ON e.event_id = l.event_id
        WHERE LOWER(TRIM(e.kategori)) = LOWER(TRIM(?))
          AND u.email IS NOT NULL AND u.email != ''
          AND LOWER(TRIM(u.role)) = 'mahasiswa'
    """, (kategori,)).fetchall()
    conn.close()
    return [r[0] for r in rows]


def _get_all_student_emails() -> list:
    """
    Mengambil semua email user dengan role 'mahasiswa'.
    Dipakai untuk Campus Spotlight (broadcast event Internal).

    CATATAN: sengaja filter role = 'mahasiswa' secara eksplisit
    agar EO dan admin tidak ikut menerima notifikasi ini,
    meskipun mereka juga tercatat di tabel users.

    Return: list of str (email)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT email FROM users
        WHERE LOWER(TRIM(role)) = 'mahasiswa'
          AND email IS NOT NULL AND email != ''
    """).fetchall()
    conn.close()
    return [r[0] for r in rows]


def _sudah_ada_notif_h1(email_user: str, event_id: str) -> bool:
    """
    Mengecek apakah reminder H-1 untuk event tertentu sudah pernah
    dibuat untuk user ini. Mencegah duplikat reminder.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT 1 FROM notifications
        WHERE email_user = ? AND event_id_ref = ? AND tipe_notif = 'H1_REMINDER'
        LIMIT 1
    """, (email_user, event_id)).fetchone()
    conn.close()
    return row is not None


def simpan_notifikasi(email_user: str, judul: str, pesan: str,
                      tipe_notif: str = "EO_APPROVAL",
                      event_id_ref: str = ""):
    """
    Menyimpan satu notifikasi baru ke tabel notifications.

    Parameter:
        email_user   : email penerima (str)
        judul        : judul singkat (str)
        pesan        : isi pesan lengkap (str)
        tipe_notif   : 'EO_APPROVAL' | 'H1_REMINDER' | 'EVENT_UPDATED'
                       | 'NEW_LIKED_MATCH' | 'CAMPUS_NEW_EVENT'
        event_id_ref : event_id yang relevan, untuk redirect (str)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications
            (email_user, judul, pesan, is_read, created_at, tipe_notif, event_id_ref)
        VALUES (?, ?, ?, 0, ?, ?, ?)
    """, (
        email_user,
        judul,
        pesan,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        tipe_notif,
        event_id_ref,
    ))
    conn.commit()
    conn.close()


def kirim_notif_critical_update(event_id: str, nama_event: str):
    """
    Mengirim notifikasi Critical Update ke semua student
    yang sudah booking event ini (jika preferensi mereka ON).
    Dipanggil dari main_window.py saat admin/EO update detail event.
    """
    judul = f"📢 Event Update: {nama_event}"
    pesan = (
        f'"{nama_event}" has been updated by the organizer. '
        f"Please check the latest event details to stay up to date."
    )
    for email in _get_emails_booked_event(event_id):
        if get_notif_pref(email, "notif_critical_updates"):
            simpan_notifikasi(email, judul, pesan,
                              tipe_notif="EVENT_UPDATED",
                              event_id_ref=event_id)


def kirim_notif_interest_match(event_id: str, nama_event: str, kategori: str):
    """
    Mengirim notifikasi Interest Match ke student yang pernah
    me-like event dengan kategori yang sama (jika preferensi ON).
    Dipanggil dari main_window.py saat admin approve event baru.
    """
    judul = f"✨ New event you might like!"
    pesan = (
        f'"{nama_event}" is a new {kategori} event that matches '
        f"your interests based on your liked events. Check it out!"
    )
    for email in _get_emails_liked_same_category(kategori):
        if get_notif_pref(email, "notif_interest_match"):
            simpan_notifikasi(email, judul, pesan,
                              tipe_notif="NEW_LIKED_MATCH",
                              event_id_ref=event_id)


def kirim_notif_campus_spotlight(event_id: str, nama_event: str):
    """
    Mengirim notifikasi Campus Spotlight ke semua student
    saat event Internal baru di-approve (jika preferensi ON).
    Dipanggil dari main_window.py saat admin approve event berjenis Internal.
    """
    judul = f"🏫 New campus event: {nama_event}"
    pesan = (
        f'"{nama_event}" from your campus is now live on Campus Connect! '
        f"Be the first to know and grab your spot."
    )
    for email in _get_all_student_emails():
        if get_notif_pref(email, "notif_campus_spotlight"):
            simpan_notifikasi(email, judul, pesan,
                              tipe_notif="CAMPUS_NEW_EVENT",
                              event_id_ref=event_id)


def hitung_registrant_event(event_id: str) -> int:
    """
    Menghitung total registrant (booking) untuk sebuah event.
    Dipakai untuk pesan notifikasi New Registrant ke EO.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT COUNT(*) FROM bookings WHERE event_id = ?
    """, (event_id,)).fetchone()
    conn.close()
    return row[0] if row else 0


def kirim_notif_new_registrant(event_id: str, nama_event: str,
                                email_student: str, email_eo: str):
    """
    Mengirim notifikasi New Registrant ke EO pemilik event
    saat ada student yang booking, jika preferensi EO ON.

    Parameter:
        event_id      : ID event yang di-booking (str)
        nama_event    : nama event (str)
        email_student : email student yang baru booking (str)
        email_eo      : email EO pemilik event (str)
    """
    if not email_eo:
        return
    if not get_notif_pref(email_eo, "notif_new_registrant"):
        return   # EO matikan toggle ini

    total = hitung_registrant_event(event_id)
    judul = f"New Registrant for {nama_event}!"
    suffix = "s" if total != 1 else ""
    pesan = (
        f"Congrats! There's a new registrant for \"{nama_event}\". "
        f"Your event now has {total} registrant{suffix}. "
        f"Keep up the momentum!"
    )
    simpan_notifikasi(email_eo, judul, pesan,
                      tipe_notif="EO_APPROVAL",   # tampil dengan ikon ✅ di notif EO
                      event_id_ref=event_id)


def cek_dan_kirim_reminder_h1(email_user: str):
    """
    Mengecek semua event yang di-booking user, lalu membuat notifikasi
    H-1 reminder untuk yang tanggalnya besok dan belum ada remindernya.
    
    Dipanggil dari main_window.py:
      - Sekali saat login
      - Setiap jam via QTimer
    """
    if not get_notif_pref(email_user, "notif_event_reminder"):
        return   # User matikan toggle ini

    # Cari user_id berdasarkan email
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user_row = cursor.execute(
        "SELECT id FROM users WHERE email = ?", (email_user,)
    ).fetchone()
    if not user_row:
        conn.close()
        return
    user_id = user_row[0]

    # Ambil semua event yang di-booking user ini
    rows = cursor.execute("""
        SELECT e.event_id, e.nama_event, e.tanggal_waktu, e.waktu_display
        FROM events e
        JOIN bookings b ON b.event_id = e.event_id
        WHERE b.user_id = ?
    """, (user_id,)).fetchall()
    conn.close()

    from datetime import timedelta as _td
    besok = (datetime.now() + _td(days=1)).date()

    for event_id, nama_event, tanggal_waktu, waktu_display in rows:
        parsed = _parse_event_datetime(tanggal_waktu)  # fungsi di file ini
        if parsed is None:
            continue
        if parsed.date() != besok:
            continue
        if _sudah_ada_notif_h1(email_user, event_id):
            continue   # Sudah pernah kirim, skip

        waktu_str = waktu_display or tanggal_waktu or "the scheduled time"
        judul = f"🔔 Reminder: {nama_event} is tomorrow!"
        pesan = (
            f"Don't forget — '{nama_event}' is happening tomorrow "
            f"at {waktu_str}. See you there!"
        )
        simpan_notifikasi(email_user, judul, pesan,
                          tipe_notif="H1_REMINDER",
                          event_id_ref=event_id)


def ensure_user_exists(email_user, role: str = "mahasiswa"):
    """
    Pastikan user ada di tabel users (database.db).
    Dipanggil saat login agar booking & notifikasi bisa berjalan.

    Parameter:
        email_user : email user yang login (str)
        role       : role dari accounts.db — 'mahasiswa', 'eo', 'admin' (str)
                     Penting agar EO tidak masuk bucket 'mahasiswa' dan
                     tidak ikut menerima Campus Spotlight / Interest Match.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT id, role FROM users WHERE email = ?", (email_user,)
    ).fetchone()

    if existing:
        user_id = existing[0]
        existing_role = existing[1] or ""
        # Update role jika berbeda (misal akun lama tersimpan dengan role salah)
        if existing_role != role:
            cursor.execute(
                "UPDATE users SET role = ? WHERE email = ?", (role, email_user)
            )
            conn.commit()
        conn.close()
        return user_id

    # User belum ada — buat baru dengan role yang benar
    cursor.execute("""
        INSERT INTO users (email, role)
        VALUES (?, ?)
    """, (email_user, role))
    conn.commit()
    new_user_id = cursor.lastrowid
    conn.close()
    return new_user_id

def book_event(email_user, event_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = cursor.execute(
        "SELECT id FROM users WHERE email = ?", (email_user,)
    ).fetchone()

    if not user:
        conn.close()
        return

    # Insert booking (IGNORE jika sudah ada — mencegah double notif)
    cursor.execute("""
        INSERT OR IGNORE INTO bookings (user_id, event_id, created_at)
        VALUES (?, ?, ?)
    """, (user[0], event_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    was_inserted = cursor.rowcount > 0   # 1 = baru, 0 = sudah ada sebelumnya
    conn.commit()
    conn.close()

    # Kirim notif New Registrant ke EO hanya jika ini booking baru
    if was_inserted:
        try:
            # Ambil info event: nama_event dan email_eo
            ev_rows = get_all_events()
            ev = next((e for e in ev_rows
                       if str(e.get("event_id", "")) == str(event_id)), None)
            if ev:
                kirim_notif_new_registrant(
                    event_id=str(event_id),
                    nama_event=ev.get("nama_event", event_id),
                    email_student=email_user,
                    email_eo=ev.get("email_eo", ""),
                )
        except Exception as _e:
            print(f"[NEW REGISTRANT NOTIF] {_e}")

def kirim_notif_cancellation(event_id: str, nama_event: str,
                              email_student: str, email_eo: str):
    """
    Mengirim notifikasi Registration Cancellation ke EO
    saat student cancel booking, jika preferensi EO ON.
    """
    if not email_eo:
        return
    if not get_notif_pref(email_eo, "notif_cancellations"):
        return

    sisa = hitung_registrant_event(event_id)   # hitung SETELAH unbook
    judul = f"📋 Cancellation: {nama_event}"
    pesan = (
        f'A participant has cancelled their registration for "{nama_event}". '
        f'Your event now has {sisa} registrant{"s" if sisa != 1 else ""} remaining.'
    )
    simpan_notifikasi(email_eo, judul, pesan,
                      tipe_notif="EO_APPROVAL",
                      event_id_ref=event_id)


def unbook_event(email_user, event_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = cursor.execute(
        "SELECT id FROM users WHERE email = ?", (email_user,)
    ).fetchone()
    if not user:
        conn.close()
        return

    print(f"[unbook_event] Unbooking user_id={user[0]} with event_id={event_id}")
    cursor.execute(
        "DELETE FROM bookings WHERE user_id = ? AND event_id = ?",
        (user[0], event_id)
    )
    was_deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    # Kirim notif cancellation ke EO hanya jika memang ada row yang dihapus
    if was_deleted:
        try:
            ev_rows = get_all_events()
            ev = next((e for e in ev_rows
                       if str(e.get("event_id", "")) == str(event_id)), None)
            if ev:
                kirim_notif_cancellation(
                    event_id=str(event_id),
                    nama_event=ev.get("nama_event", event_id),
                    email_student=email_user,
                    email_eo=ev.get("email_eo", ""),
                )
        except Exception as _e:
            print(f"[CANCELLATION NOTIF] {_e}")

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