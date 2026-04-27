import sys
import os
import hashlib
from urllib.parse import urlparse

from PyQt5.QtWidgets import QApplication
import requests

import db_manager
import main_window
from main_window import MainWindow


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "assets", "cache_images")


def _normalize_event_row(row):
    """Menyamakan format data event dari DB menjadi dictionary untuk UI."""
    # db_manager.get_all_events() saat ini mengembalikan tuple SELECT *:
    # (id, event_id, nama_event, deskripsi_singkat, gambar_poster,
    #  jenis_event, tanggal_waktu, source, kategori)
    if isinstance(row, dict):
        return {
            "event_id": row.get("event_id", ""),
            "jenis_event": (row.get("jenis_event", "External") or "External").title(),
            "nama_event": row.get("nama_event", "Tanpa Judul") or "Tanpa Judul",
            "deskripsi_singkat": row.get("deskripsi_singkat", "") or "",
            "tanggal_waktu": row.get("tanggal_waktu", "TBA") or "TBA",
            "gambar_poster": row.get("gambar_poster", "") or "",
        }

    return {
        "event_id": row[1] if len(row) > 1 else "",
        "jenis_event": (row[5] if len(row) > 5 and row[5] else "External").title(),
        "nama_event": row[2] if len(row) > 2 and row[2] else "Tanpa Judul",
        "deskripsi_singkat": row[3] if len(row) > 3 and row[3] else "",
        "tanggal_waktu": row[6] if len(row) > 6 and row[6] else "TBA",
        "gambar_poster": row[4] if len(row) > 4 and row[4] else "",
    }


def _is_http_url(value):
    """Mengecek apakah nilai adalah URL gambar online (http/https)."""
    return isinstance(value, str) and value.startswith(("http://", "https://"))


def _cache_image(image_url):
    """Menyimpan gambar URL ke cache lokal agar loading UI lebih cepat/stabil."""
    # Jika bukan URL online, langsung pakai path asli.
    if not _is_http_url(image_url):
        return image_url

    # Pastikan folder cache tersedia.
    os.makedirs(CACHE_DIR, exist_ok=True)

    parsed = urlparse(image_url)
    ext = os.path.splitext(parsed.path)[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"

    # Nama file cache dibuat deterministik dari URL (MD5).
    file_name = hashlib.md5(image_url.encode("utf-8")).hexdigest() + ext
    local_path = os.path.join(CACHE_DIR, file_name)

    # Jika sudah pernah diunduh, pakai file lokal.
    if os.path.exists(local_path):
        return local_path

    try:
        # Download gambar sekali, lalu simpan untuk pemakaian berikutnya.
        response = requests.get(
            image_url,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
        return local_path
    except requests.RequestException:
        # Fallback: kembalikan URL asli jika unduh gagal.
        return image_url


def _load_ui_events_from_db():
    """Mengambil event dari DB, normalisasi field, lalu siapkan path gambar untuk UI."""
    rows = db_manager.get_all_events()
    events = []

    for row in rows:
        event = _normalize_event_row(row)
        
        # Pastikan field wajib tidak pernah kosong agar card render konsisten
        if not event.get("deskripsi_singkat") or event.get("deskripsi_singkat").strip() == "":
            event["deskripsi_singkat"] = "..."
        
        if not event.get("tanggal_waktu") or event.get("tanggal_waktu").strip() == "":
            event["tanggal_waktu"] = "TBA"
        
        if not event.get("jenis_event") or event.get("jenis_event").strip() == "":
            event["jenis_event"] = "External"
        
        event["gambar_poster"] = _cache_image(event.get("gambar_poster", ""))
        events.append(event)

    # Dipakai untuk mengganti dummy data saat data DB tersedia.
    return events


def main():
    """Entry point aplikasi: init DB, siapkan data UI, lalu jalankan PyQt app."""
    # Ensure local database and table exist before UI is shown.
    db_manager.init_db()

    # Muat data event dari DB untuk ditampilkan di homepage.
    db_events = _load_ui_events_from_db()
    if db_events:
        # Override dummy list in main_window only when DB has data.
        main_window.dummy_events = db_events

    # Inisialisasi aplikasi Qt dan tampilkan jendela utama.
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()