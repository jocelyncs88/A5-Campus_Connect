# ==============================================================
# FILE: db_manager.py
# TUGAS: Pengelola database SQLite untuk Event
# ==============================================================

import sqlite3

DB_NAME = "database.db"

# =========================
# INIT DATABASE
# =========================
def init_db():
    # Buka koneksi ke file database SQLite.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # TAMBAHAN: Kolom 'status' ditambahkan di baris terakhir sebelum UNIQUE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT,
        nama_event TEXT,
        deskripsi_singkat TEXT,
        gambar_poster TEXT,
        jenis_event TEXT,
        tanggal_waktu TEXT,
        source TEXT,
        kategori TEXT,
        status TEXT,
        UNIQUE(nama_event, tanggal_waktu)
    )
    """)

    # Simpan struktur tabel ke database dan tutup koneksi.
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
    """Mengambil SEMUA event tanpa terkecuali"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows


# =========================
# GET EVENTS BY STATUS (FUNGSI BARU)
# =========================
def get_events_by_status(status):
    """Mengambil event yang sesuai dengan status tertentu (approved/pending/rejected)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE status = ? ORDER BY id ASC", (status,))
    rows = cursor.fetchall()
    conn.close()
    return rows


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