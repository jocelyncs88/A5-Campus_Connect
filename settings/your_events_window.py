# ==============================================================
# FILE: settings/your_events_window.py
# TUGAS: Membangun panel "Your Events Settings" di halaman Settings
#        dengan 2 skenario tampilan berbeda berdasarkan role user:
#
#   ROLE_ORGANIZER → Published Events (grid kartu + icon edit hover)
#   ROLE_MAHASISWA / ROLE_UMUM → Booked Events (scroll horizontal)
#                                + Liked Events (grid dengan deskripsi)
#
# DIBUAT OLEH: UI/UX Designer (fitur-Settings)
#
# CATATAN DATA DUMMY:
#   Saat ini menggunakan data dummy yang sudah lengkap strukturnya.
#   Saat database sudah memiliki tabel bookings, likes, dan kolom
#   tambahan di tabel events, cukup ganti fungsi:
#     - _get_published_events()  → db_manager.get_events_by_organizer(id)
#     - _get_booked_events()     → db_manager.get_booked_events(user_id)
#     - _get_liked_events()      → db_manager.get_liked_events(user_id)
#   Tampilan tidak perlu diubah sama sekali.
# ==============================================================

import sys
import os
from language_manager import lang
import requests

# Tambahkan root ke sys.path agar bisa import dari luar folder settings/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog
from detail_event_page import DetailEventPage

# Global store for image loader threads to ensure they are not GC'd
_GLOBAL_IMG_THREADS = []


# ==============================================================
# ASYNC IMAGE LOADER — mencegah UI freeze saat load gambar URL
# ==============================================================
class _ImageLoaderThread(QThread):
    loaded = pyqtSignal(QPixmap)

    def __init__(self, source, size, parent=None):
        super().__init__(parent)
        self.source = source
        self.size = size

    def run(self):
        pixmap = QPixmap()
        source = str(self.source or "").strip()
        if source.startswith(("http://", "https://")):
            try:
                response = requests.get(source, timeout=8)
                response.raise_for_status()
                pixmap.loadFromData(response.content)
            except Exception:
                pixmap = QPixmap()
        elif source and os.path.exists(source):
            pixmap = QPixmap(source)

        if not pixmap.isNull() and self.size:
            pixmap = pixmap.scaled(
                self.size,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
        self.loaded.emit(pixmap)


# ==============================================================
# KONSTANTA WARNA
# ==============================================================
C_TITLE = "#516465"
C_SUBTITLE = "#828282"
C_OPTION = "#747C86"
C_DIVIDER = "#888780"

COLOR_GRAY_LIGHT   = "#D2E6E5"
COLOR_TEAL_DARK    = "#516465"
COLOR_TEXT_PRIMARY = "#5D6B6B"
COLOR_TEXT_MUTED   = "#9AABAB"
COLOR_DIVIDER      = "#D2E6E5"
COLOR_PINK_BOOKED  = "#EAA4A6"   # Warna tombol Booked setelah di-klik


# ==============================================================
# KONSTANTA ROW EVENTS
# ==============================================================
GRID_MAX_COLS      = 7
GRID_H_SPACING     = 50
GRID_V_SPACING     = 46
CARD_WIDTH         = 200
BOOKED_POSTER_H    = 218
LIKED_POSTER_H     = 240
EO_POSTER_H        = 240


# ==============================================================
# KONSTANTA ROLE USER
# ==============================================================
ROLE_ORGANIZER = "eo"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM      = "umum"


def _is_eo_role(role):
    return (role or "").lower().strip() in ("eo", "organizer")

def _is_mahasiswa_role(role):
    return (role or "").lower().strip() in ("mahasiswa", "student")


# ==============================================================
# DATA DUMMY
# Struktur data sudah lengkap sesuai kebutuhan halaman deskripsi.
# Saat database siap, ganti return value di fungsi _get_*() saja.
#
# Field yang akan ditambahkan ke tabel events nanti:
#   lokasi, waktu_display, tipe_tiket, harga_tiket,
#   overview, phone_eo, email_eo, nama_eo, inisial_eo
# ==============================================================
DUMMY_EVENTS_EO = [
    {
        "event_id"       : "EVT-001",
        "nama_event"     : "Sparta Festival",
        "deskripsi_singkat": "Live painting and exhibition",
        "jenis_event"    : "External",
        "tanggal_waktu"  : "2026-05-20",
        "tanggal_display": "Sunday, November 30",
        "waktu_display"  : "8 AM",
        "lokasi"         : "Istana Plaza (Lt. Lower Ground)",
        "tipe_tiket"     : "Gratis",
        "harga_tiket"    : "0",
        "overview"       : (
            "SPARTA FESTIVAL Is Coming!\n\n"
            "Terbuka untuk seluruh siswa SMA/SMK dan Mahasiswa se-Bandung Raya.\n\n"
            "What to Expect:\n"
            "• Live Painting Artist: Menyaksikan kreativitas seni secara langsung.\n"
            "• Live Performance: Penampilan panggung yang akan membangun vibes positif.\n"
            "• Pameran Karya: Eksibisi karya terbaik dari anak muda Bandung.\n"
            "• GUEST STAR RAHASIA: Penampilan spesial dari bintang tamu tak terduga.\n\n"
            "Registration Info:\n"
            "• GRATIS! Terbuka untuk umum.\n"
            "• Benefit: FREE MERCHANDISE untuk kuota terbatas.\n"
            "• Periode Pendaftaran: 21 – 29 November 2025."
        ),
        "phone_eo"       : "+6281-3456-7898",
        "email_eo"       : "eventorganizer@gmail.com",
        "nama_eo"        : "Event Organizer",
        "inisial_eo"     : "EO",
        "gambar_poster"  : os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "dummy_sparta.jpg"
        ),
    },
    {
        "event_id"       : "EVT-003",
        "nama_event"     : "Kelas Karir 4.0",
        "deskripsi_singkat": "Career talk",
        "jenis_event"    : "Internal",
        "tanggal_waktu"  : "2026-07-01",
        "tanggal_display": "Tuesday, July 1",
        "waktu_display"  : "9 AM",
        "lokasi"         : "Aula Kampus Polban",
        "tipe_tiket"     : "Gratis",
        "harga_tiket"    : "0",
        "overview"       : (
            "Kelas Karir 4.0 hadir untuk mempersiapkan kamu menghadapi dunia kerja!\n\n"
            "Dapatkan insight langsung dari para profesional di bidangnya.\n\n"
            "What to Expect:\n"
            "• Panel diskusi dengan praktisi industri.\n"
            "• Workshop CV dan portofolio.\n"
            "• Sesi tanya jawab eksklusif."
        ),
        "phone_eo"       : "+6281-3456-7898",
        "email_eo"       : "eventorganizer@gmail.com",
        "nama_eo"        : "Event Organizer",
        "inisial_eo"     : "EO",
        "gambar_poster"  : os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "career_40.png"
        ),
    },
]

# Data dummy untuk Booked Events dan Liked Events (student/umum)
# Dalam implementasi nyata, data ini diambil dari tabel bookings dan likes
DUMMY_EVENTS_STUDENT = [
    {
        "event_id"       : "EVT-001",
        "nama_event"     : "Sparta Festival",
        "deskripsi_singkat": "Live painting and exhibition",
        "jenis_event"    : "External",
        "tanggal_waktu"  : "2026-05-20",  # Digunakan untuk cek apakah event sudah selesai
        "tanggal_display": "Sunday, November 30",
        "waktu_display"  : "8 AM",
        "lokasi"         : "Istana Plaza (Lt. Lower Ground)",
        "tipe_tiket"     : "Gratis",
        "harga_tiket"    : "0",
        "overview"       : (
            "SPARTA FESTIVAL Is Coming!\n\n"
            "Terbuka untuk seluruh siswa SMA/SMK dan Mahasiswa se-Bandung Raya.\n\n"
            "What to Expect:\n"
            "• Live Painting Artist: Menyaksikan kreativitas seni secara langsung.\n"
            "• Live Performance: Penampilan panggung yang akan membangun vibes positif.\n"
            "• Pameran Karya: Eksibisi karya terbaik dari anak muda Bandung.\n"
            "• GUEST STAR RAHASIA: Penampilan spesial dari bintang tamu tak terduga.\n\n"
            "Registration Info:\n"
            "• GRATIS! Terbuka untuk umum.\n"
            "• Benefit: FREE MERCHANDISE untuk kuota terbatas.\n"
            "• Periode Pendaftaran: 21 – 29 November 2025."
        ),
        "phone_eo"       : "+6281-3456-7898",
        "email_eo"       : "eventorganizer@gmail.com",
        "nama_eo"        : "Event Organizer",
        "inisial_eo"     : "EO",
        "gambar_poster"  : os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "dummy_sparta.jpg"
        ),
        "is_booked"      : True,   # Status booking awal
    },
    {
        "event_id"       : "EVT-003",
        "nama_event"     : "Kelas Karir 4.0",
        "deskripsi_singkat": "Career talk",
        "jenis_event"    : "Internal",
        "tanggal_waktu"  : "2026-07-01",
        "tanggal_display": "Tuesday, July 1",
        "waktu_display"  : "9 AM",
        "lokasi"         : "Aula Kampus Polban",
        "tipe_tiket"     : "Gratis",
        "harga_tiket"    : "0",
        "overview"       : (
            "Kelas Karir 4.0 hadir untuk mempersiapkan kamu menghadapi dunia kerja!\n\n"
            "Dapatkan insight langsung dari para profesional di bidangnya."
        ),
        "phone_eo"       : "+6281-3456-7898",
        "email_eo"       : "eventorganizer@gmail.com",
        "nama_eo"        : "Event Organizer",
        "inisial_eo"     : "EO",
        "gambar_poster"  : os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "career_40.png"
        ),
        "is_booked"      : False,
    },
]


def _apply_poster_image(label, image_source, placeholder_color="#D2E6E5"):
    """Tampilkan poster dari path lokal (sync) atau URL (async, non-blocking)."""
    source = str(image_source or "").strip()

    # Path lokal — langsung load, tidak perlu thread
    if source and not source.startswith(("http://", "https://")):
        if os.path.exists(source):
            pixmap = QPixmap(source)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    label.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )
                label.setPixmap(scaled)
                return
        label.setStyleSheet(f"background-color: {placeholder_color}; border-radius: 8px;")
        return

    # URL — set placeholder dulu, lalu load di background thread
    label.setStyleSheet(f"background-color: {placeholder_color}; border-radius: 8px;")
    if not source:
        return

    # Create thread without parent to avoid it being destroyed when label/widget is deleted
    thread = _ImageLoaderThread(source, label.size(), parent=None)

    def _on_loaded(pixmap):
        try:
            if not pixmap.isNull():
                label.setStyleSheet("border-radius: 8px;")
                label.setPixmap(pixmap)
        except RuntimeError:
            # QLabel was deleted on the main thread; ignore safely
            return

    thread.loaded.connect(_on_loaded)
    # Simpan referensi agar thread tidak di-GC sebelum selesai.
    # Gunakan dua tempat penyimpanan: di label dan di global list.
    if not hasattr(label, "_img_threads"):
        label._img_threads = []
    label._img_threads.append(thread)
    _GLOBAL_IMG_THREADS.append(thread)
    def _cleanup(t=thread):
        try:
            if hasattr(label, "_img_threads") and t in label._img_threads:
                label._img_threads.remove(t)
        except Exception:
            pass
        try:
            if t in _GLOBAL_IMG_THREADS:
                _GLOBAL_IMG_THREADS.remove(t)
        except Exception:
            pass

    thread.finished.connect(_cleanup)
    thread.start()


# ==============================================================
# CLASS YourEventsPanel
# Mewarisi QWidget — dimasukkan ke stacked_widget settings_window
#
# Menampilkan panel berbeda berdasarkan role:
#   EO      → Published Events + icon edit hover
#   Student → Booked Events (scroll horizontal) + Liked Events
# ==============================================================
class YourEventsPanel(QWidget):

    # ----------------------------------------------------------
    # SINYAL
    # minta_edit_event: dipancarkan saat EO klik icon edit
    #   → diterima settings_window/main_window untuk buka halaman edit
    # ----------------------------------------------------------
    minta_edit_event = pyqtSignal(dict)
    minta_buka_add_event = pyqtSignal()

    # ----------------------------------------------------------
    # FUNGSI __init__
    #
    # Parameter:
    #   user_data      = dictionary data user yang login
    #   stacked_widget = QStackedWidget milik settings_window
    #                    untuk navigasi ke halaman deskripsi event
    #   parent         = komponen induk
    # ----------------------------------------------------------
    def __init__(self, user_data=None, stacked_widget=None, parent=None):
        super().__init__(parent)

        self.user_data = user_data or {
            "nama"   : "",
            "role"   : ROLE_UMUM,
            "inisial": ""
        }
        self.role = self.user_data.get("role", ROLE_UMUM)
        self.stacked_widget = stacked_widget

        # Menyimpan referensi panel deskripsi yang sedang aktif
        # agar bisa dihapus saat user kembali
        self.panel_deskripsi_aktif = None

        # Menyimpan status liked events — key: event_id, value: bool
        # True = liked, False = unliked (akan hilang dari daftar)
        self.liked_status = {}

        # Memuat font GoogleSans dari assets
        self._load_fonts()

        self.setStyleSheet("background: transparent;")
        self._rendered = False  # render dilakukan saat pertama kali ditampilkan
        lang.language_changed.connect(self._retranslate)


    def _minta_buka_add_event(self):
        self.minta_buka_add_event.emit()


    def _set_label_style(self, label, size, color, bold = False):
        font = QFont(self.font_bold if bold else self.font_regular)
        font.setPointSize(size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet(f"color: {color}; background: transparent;")

    def _event_id_from(self, event):
        return str(
            event.get("event_id")
            or event.get("db_id")
            or event.get("id")
            or ""
        ).strip()

    def _is_free_ticket(self, event):
        tipe = str(event.get("tipe_tiket", "Free") or "Free").lower()
        harga = str(event.get("harga_tiket", "0") or "0").strip()
        return tipe in ("free", "gratis") or harga in ("", "0", "0.0", "None")

    def _is_event_booked(self, event):
        email = self.user_data.get("email", "")
        event_id = self._event_id_from(event)
        if not email or not event_id:
            return bool(event.get("is_booked", False))
        try:
            import db_manager
            event_date = str(event.get("tanggal_waktu") or event.get("tanggal_display") or "").strip()
            if hasattr(db_manager, "is_event_booked"):
                return db_manager.is_event_booked(email, event_id, event_date)
        except Exception as exc:
            print(f"[YourEventsPanel] Gagal cek booking event: {exc}")
        return bool(event.get("is_booked", False))

    def _book_event_from_settings(self, event):
        email = self.user_data.get("email", "")
        event_id = self._event_id_from(event)
        if not email:
            QMessageBox.warning(self, lang.t("detail.login_required_title"),
                lang.t("detail.login_required_book"))
            return False
        if not _is_mahasiswa_role(self.role):
            QMessageBox.warning(self, lang.t("detail.access_denied_title"),
                lang.t("detail.access_denied_book"))
            return False
        if not event_id:                          # <-- validasi BARU
            QMessageBox.warning(self, lang.t("your_events.booking_failed"), lang.t("your_events.event_id_missing"))
            return False
        try:
            import db_manager
            event_date = str(event.get("tanggal_waktu") or event.get("tanggal_display") or "").strip()
            if hasattr(db_manager, "book_event"):
                db_manager.book_event(email, event_id, event_date)
                event["is_booked"] = True
                return True
        except Exception as exc:
            QMessageBox.warning(self, lang.t("your_events.booking_failed"), f"{lang.t("your_events.failed_book")}\n{exc}")
            return False
        return False

    def _unbook_event_from_settings(self, event):   # <-- BARU
        email = self.user_data.get("email", "")
        event_id = self._event_id_from(event)
        if not email or not event_id:
            return False
        try:
            import db_manager
            event_date = str(event.get("tanggal_waktu") or event.get("tanggal_display") or "").strip()
            if hasattr(db_manager, "unbook_event"):
                db_manager.unbook_event(email, event_id, event_date)
                event["is_booked"] = False
                return True
        except Exception as exc:
            print(f"[YourEventsPanel] Gagal unbook event: {exc}")
        return False

    def _ticket_button_style(self, booked=False):   # <-- BARU
        if booked:
            return f"""
                QPushButton {{
                    background-color: {COLOR_PINK_BOOKED};
                    color: white; border-radius: 8px; border: none;
                    font-size: 9px; font-weight: bold;
                }}
            """
        return """
            QPushButton {
                background-color: #5D6B6B;
                color: white; border-radius: 8px; border: none;
                font-size: 9px; font-weight: bold;
            }
            QPushButton:hover { background-color: #4a5858; }
        """


    # ----------------------------------------------------------
    # FUNGSI _load_fonts()
    # Memuat font GoogleSans dari folder assets
    # Font ini digunakan di seluruh panel Your Events
    # ----------------------------------------------------------
    def _load_fonts(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets = os.path.join(BASE_DIR, "assets")

        id_regular = QFontDatabase.addApplicationFont(
            os.path.join(assets, "Inter_18pt-Regular.ttf")
        )
        id_bold = QFontDatabase.addApplicationFont(
            os.path.join(assets, "Inter_18pt-Bold.ttf")
        )

        families_regular = QFontDatabase.applicationFontFamilies(id_regular)
        families_bold    = QFontDatabase.applicationFontFamilies(id_bold)

        self.font_regular = families_regular[0] if families_regular else "Inter"
        self.font_bold    = families_bold[0]    if families_bold    else "Inter"


    # ----------------------------------------------------------
    # FUNGSI _render()
    # Membangun ulang tampilan panel berdasarkan role
    # Dipanggil saat pertama dibuat dan saat refresh diperlukan
    # ----------------------------------------------------------
    def _render(self):
        # Bersihkan layout lama jika ada
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.layout())

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Scroll utama halaman Your Events
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255,255,255,0.35);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #516465;
                min-height: 28px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        content = QWidget()
        content.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 40, 24, 40)
        layout.setSpacing(18)

        # Judul panel
        lbl_judul = QLabel(lang.t("your_events.settings_title"))
        self._set_label_style(lbl_judul, 30, C_TITLE, bold=True)
        layout.addWidget(lbl_judul)

        if _is_eo_role(self.role):
            self._render_eo(layout)
        else:
            self._render_student(layout)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self._rendered = True

    def showEvent(self, event):
        super().showEvent(event)
        if getattr(self, '_rendered', False):
            self._render()


    # ==========================================================
    # ---- TAMPILAN EVENT ORGANIZER ----
    # ==========================================================

    # ----------------------------------------------------------
    # FUNGSI _render_eo()
    # Membangun tampilan untuk Event Organizer:
    #   - Sub-judul "Published Events"
    #   - Grid kartu event yang sudah dipublikasi
    #   - Setiap kartu punya icon edit yang muncul saat hover
    # ----------------------------------------------------------
    def _render_eo(self, layout):
        lbl_sub = QLabel(lang.t("your_events.published"))
        self._set_label_style(lbl_sub, 17, C_TITLE, bold=True)
        layout.addWidget(lbl_sub)

        events = self._get_published_events()

        if not events:
            lbl_empty = QLabel(lang.t("your_events.empty_created"))
            self._set_label_style(lbl_empty, 13, C_SUBTITLE)

            lbl_buat = QLabel(lang.t("your_events.create_first"))
            self._set_label_style(lbl_buat, 13, C_TITLE, bold=True)
            lbl_buat.setTextFormat(Qt.RichText)
            lbl_buat.setCursor(Qt.PointingHandCursor)
            lbl_buat.mousePressEvent = lambda ev: self._minta_buka_add_event()

            layout.addWidget(lbl_empty)
            layout.addWidget(lbl_buat)
            return

        grid_container = QWidget()
        grid_container.setStyleSheet("background: transparent;")

        grid = QGridLayout(grid_container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(GRID_H_SPACING)
        grid.setVerticalSpacing(GRID_V_SPACING)
        for i, event in enumerate(events):
            kartu = self._buat_kartu_eo(event)
            row = i // GRID_MAX_COLS
            col = i % GRID_MAX_COLS
            grid.addWidget(kartu, row, col)

        layout.addWidget(grid_container)


    # ----------------------------------------------------------
    # FUNGSI _buat_kartu_eo()
    # Membuat satu kartu event untuk EO dengan:
    #   - Poster event
    #   - Badge jenis event (Internal/External)
    #   - Icon edit yang muncul saat hover (tersembunyi secara default)
    #   - Nama event dan deskripsi singkat di bawah poster
    #
    # Parameter:
    #   event = dictionary data satu event
    #
    # Return: QWidget kartu siap pakai
    # ----------------------------------------------------------
    def _buat_kartu_eo(self, event):
        kartu = QWidget()
        kartu.setFixedWidth(CARD_WIDTH)
        kartu.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ---- AREA POSTER (relatif untuk overlay badge + edit) ----
        poster_container = QWidget()
        poster_container.setFixedSize(CARD_WIDTH, EO_POSTER_H)
        poster_container.setStyleSheet("background: transparent;")

        # Gambar poster
        lbl_poster = QLabel(poster_container)
        lbl_poster.setFixedSize(CARD_WIDTH, EO_POSTER_H)
        lbl_poster.setScaledContents(True)
        lbl_poster.setStyleSheet("border-radius: 8px;")

        # Load gambar poster dari path lokal
        path = event.get("gambar_poster", "")
        if path and os.path.exists(path):
            lbl_poster.setPixmap(QPixmap(path))
        else:
            # Fallback: background abu-abu jika gambar tidak ditemukan
            lbl_poster.setStyleSheet(
                "background-color: #D2E6E5; border-radius: 8px;"
            )

        # Badge jenis event (Internal/External) — pojok kiri atas poster
        badge = QLabel(event.get("jenis_event", ""), poster_container)
        badge.move(8, 8)
        badge.setFixedSize(62, 18)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFont(QFont(self.font_regular, 8))
        badge.setStyleSheet("""
            background-color: #4a90d9;
            color: white;
            border-radius: 4px;
            font-size: 9px;
        """)

        # Icon edit — pojok kanan atas poster
        # Tersembunyi secara default, muncul saat mouse hover ke poster
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        btn_edit = QPushButton(poster_container)
        btn_edit.setIcon(QIcon(os.path.join(BASE_DIR, "assets", "edit.png")))
        btn_edit.setIconSize(QSize(18, 18))
        btn_edit.setFixedSize(30, 30)
        btn_edit.move(CARD_WIDTH - 38, 8)  
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: white;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setVisible(False)  # Tersembunyi secara default

        # Saat diklik → pancarkan sinyal minta_edit_event membawa data event
        btn_edit.clicked.connect(
            lambda checked, e=event: self.minta_edit_event.emit(e)
        )

        # ---- HOVER EFFECT ----
        # Override event mouse enter/leave pada poster_container
        # agar icon edit muncul/hilang saat mouse masuk/keluar area poster

        def on_enter(ev, btn=btn_edit):
            btn.setVisible(True)

        def on_leave(ev, btn=btn_edit):
            btn.setVisible(False)

        poster_container.enterEvent = lambda ev, btn=btn_edit: btn.setVisible(True)
        poster_container.leaveEvent = lambda ev, btn=btn_edit: btn.setVisible(False)
        poster_container.setCursor(Qt.PointingHandCursor)

        # ---- TEKS DI BAWAH POSTER ----
        lbl_nama = QLabel(event.get("nama_event", ""))
        lbl_nama.setFont(QFont(self.font_bold, 10))
        lbl_nama.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        lbl_nama.setWordWrap(True)

        lbl_deskripsi = QLabel(event.get("deskripsi_singkat", ""))
        lbl_deskripsi.setFont(QFont(self.font_regular, 9))
        lbl_deskripsi.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        lbl_deskripsi.setWordWrap(True)

        layout.addWidget(poster_container)
        layout.addWidget(lbl_nama)
        layout.addWidget(lbl_deskripsi)

        return kartu


    # ==========================================================
    # ---- TAMPILAN STUDENT / UMUM ----
    # ==========================================================

    # ----------------------------------------------------------
    # FUNGSI _render_student()
    # Membangun tampilan untuk mahasiswa/umum:
    #   - Sub-judul "My Events"
    #   - Booked Events: scroll horizontal, hilang jika sudah selesai
    #   - Liked Events: grid kartu dengan aksi unlike
    # ----------------------------------------------------------
    def _render_student(self, layout):
        lbl_sub = QLabel(lang.t("your_events.my_events"))
        self._set_label_style(lbl_sub, 15, C_SUBTITLE, bold=True)
        layout.addWidget(lbl_sub)

        # ---- BOOKED EVENTS ----
        lbl_booked = QLabel(lang.t("your_events.booked_events"))
        self._set_label_style(lbl_booked, 17, C_TITLE, bold=True)
        layout.addWidget(lbl_booked)

        booked_grid = self._buat_booked_scroll()
        layout.addWidget(booked_grid)

        layout.addSpacing(34)

        # ---- LIKED EVENTS ----
        lbl_liked = QLabel(lang.t("your_events.liked_events"))
        self._set_label_style(lbl_liked, 17, C_TITLE, bold=True)
        layout.addWidget(lbl_liked)

        self.liked_container = QWidget()
        self.liked_container.setStyleSheet("background: transparent;")
        self.liked_container.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.liked_container)

        self._render_liked_grid()


    # ----------------------------------------------------------
    # FUNGSI _buat_booked_scroll()
    # Membuat area scroll horizontal untuk Booked Events
    # Event yang sudah selesai (tanggal sudah lewat) tidak ditampilkan
    #
    # Return: QScrollArea siap pakai
    # ----------------------------------------------------------
    def _buat_booked_scroll(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")

        booked_events = self._get_booked_events()

        # Filter event yang sudah selesai berdasarkan tanggal
        from datetime import date
        today = date.today()
        aktif = []

        for e in booked_events:
            try:
                tgl_str = e.get("tanggal_waktu", "")
                tgl = date.fromisoformat(tgl_str[:10])
                if tgl >= today:
                    aktif.append(e)
            except Exception:
                aktif.append(e)

        if not aktif:
            vbox = QVBoxLayout(container)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(0)

            lbl_empty = QLabel(lang.t("your_events.empty_booked"))
            self._set_label_style(lbl_empty, 13, C_SUBTITLE)
            vbox.addWidget(lbl_empty)
            return container

        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(GRID_H_SPACING)
        grid.setVerticalSpacing(GRID_V_SPACING)
        grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        for i, event in enumerate(aktif):
            kartu = self._buat_kartu_booked(event) 
            row = i // GRID_MAX_COLS
            col = i % GRID_MAX_COLS
            grid.addWidget(kartu, row, col)

        return container


    # ----------------------------------------------------------
    # FUNGSI _buat_kartu_booked()
    # Membuat satu kartu untuk Booked Events (scroll horizontal)
    # Kartu berisi poster kecil + nama + deskripsi
    #
    # Parameter:
    #   event = dictionary data satu event
    #
    # Return: QWidget kartu siap pakai
    # ----------------------------------------------------------
    def _buat_kartu_booked(self, event):
        kartu = QWidget()
        kartu.setFixedWidth(CARD_WIDTH)     # 170, tidak ada setFixedHeight
        kartu.setStyleSheet("background: transparent;")
        kartu.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)                # dari 6

        lbl_poster = QLabel()
        lbl_poster.setFixedSize(CARD_WIDTH, BOOKED_POSTER_H)  # 170 x 205
        lbl_poster.setScaledContents(True)
        lbl_poster.setStyleSheet("border-radius: 8px;")

        path = event.get("gambar_poster", "")
        if path and os.path.exists(path):
            lbl_poster.setPixmap(QPixmap(path))
        else:
            _apply_poster_image(lbl_poster, path, placeholder_color="#D2E6E5")

        lbl_nama = QLabel(event.get("nama_event", ""))
        self._set_label_style(lbl_nama, 10, "#243333", bold=True)
        lbl_nama.setWordWrap(True)

        lbl_desk = QLabel(event.get("deskripsi_singkat", ""))
        self._set_label_style(lbl_desk, 9, C_SUBTITLE)   # font size 9 (dari 10)
        lbl_desk.setWordWrap(True)

        layout.addWidget(lbl_poster)
        layout.addWidget(lbl_nama)
        layout.addWidget(lbl_desk)

        kartu.mousePressEvent = lambda ev, e=event: self._buka_deskripsi(e)
        return kartu 


    # ----------------------------------------------------------
    # FUNGSI _render_liked_grid()
    # Membangun grid kartu Liked Events di dalam self.liked_container
    # Dipanggil saat pertama render dan saat user unlike sebuah event
    # ----------------------------------------------------------
    def _render_liked_grid(self):
        # Bersihkan layout lama di liked_container
        if self.liked_container.layout():
            old_layout = self.liked_container.layout()

            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            QWidget().setLayout(old_layout)

        grid = QGridLayout(self.liked_container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(GRID_H_SPACING)
        grid.setVerticalSpacing(GRID_V_SPACING)
        grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        liked_events = self._get_liked_events()

        tampil = liked_events

        if not tampil:
            lbl_empty = QLabel(lang.t("your_events.empty_liked"))
            self._set_label_style(lbl_empty, 13, C_SUBTITLE)
            grid.addWidget(lbl_empty, 0, 0)
            return

        for i, event in enumerate(tampil):
            kartu = self._buat_kartu_liked(event) 
            row = i // GRID_MAX_COLS
            col = i % GRID_MAX_COLS
            grid.addWidget(kartu, row, col) 


    # ----------------------------------------------------------
    # FUNGSI _buat_kartu_liked()
    # Membuat satu kartu untuk Liked Events dengan:
    #   - Poster besar (W: 200, H: 260) yang bisa diklik
    #     → buka halaman deskripsi event
    #   - Icon hati (liked/unliked) interaktif
    #   - Bar bawah: harga | tanggal | tombol Get Ticket/Booked
    #
    # Parameter:
    #   event = dictionary data satu event
    #
    # Return: QWidget kartu siap pakai
    # ----------------------------------------------------------
    def _buat_kartu_liked(self, event):
        kartu = QWidget()
        kartu.setFixedWidth(CARD_WIDTH)
        kartu.setStyleSheet("background: transparent;")
        kartu.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        poster_container = QWidget()
        poster_container.setFixedSize(CARD_WIDTH, LIKED_POSTER_H)
        poster_container.setStyleSheet("background: transparent;")
        poster_container.setCursor(Qt.PointingHandCursor)

        lbl_poster = QLabel(poster_container)
        lbl_poster.setFixedSize(CARD_WIDTH, LIKED_POSTER_H)
        lbl_poster.setScaledContents(True)
        lbl_poster.setStyleSheet("border-radius: 10px;")

        path = event.get("gambar_poster", "")
        if path and os.path.exists(path):
            lbl_poster.setPixmap(QPixmap(path))
        else:
            lbl_poster.setStyleSheet(
                "background-color: #D2E6E5; border-radius: 10px;"
            )

        btn_hati = QPushButton(poster_container)
        btn_hati.setFixedSize(28, 28)
        btn_hati.move(CARD_WIDTH - 34, LIKED_POSTER_H - 34)
        btn_hati.setStyleSheet("background: transparent; border: none;")
        btn_hati.setCursor(Qt.PointingHandCursor)

        liked_icon_path = os.path.join(BASE_DIR, "assets", "liked.png")
        unliked_icon_path = os.path.join(BASE_DIR, "assets", "unliked.png")
        btn_hati.setIcon(QIcon(liked_icon_path))
        btn_hati.setIconSize(QSize(24, 24))

        def on_hati_diklik(checked, ev=event):
            event_id = str(ev.get("event_id", ""))
            event_date = str(ev.get("tanggal_waktu") or ev.get("tanggal_display") or "").strip()
            email = self.user_data.get("email", "")

            try:
                import db_manager
                if email and event_id and hasattr(db_manager, "unlike_event"):
                    db_manager.unlike_event(email, event_id, event_date)
            except Exception as e:
                print(f"[YourEventsPanel] Gagal unlike event: {e}")

            self.liked_status[f"{event_id}|||{event_date}"] = False
            self._render_liked_grid()

        btn_hati.clicked.connect(on_hati_diklik)

        bar = QWidget(poster_container)
        bar.setFixedSize(CARD_WIDTH, 56)
        bar.move(0, LIKED_POSTER_H - 56)
        bar.setStyleSheet(
            "background-color: rgba(203, 213, 224, 0.42); border-radius: 0px;"
        )

        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(8, 6, 8, 6)
        bar_layout.setSpacing(4)

        kiri_layout = QVBoxLayout()
        kiri_layout.setSpacing(1)

        tipe = event.get("tipe_tiket", "Free")
        harga = event.get("harga_tiket", "0")
        teks_harga = "Free" if self._is_free_ticket(event) else f"IDR {harga}"

        lbl_harga = QLabel(teks_harga)
        lbl_harga.setFont(QFont(self.font_bold, 12))
        lbl_harga.setStyleSheet("color: black; background: transparent;")

        tgl = event.get("tanggal_display", "") or event.get("tanggal_waktu", "")
        wkt = event.get("waktu_display", "")
        lbl_tgl = QLabel(f"{tgl}  |  {wkt}".strip(" |"))
        lbl_tgl.setFont(QFont(self.font_regular, 7))
        lbl_tgl.setStyleSheet("color: #454545; background: transparent;")

        kiri_layout.addWidget(lbl_harga)
        kiri_layout.addWidget(lbl_tgl)

        sudah_booked = self._is_event_booked(event)
        event["is_booked"] = sudah_booked

        btn_tiket = QPushButton(lang.t("detail.booked") if sudah_booked else lang.t("your_events.get_ticket"))
        btn_tiket.setFixedSize(84, 34)
        btn_tiket.setCursor(Qt.PointingHandCursor)
        btn_tiket.setFont(QFont(self.font_bold, 11))
        btn_tiket.setStyleSheet(self._ticket_button_style(sudah_booked))

        def on_tiket_diklik(checked, ev=event, btn=btn_tiket):
            if not self._is_free_ticket(ev):
                QMessageBox.information(
                    self,
                    "Payment",
                    "Payment feature will be available soon!"
                )
                return

            if self._book_event_from_settings(ev):
                btn.setText(lang.t("detail.booked"))
                btn.setStyleSheet(self._ticket_button_style(True))
                QTimer.singleShot(0, self._render)

        btn_tiket.clicked.connect(on_tiket_diklik)

        bar_layout.addLayout(kiri_layout)
        bar_layout.addStretch()
        bar_layout.addWidget(btn_tiket)

        lbl_nama = QLabel(event.get("nama_event", ""))
        self._set_label_style(lbl_nama, 10, "#243333", bold=True)
        lbl_nama.setWordWrap(True)

        lbl_desk = QLabel(event.get("deskripsi_singkat", ""))
        self._set_label_style(lbl_desk, 9, C_SUBTITLE)
        lbl_desk.setWordWrap(True)

        layout.addWidget(poster_container)
        layout.addSpacing(9)
        layout.addWidget(lbl_nama)
        layout.addWidget(lbl_desk)

        kartu.mousePressEvent = lambda ev, e=event: self._buka_deskripsi(e)
        poster_container.mousePressEvent = lambda ev, e=event: self._buka_deskripsi(e)

        return kartu


    # ==========================================================
    # ---- HALAMAN DESKRIPSI EVENT ----
    # ==========================================================

    # ----------------------------------------------------------
    # FUNGSI _buka_deskripsi()
    # Membuat panel deskripsi event dan menampilkannya
    # di stacked_widget menggantikan panel Your Events sementara
    #
    # Parameter:
    #   event = dictionary data event yang diklik
    # ----------------------------------------------------------
    def _buka_deskripsi(self, event):
        dialog = QDialog(self)
        dialog.setModal(True)
        dialog.setWindowTitle("Event Detail")
        dialog.setFixedSize(980, 720)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #D2E6E5,
                    stop:0.72 #D2E6E5,
                    stop:1 #F7CBCA
                );
                border-radius: 18px;
            }
        """)

        root = QVBoxLayout(dialog)
        root.setContentsMargins(20, 18, 20, 20)
        root.setSpacing(0)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # ---- TOPBAR DESKRIPSI: tombol back ----
        topbar = QWidget()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet("background: transparent;")

        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)

        btn_back = QPushButton()
        btn_back.setIcon(QIcon(os.path.join(BASE_DIR, "assets", "back.png")))
        btn_back.setIconSize(QSize(24, 24))
        btn_back.setFixedSize(36, 36)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
        """)
        btn_back.clicked.connect(dialog.reject)

        topbar_layout.addWidget(btn_back)
        topbar_layout.addStretch()
        root.addWidget(topbar)

        # ---- KONTEN DESKRIPSI (scrollable) ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        konten = QWidget()
        konten.setStyleSheet("background: transparent;")
        konten_layout = QHBoxLayout(konten)
        konten_layout.setContentsMargins(30, 20, 30, 30)
        konten_layout.setSpacing(30)

        # ---- KOLOM KIRI: Poster + bar harga/tiket ----
        kiri = QWidget()
        kiri.setFixedWidth(260)
        kiri.setStyleSheet("background: transparent;")
        kiri_layout = QVBoxLayout(kiri)
        kiri_layout.setContentsMargins(0, 0, 0, 0)
        kiri_layout.setSpacing(10)

        # Poster besar
        lbl_poster = QLabel()
        lbl_poster.setFixedSize(220, 286)
        lbl_poster.setScaledContents(True)
        lbl_poster.setStyleSheet("border-radius: 10px;")

        path = event.get("gambar_poster", "")
        if path and os.path.exists(path):
            lbl_poster.setPixmap(QPixmap(path))
        else:
            lbl_poster.setStyleSheet(
                "background-color: #D2E6E5; border-radius: 10px;"
            )

        # Icon hati di bawah poster
        btn_hati_desk = QPushButton()
        liked_icon = os.path.join(BASE_DIR, "assets", "liked.png")
        unliked_icon = os.path.join(BASE_DIR, "assets", "unliked.png")
        btn_hati_desk.setIconSize(QSize(28, 28))
        btn_hati_desk.setFixedSize(32, 32)
        btn_hati_desk.setStyleSheet("background: transparent; border: none;")
        btn_hati_desk.setCursor(Qt.PointingHandCursor)

        # Status liked dicek dari DB dulu
        event_id_popup = self._event_id_from(event)
        event_date_popup = str(event.get("tanggal_waktu") or event.get("tanggal_display") or "").strip()
        email_popup = self.user_data.get("email", "")
        liked_awal = self.liked_status.get(f"{event_id_popup}|||{event_date_popup}", False)

        try:
            import db_manager
            if email_popup and event_id_popup and hasattr(db_manager, "is_event_liked"):
                liked_awal = db_manager.is_event_liked(email_popup, event_id_popup, event_date_popup)
        except Exception as exc:
            print(f"[YourEventsPanel] Gagal cek like event: {exc}")

        is_liked = [liked_awal]
        btn_hati_desk.setIcon(QIcon(liked_icon if liked_awal else unliked_icon))

        def toggle_hati_desk(checked, btn=btn_hati_desk):
            is_liked[0] = not is_liked[0]
            self.liked_status[f"{event_id_popup}|||{event_date_popup}"] = is_liked[0]

            try:
                import db_manager
                if email_popup and event_id_popup:
                    if is_liked[0] and hasattr(db_manager, "like_event"):
                        db_manager.like_event(email_popup, event_id_popup, event_date_popup)
                    elif not is_liked[0] and hasattr(db_manager, "unlike_event"):
                        db_manager.unlike_event(email_popup, event_id_popup, event_date_popup)
            except Exception as exc:
                print(f"[YourEventsPanel] Gagal update like event: {exc}")

            btn.setIcon(QIcon(liked_icon if is_liked[0] else unliked_icon))
            QTimer.singleShot(0, self._render_liked_grid)

        btn_hati_desk.clicked.connect(toggle_hati_desk)

        # Bar harga + Get Ticket / Booked
        bar_desk = QWidget()
        bar_desk.setFixedSize(220, 70)
        bar_desk.setStyleSheet(
            "background-color: rgba(203, 213, 224, 0.4); border-radius: 8px;"
        )
        bar_desk_layout = QHBoxLayout(bar_desk)
        bar_desk_layout.setContentsMargins(10, 8, 10, 8)
        bar_desk_layout.setSpacing(4)

        kiri2 = QVBoxLayout()
        tipe = event.get("tipe_tiket", "Gratis")
        harga = event.get("harga_tiket", "0")
        teks_harga = "Free" if self._is_free_ticket(event) else f"IDR {harga}"

        lbl_harga2 = QLabel(teks_harga)
        lbl_harga2.setFont(QFont(self.font_bold, 16))
        lbl_harga2.setStyleSheet("color: black; background: transparent;")

        tgl2 = event.get("tanggal_display", "")
        wkt2 = event.get("waktu_display", "")
        lbl_tgl2 = QLabel(f"{tgl2}  |  {wkt2}")
        lbl_tgl2.setFont(QFont(self.font_regular, 8))
        lbl_tgl2.setStyleSheet("color: #454545; background: transparent;")

        kiri2.addWidget(lbl_harga2)
        kiri2.addWidget(lbl_tgl2)

        sudah_booked = self._is_event_booked(event)
        event["is_booked"] = sudah_booked

        btn_tiket2 = QPushButton(lang.t("detail.booked") if sudah_booked else lang.t("your_events.get_ticket"))
        btn_tiket2.setFixedSize(100, 44)
        btn_tiket2.setCursor(Qt.PointingHandCursor)
        btn_tiket2.setFont(QFont(self.font_bold, 9))
        btn_tiket2.setStyleSheet(self._ticket_button_style(sudah_booked))

        def on_tiket2_diklik(checked, ev=event, btn=btn_tiket2):
            if not self._is_free_ticket(ev):
                QMessageBox.information(
                    self, "Payment", "Payment feature will be available soon!"
                )
                return

            if self._book_event_from_settings(ev):
                btn.setText(lang.t("detail.booked"))
                btn.setStyleSheet(self._ticket_button_style(True))
                QTimer.singleShot(0, self._render)

        btn_tiket2.clicked.connect(on_tiket2_diklik)

        bar_desk_layout.addLayout(kiri2)
        bar_desk_layout.addStretch()
        bar_desk_layout.addWidget(btn_tiket2)

        kiri_layout.addWidget(lbl_poster)
        kiri_layout.addWidget(btn_hati_desk, alignment=Qt.AlignRight)
        kiri_layout.addWidget(bar_desk)
        kiri_layout.addStretch()

        # ---- KOLOM KANAN: Info detail event ----
        kanan = QWidget()
        kanan.setStyleSheet("background: transparent;")
        kanan_layout = QVBoxLayout(kanan)
        kanan_layout.setContentsMargins(0, 0, 0, 0)
        kanan_layout.setSpacing(10)

        # 1. Judul event
        lbl_judul = QLabel(event.get("nama_event", ""))
        lbl_judul.setFont(QFont(self.font_bold, 28))
        lbl_judul.setStyleSheet("color: black;")
        lbl_judul.setWordWrap(True)
        kanan_layout.addWidget(lbl_judul)

        # 2. Profile EO
        eo_widget = QWidget()
        eo_widget.setStyleSheet("background: transparent;")
        eo_layout = QHBoxLayout(eo_widget)
        eo_layout.setContentsMargins(0, 0, 0, 0)
        eo_layout.setSpacing(10)

        inisial_eo = event.get("inisial_eo", "EO")
        lbl_avatar = QLabel(inisial_eo)
        lbl_avatar.setFixedSize(36, 36)
        lbl_avatar.setAlignment(Qt.AlignCenter)
        lbl_avatar.setStyleSheet(f"""
            background-color: {COLOR_TEAL_DARK};
            color: white; font-weight: bold;
            font-size: 13px; border-radius: 18px;
        """)

        nama_eo = event.get("nama_eo", "Event Organizer")
        lbl_by = QLabel(f'<span style="color:#454545;">by </span>'
                        f'<span style="color:black; font-weight:bold;">{nama_eo}</span>')
        lbl_by.setFont(QFont(self.font_regular, 11))
        lbl_by.setTextFormat(Qt.RichText)

        eo_layout.addWidget(lbl_avatar)
        eo_layout.addWidget(lbl_by)
        eo_layout.addStretch()
        kanan_layout.addWidget(eo_widget)

        # 3. Tempat, Tanggal, Phone, Email
        def baris_icon(icon_name, teks):
            w = QWidget()
            w.setStyleSheet("background: transparent;")
            hl = QHBoxLayout(w)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(8)
            icon_path = os.path.join(BASE_DIR, "assets", f"{icon_name}.png")
            lbl_icon = QLabel()
            lbl_icon.setPixmap(QIcon(icon_path).pixmap(QSize(18, 18)))
            lbl_icon.setFixedSize(20, 20)
            lbl_icon.setStyleSheet("background: transparent;")
            lbl_teks = QLabel(teks)
            lbl_teks.setFont(QFont(self.font_regular, 10))
            lbl_teks.setStyleSheet("color: #454545; background: transparent;")
            hl.addWidget(lbl_icon)
            hl.addWidget(lbl_teks)
            hl.addStretch()
            return w

        kanan_layout.addWidget(
            baris_icon("place", event.get("lokasi", ""))
        )
        kanan_layout.addWidget(
            baris_icon(
                "calendar",
                f"{event.get('tanggal_display', '')}  |  {event.get('waktu_display', '')}"
            )
        )

        # Phone dan email dalam satu baris
        contact_widget = QWidget()
        contact_widget.setStyleSheet("background: transparent;")
        contact_layout = QHBoxLayout(contact_widget)
        contact_layout.setContentsMargins(0, 0, 0, 0)
        contact_layout.setSpacing(20)
        contact_layout.addWidget(
            baris_icon("phone", event.get("phone_eo", ""))
        )
        contact_layout.addWidget(
            baris_icon("email", event.get("email_eo", ""))
        )
        contact_layout.addStretch()
        kanan_layout.addWidget(contact_widget)

        # 4. Overview
        lbl_overview_title = QLabel(lang.t("detail.overview"))
        lbl_overview_title.setFont(QFont(self.font_bold, 18))
        lbl_overview_title.setStyleSheet("color: black;")
        kanan_layout.addWidget(lbl_overview_title)

        # 5. Konten overview
        lbl_overview = QLabel(event.get("overview", ""))
        lbl_overview.setFont(QFont(self.font_regular, 9))
        lbl_overview.setStyleSheet("color: #333333;")
        lbl_overview.setWordWrap(True)
        lbl_overview.setTextFormat(Qt.PlainText)
        kanan_layout.addWidget(lbl_overview)

        kanan_layout.addStretch()

        konten_layout.addWidget(kiri)
        konten_layout.addWidget(kanan, stretch=1)

        scroll.setWidget(konten)
        root.addWidget(scroll, stretch=1)

        dialog.exec_()
        self._render()   # refresh panel setelah dialog ditutup

    # ---------------------------------------------------------------------
    # FUNGSI _show_detail_popup()
    # Dipanggil saat user Mahasiswa klik card event di Your Event Settings
    # Kembali ke panel Your Events dan hapus panel deskripsi
    # ---------------------------------------------------------------------
    def _show_detail_popup(self, event):
        dialog = QDialog(self)
        dialog.setModal(True)
        dialog.setWindowTitle("Event Detail")
        dialog.resize(980, 720)
        dialog.setStyleSheet("""
            QDialog {
                background: #F8FBFB;
                border-radius: 18px;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # kalau kamu punya widget detail event yang sekarang dipakai di page lain
        detail_widget = DetailEventPage()
        detail_widget.set_data(event)

        # kalau perlu kirim context login/user
        if hasattr(detail_widget, "current_user_email"):
            detail_widget.current_user_email = self.user_data.get("email", "")
        if hasattr(detail_widget, "current_user_role"):
            detail_widget.current_user_role = self.user_role

        layout.addWidget(detail_widget)
        dialog.exec_()


    # ----------------------------------------------------------
    # FUNGSI _tutup_deskripsi()
    # Dipanggil saat user klik tombol back di halaman deskripsi
    # Kembali ke panel Your Events dan hapus panel deskripsi
    # ----------------------------------------------------------
    def _tutup_deskripsi(self):
        self.stacked_widget.setCurrentWidget(self)
        if self.panel_deskripsi_aktif:
            self.stacked_widget.removeWidget(self.panel_deskripsi_aktif)
            self.panel_deskripsi_aktif.deleteLater()
            self.panel_deskripsi_aktif = None


    # ==========================================================
    # ---- FUNGSI DATA ----
    # Fungsi-fungsi di bawah mengembalikan data event.
    # Saat database siap, ganti return value-nya saja —
    # tampilan tidak perlu diubah sama sekali.
    # ==========================================================

    # ----------------------------------------------------------
    # FUNGSI _get_published_events()
    # Mengambil event milik EO dari database dengan 3 skenario:
    #
    #   Skenario 1 — EO belum pernah add event sama sekali:
    #     → Query ke database tidak menemukan event apapun
    #     → Return list kosong []
    #
    #   Skenario 2 — EO sudah add event tapi belum di-approve admin:
    #     → Event ada di database dengan status "pending" atau "rejected"
    #     → Filter hanya status "approved", hasilnya tetap kosong []
    #     → Return list kosong [] (tampilan sama seperti skenario 1)
    #
    #   Skenario 3 — EO sudah add event dan sudah di-approve admin:
    #     → Event ada di database dengan status "approved"
    #     → Return list berisi event yang sudah disetujui
    #
    # Query menggunakan email EO sebagai identifier karena
    # account_db.check_login() hanya mengembalikan role, tidak user_id.
    # Email EO disimpan di kolom email_eo di tabel events saat add event.
    # ----------------------------------------------------------
    def _get_published_events(self):
        try:
            import db_manager

            # Ambil email EO dari user_data yang dikirim saat login
            # Email ini yang dipakai sebagai identifier di tabel events
            email_eo = self.user_data.get("email", "")

            if not email_eo:
                # Tidak ada email → tidak bisa query → tampilkan kosong
                return []

            # Query semua event milik EO ini yang sudah di-approve
            # Filter ganda: email_eo cocok DAN status = "approved"
            # Skenario 1 & 2 akan menghasilkan list kosong dari sini
            conn = __import__("sqlite3").connect(db_manager.DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM events
                WHERE email_eo = ? AND status = 'approved'
                ORDER BY tanggal_waktu ASC
            """, (email_eo,))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return []

            # Konversi rows ke list of dict agar format sama
            # dengan yang dipakai oleh _buat_kartu_eo()
            hasil = []
            for row in rows:
                # db_manager.row_to_dict butuh cursor dengan description
                # Buat ulang query untuk dapat cursor yang valid
                conn2 = __import__("sqlite3").connect(db_manager.DB_NAME)
                c2 = conn2.cursor()
                c2.execute("SELECT * FROM events WHERE id = ?", (row[0],))
                r2 = c2.fetchone()
                if r2:
                    event_dict = db_manager.row_to_dict(c2, r2)
                    hasil.append(event_dict)
                conn2.close()

            return hasil

        except Exception as e:
            # Jika database belum ada atau error apapun,
            # jangan crash — tampilkan kosong saja
            print(f"[YourEventsPanel] Error mengambil published events: {e}")
            return []


    # ----------------------------------------------------------
    # FUNGSI _get_booked_events()
    # Mengembalikan list event yang sudah di-booking oleh student
    #
    # CATATAN untuk sambung ke database:
    #   import db_manager
    #   return db_manager.get_booked_events(
    #       self.user_data.get("user_id")
    #   )
    # ----------------------------------------------------------
    def _get_booked_events(self):
        """
        Mengambil event yang sudah di-booking oleh student dari database.
        Query ke tabel bookings JOIN events berdasarkan email user.

        CATATAN: Saat ini query menggunakan email untuk lookup user_id,
        karena main_window hanya menyimpan email di user_data.
        """
        try:
            import db_manager, sqlite3
            email = self.user_data.get("email", "")
            if not email:
                return []

            conn = sqlite3.connect(db_manager.DB_NAME)
            cursor = conn.cursor()

            # Cari user_id dari tabel users berdasarkan email
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user_row = cursor.fetchone()
            conn.close()

            if not user_row:
                return []

            user_id = user_row[0]
            # Gunakan fungsi db_manager yang sudah ada
            return db_manager.get_booked_events(user_id)

        except Exception as e:
            print(f"[YourEventsPanel] Error ambil booked events: {e}")
            return []


    # ----------------------------------------------------------
    # FUNGSI _get_liked_events()
    # Mengembalikan list event yang di-liked oleh student
    #
    # CATATAN untuk sambung ke database:
    #   import db_manager
    #   return db_manager.get_liked_events(
    #       self.user_data.get("user_id")
    #   )
    # ----------------------------------------------------------
    def _get_liked_events(self):
        """
        Mengambil event yang di-liked oleh student dari database.
        Query ke tabel likes JOIN events berdasarkan email user.
        """
        try:
            import db_manager, sqlite3
            email = self.user_data.get("email", "")
            if not email:
                return []

            conn = sqlite3.connect(db_manager.DB_NAME)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user_row = cursor.fetchone()
            conn.close()

            if not user_row:
                return []

            user_id = user_row[0]
            return db_manager.get_liked_events(user_id)

        except Exception as e:
            print(f"[YourEventsPanel] Error ambil liked events: {e}")
            return []
    
    def _retranslate(self, _code=""):
        if self._rendered and hasattr(self, "_render"):
            self._render()


# ==============================================================
# BLOK TESTING MANDIRI
# Jalankan: python settings/your_events_window.py
# Ganti "role" untuk test tampilan EO vs student
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dialog = QDialog()
    dialog.setWindowTitle("Your Events - Preview")
    dialog.setFixedSize(700, 650)
    dialog.setStyleSheet("""
        QDialog {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #BDD7D8, stop:0.5 #D6E6E6,
                stop:0.75 #D2E6E5, stop:1 #F7CBCA
            );
        }
    """)

    stacked = QStackedWidget(dialog)
    stacked.setGeometry(0, 0, 700, 650)
    stacked.setStyleSheet("background: transparent;")

    # Ganti role untuk test:
    # ROLE_ORGANIZER → tampilan EO
    # ROLE_MAHASISWA → tampilan student
    user_dummy = {
        "nama"   : "Event Organizer",
        "role"   : ROLE_ORGANIZER,
        "inisial": "EO"
    }

    panel = YourEventsPanel(user_data=user_dummy, stacked_widget=stacked)
    stacked.addWidget(panel)
    stacked.setCurrentWidget(panel)

    dialog.show()
    sys.exit(app.exec_())