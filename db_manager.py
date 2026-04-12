import sqlite3

DB_NAME = "database.db"

# =========================
# INIT DATABASE
# =========================

def init_db():
    # Buka koneksi ke file database SQLite.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

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

    # Insert event baru, atau ignore jika event sudah ada berdasarkan UNIQUE constraint.
    cursor.execute("""
    INSERT OR IGNORE INTO events
    (event_id, nama_event, deskripsi_singkat, gambar_poster,
     jenis_event, tanggal_waktu, source, kategori)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event.get("event_id"),
        event.get("nama_event"),
        event.get("deskripsi_singkat"),
        event.get("gambar_poster"),
        event.get("jenis_event"),
        event.get("tanggal_waktu"),
        event.get("source"),
        event.get("kategori")
    ))

    # Commit agar data benar-benar tersimpan, lalu tutup koneksi.
    conn.commit()
    conn.close()


# =========================
# GET ALL EVENTS
# =========================
def get_all_events():
    # Buka koneksi untuk membaca semua event yang tersimpan.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ambil semua event dan urutkan berdasarkan tanggal agar lebih mudah dibaca.
    cursor.execute("SELECT * FROM events ORDER BY tanggal_waktu ASC")
    rows = cursor.fetchall()

    # Tutup koneksi lalu kembalikan data.
    conn.close()
    return rows


# =========================
# TEST MANUAL
# =========================
if __name__ == "__main__":
    # Inisialisasi database untuk memastikan tabel events tersedia.
    init_db()

    # Contoh data event yang akan dimasukkan ke database untuk pengujian.
    dummy_event = {
        "event_id": "SCR-TEST",
        "nama_event": "Seminar AI",
        "deskripsi_singkat": "Belajar AI",
        "gambar_poster": "",
        "jenis_event": "Internal",
        "tanggal_waktu": "2026-05-20",
        "source": "test.com",
        "kategori": "Seminar"
    }

    # Simpan data contoh ke database.
    upsert_event(dummy_event)

    # Ambil semua data event yang ada dan tampilkan ke layar.
    for e in get_all_events():
        print(e)