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

# Tambahkan root ke sys.path agar bisa import dari luar folder settings/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# ==============================================================
# KONSTANTA WARNA
# ==============================================================
COLOR_GRAY_LIGHT   = "#D2E6E5"
COLOR_TEAL_DARK    = "#516465"
COLOR_TEXT_PRIMARY = "#5D6B6B"
COLOR_TEXT_MUTED   = "#9AABAB"
COLOR_DIVIDER      = "#D2E6E5"
COLOR_PINK_BOOKED  = "#EAA4A6"   # Warna tombol Booked setelah di-klik


# ==============================================================
# KONSTANTA ROLE USER
# ==============================================================
ROLE_ORGANIZER = "eo"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM      = "umum"


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
        self._render()


    def _minta_buka_add_event(self):
        self.minta_buka_add_event.emit()


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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)

        # Judul panel
        lbl_judul = QLabel("Your Events Settings")
        lbl_judul.setFont(QFont(self.font_bold, 24))
        lbl_judul.setStyleSheet("color: #516465; font-weight: bold;")
        layout.addWidget(lbl_judul)

        # Render konten sesuai role
        if self.role == ROLE_ORGANIZER:
            self._render_eo(layout)
        else:
            self._render_student(layout)


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

        lbl_sub = QLabel("Published Events")
        lbl_sub.setFont(QFont(self.font_bold, 16))
        lbl_sub.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_sub)

        events = self._get_published_events()

        # Jika belum ada event yang approved (skenario 1 & 2):
        # Tampilkan pesan dengan dua bagian:
        #   - Kalimat pertama: teks biasa
        #   - "Create your first event now!": underline + pointer + klik → Add Event
        if not events:
            # Baris pertama: teks biasa abu-abu
            lbl_empty = QLabel("You haven't created any events yet!")
            lbl_empty.setFont(QFont(self.font_regular, 13))
            lbl_empty.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")

            # Baris kedua: "Create your first event now!" dengan underline
            # Menggunakan QLabel dengan RichText agar bisa underline tanpa QPushButton
            # tapi tetap bisa diklik via mousePressEvent
            lbl_buat = QLabel('<u>Create your first event now!</u>')
            lbl_buat.setFont(QFont(self.font_regular, 13))
            lbl_buat.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            lbl_buat.setTextFormat(Qt.RichText)
            lbl_buat.setCursor(Qt.PointingHandCursor)

            # Klik pada label → pancarkan sinyal ke main_window untuk buka Add Event
            lbl_buat.mousePressEvent = lambda ev: self._minta_buka_add_event()

            layout.addWidget(lbl_empty)
            layout.addWidget(lbl_buat)
            layout.addStretch()
            return

        # Area scroll untuk grid kartu
        # Scroll hanya dibuat jika ada events
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Susun kartu dalam grid 3 kolom
        for i, event in enumerate(events):
            kartu = self._buat_kartu_eo(event)
            grid.addWidget(kartu, i // 3, i % 3)

        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)


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
        kartu.setFixedWidth(200)
        kartu.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ---- AREA POSTER (relatif untuk overlay badge + edit) ----
        poster_container = QWidget()
        poster_container.setFixedSize(200, 260)
        poster_container.setStyleSheet("background: transparent;")

        # Gambar poster
        lbl_poster = QLabel(poster_container)
        lbl_poster.setFixedSize(200, 260)
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
        badge.setFixedSize(60, 18)
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
        btn_edit.move(162, 8)  # Pojok kanan atas poster (200-30-8=162)
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

        poster_container.enterEvent = on_enter
        poster_container.leaveEvent = on_leave
        poster_container.setCursor(Qt.PointingHandCursor)

        # ---- TEKS DI BAWAH POSTER ----
        lbl_nama = QLabel(event.get("nama_event", ""))
        lbl_nama.setFont(QFont(self.font_bold, 11))
        lbl_nama.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        lbl_nama.setWordWrap(True)

        lbl_deskripsi = QLabel(event.get("deskripsi_singkat", ""))
        lbl_deskripsi.setFont(QFont(self.font_regular, 10))
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

        lbl_sub = QLabel("My Events")
        lbl_sub.setFont(QFont(self.font_bold, 16))
        lbl_sub.setStyleSheet("color: black; font-weight: bold;")
        layout.addWidget(lbl_sub)

        # ---- BOOKED EVENTS ----
        lbl_booked = QLabel("Booked Events")
        lbl_booked.setFont(QFont(self.font_bold, 13))
        lbl_booked.setStyleSheet("color: black; font-weight: bold;")
        layout.addWidget(lbl_booked)

        booked_scroll = self._buat_booked_scroll()
        layout.addWidget(booked_scroll)

        # ---- LIKED EVENTS ----
        lbl_liked = QLabel("Liked Events")
        lbl_liked.setFont(QFont(self.font_bold, 13))
        lbl_liked.setStyleSheet("color: black; font-weight: bold;")
        layout.addWidget(lbl_liked)

        # Container liked events — disimpan sebagai atribut
        # agar bisa di-refresh saat user unlike sebuah event
        self.liked_container = QWidget()
        self.liked_container.setStyleSheet("background: transparent;")
        self._render_liked_grid()

        layout.addWidget(self.liked_container, stretch=1)


    # ----------------------------------------------------------
    # FUNGSI _buat_booked_scroll()
    # Membuat area scroll horizontal untuk Booked Events
    # Event yang sudah selesai (tanggal sudah lewat) tidak ditampilkan
    #
    # Return: QScrollArea siap pakai
    # ----------------------------------------------------------
    def _buat_booked_scroll(self):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(320)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal {
                border: none; background: rgba(255,255,255,50);
                height: 6px; border-radius: 3px;
            }
            QScrollBar::handle:horizontal {
                background: #5D6B6B; min-width: 20px; border-radius: 3px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal { border: none; background: none; }
        """)

        container = QWidget()
        container.setFixedHeight(300) 
        container.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(container)
        h_layout.setSpacing(16)
        h_layout.setContentsMargins(0, 0, 0, 10)
        h_layout.setAlignment(Qt.AlignLeft)

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
                # Jika format tanggal tidak valid, tetap tampilkan
                aktif.append(e)

        if not aktif:
            lbl_empty = QLabel("Belum ada event yang kamu daftarkan.")
            lbl_empty.setFont(QFont(self.font_regular, 12))
            lbl_empty.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
            h_layout.addWidget(lbl_empty)
        else:
            for event in aktif:
                kartu = self._buat_kartu_booked(event)
                h_layout.addWidget(kartu)
            h_layout.addStretch()

        scroll.setWidget(container)
        return scroll


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
        kartu.setFixedWidth(160)
        kartu.setFixedHeight(280)
        kartu.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Poster kecil
        lbl_poster = QLabel()
        lbl_poster.setFixedSize(160, 200)
        lbl_poster.setScaledContents(True)
        lbl_poster.setStyleSheet("border-radius: 8px;")

        path = event.get("gambar_poster", "")
        if path and os.path.exists(path):
            lbl_poster.setPixmap(QPixmap(path))
        else:
            lbl_poster.setStyleSheet(
                "background-color: #D2E6E5; border-radius: 8px;"
            )

        # Nama event
        lbl_nama = QLabel(event.get("nama_event", ""))
        lbl_nama.setFont(QFont(self.font_bold, 10))
        lbl_nama.setStyleSheet("color: black;")
        lbl_nama.setWordWrap(True)

        # Deskripsi singkat
        lbl_desk = QLabel(event.get("deskripsi_singkat", ""))
        lbl_desk.setFont(QFont(self.font_regular, 9))
        lbl_desk.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        lbl_desk.setWordWrap(True)

        layout.addWidget(lbl_poster)
        layout.addWidget(lbl_nama)
        layout.addWidget(lbl_desk)

        return kartu


    # ----------------------------------------------------------
    # FUNGSI _render_liked_grid()
    # Membangun grid kartu Liked Events di dalam self.liked_container
    # Dipanggil saat pertama render dan saat user unlike sebuah event
    # ----------------------------------------------------------
    def _render_liked_grid(self):

        # Bersihkan layout lama di liked_container
        if self.liked_container.layout():
            while self.liked_container.layout().count():
                item = self.liked_container.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.liked_container.layout())

        grid = QGridLayout(self.liked_container)
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        liked_events = self._get_liked_events()

        # Filter hanya event yang masih di-liked
        # (liked_status kosong = default liked semua)
        tampil = [
            e for e in liked_events
            if self.liked_status.get(e["event_id"], True)
        ]

        if not tampil:
            lbl_empty = QLabel("Belum ada event yang kamu sukai.")
            lbl_empty.setFont(QFont(self.font_regular, 12))
            lbl_empty.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
            grid.addWidget(lbl_empty, 0, 0)
        else:
            for i, event in enumerate(tampil):
                kartu = self._buat_kartu_liked(event)
                grid.addWidget(kartu, i // 2, i % 2)


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
        kartu.setFixedWidth(220)
        kartu.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # ---- AREA POSTER ----
        poster_container = QWidget()
        poster_container.setFixedSize(220, 286)  # W:220 H:286 (proporsional dari 439x572)
        poster_container.setStyleSheet("background: transparent;")
        poster_container.setCursor(Qt.PointingHandCursor)

        # Gambar poster — klik untuk buka deskripsi
        lbl_poster = QLabel(poster_container)
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

        # Icon hati di pojok kanan bawah poster
        # Mulai dengan liked (ikon hati penuh)
        btn_hati = QPushButton(poster_container)
        btn_hati.setFixedSize(32, 32)
        btn_hati.move(180, 246)  # Pojok kanan bawah
        btn_hati.setStyleSheet("background: transparent; border: none;")
        btn_hati.setCursor(Qt.PointingHandCursor)

        # Set icon hati awal (liked)
        liked_icon_path = os.path.join(BASE_DIR, "assets", "liked.png")
        unliked_icon_path = os.path.join(BASE_DIR, "assets", "unliked.png")
        btn_hati.setIcon(QIcon(liked_icon_path))
        btn_hati.setIconSize(QSize(28, 28))

        # Status liked awal = True (karena ini Liked Events)
        self.liked_status[event["event_id"]] = True

        # Saat hati diklik → toggle liked/unliked
        # Jika unlike → hapus dari tampilan
        def on_hati_diklik(checked, ev=event, btn=btn_hati):
            event_id = ev["event_id"]
            self.liked_status[event_id] = False
            # Refresh grid liked events tanpa event yang di-unlike
            # CATATAN: Nanti tambahkan db_manager.unlike_event(user_id, event_id)
            self._render_liked_grid()

        btn_hati.clicked.connect(on_hati_diklik)

        # Klik poster → buka halaman deskripsi
        poster_container.mousePressEvent = lambda ev, e=event: self._buka_deskripsi(e)

        # ---- BAR BAWAH: Harga | Tanggal | Get Ticket ----
        # Background semi-transparan (CBD5E0, 40%)
        bar = QWidget(poster_container)
        bar.setFixedSize(220, 70)
        bar.move(0, 216)  # Di bagian bawah poster
        bar.setStyleSheet(
            "background-color: rgba(203, 213, 224, 0.4); border-radius: 0px;"
        )

        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(10, 8, 10, 8)
        bar_layout.setSpacing(4)

        # Kolom kiri: harga dan tanggal|waktu
        kiri_layout = QVBoxLayout()
        kiri_layout.setSpacing(2)

        # Harga tiket
        tipe = event.get("tipe_tiket", "Gratis")
        harga = event.get("harga_tiket", "0")
        if tipe == "Gratis":
            teks_harga = "Free"
        else:
            teks_harga = f"IDR {harga}"

        lbl_harga = QLabel(teks_harga)
        lbl_harga.setFont(QFont(self.font_bold, 16))
        lbl_harga.setStyleSheet("color: black; background: transparent;")

        # Tanggal dan waktu
        tgl = event.get("tanggal_display", "")
        wkt = event.get("waktu_display", "")
        lbl_tgl = QLabel(f"{tgl}  |  {wkt}")
        lbl_tgl.setFont(QFont(self.font_regular, 8))
        lbl_tgl.setStyleSheet("color: #454545; background: transparent;")

        kiri_layout.addWidget(lbl_harga)
        kiri_layout.addWidget(lbl_tgl)

        # Tombol Get Ticket / Booked
        # Mulai dengan "Get Ticket" (teal gelap)
        # Setelah diklik → berubah jadi "Booked" (pink EAA4A6)
        event_id = event["event_id"]
        sudah_booked = event.get("is_booked", False)

        btn_tiket = QPushButton("Booked" if sudah_booked else "Get ticket")
        btn_tiket.setFixedSize(90, 44)
        btn_tiket.setCursor(Qt.PointingHandCursor)
        btn_tiket.setFont(QFont(self.font_bold, 9))

        if sudah_booked:
            btn_tiket.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_PINK_BOOKED};
                    color: white;
                    border-radius: 8px;
                    border: none;
                }}
            """)
        else:
            btn_tiket.setStyleSheet("""
                QPushButton {
                    background-color: #5D6B6B;
                    color: white;
                    border-radius: 8px;
                    border: none;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #4a5858; }
            """)

        def on_tiket_diklik(checked, ev=event, btn=btn_tiket):
            tipe_tiket = ev.get("tipe_tiket", "Gratis")
            if tipe_tiket == "Gratis":
                # Langsung booking tanpa popup pembayaran
                btn.setText("Booked")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_PINK_BOOKED};
                        color: white;
                        border-radius: 8px;
                        border: none;
                        font-size: 11px;
                        font-weight: bold;
                    }}
                """)
                # CATATAN: Nanti tambahkan db_manager.book_event(user_id, event_id)
            else:
                # Berbayar → popup pembayaran (menyusul)
                QMessageBox.information(
                    self,
                    "Pembayaran",
                    "Fitur pembayaran akan segera hadir!"
                )

        btn_tiket.clicked.connect(on_tiket_diklik)

        bar_layout.addLayout(kiri_layout)
        bar_layout.addStretch()
        bar_layout.addWidget(btn_tiket)

        # Nama dan deskripsi di bawah kartu
        lbl_nama = QLabel(event.get("nama_event", ""))
        lbl_nama.setFont(QFont(self.font_bold, 11))
        lbl_nama.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        lbl_nama.setWordWrap(True)

        lbl_desk = QLabel(event.get("deskripsi_singkat", ""))
        lbl_desk.setFont(QFont(self.font_regular, 10))
        lbl_desk.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        lbl_desk.setWordWrap(True)

        layout.addWidget(poster_container)
        layout.addSpacing(10)
        layout.addWidget(lbl_nama)
        layout.addWidget(lbl_desk)

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

        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # ---- TOPBAR DESKRIPSI: tombol back + Home + avatar ----
        topbar = QWidget()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet("background: transparent;")

        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)

        # Tombol back — kembali ke panel Your Events
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
        btn_back.clicked.connect(self._tutup_deskripsi)

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
        btn_hati_desk.setIcon(QIcon(liked_icon))
        btn_hati_desk.setIconSize(QSize(28, 28))
        btn_hati_desk.setFixedSize(32, 32)
        btn_hati_desk.setStyleSheet("background: transparent; border: none;")
        btn_hati_desk.setCursor(Qt.PointingHandCursor)

        # Status liked di halaman deskripsi sinkron dengan liked_status
        is_liked = [self.liked_status.get(event["event_id"], True)]

        def toggle_hati_desk(checked, btn=btn_hati_desk):
            is_liked[0] = not is_liked[0]
            self.liked_status[event["event_id"]] = is_liked[0]
            if is_liked[0]:
                btn.setIcon(QIcon(liked_icon))
            else:
                btn.setIcon(QIcon(unliked_icon))
            # Refresh liked grid di panel utama
            self._render_liked_grid()

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
        teks_harga = "Free" if tipe == "Gratis" else f"IDR {harga}"

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

        sudah_booked = event.get("is_booked", False)
        btn_tiket2 = QPushButton("Booked" if sudah_booked else "Get ticket")
        btn_tiket2.setFixedSize(90, 44)
        btn_tiket2.setCursor(Qt.PointingHandCursor)
        btn_tiket2.setFont(QFont(self.font_bold, 9))

        if sudah_booked:
            btn_tiket2.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_PINK_BOOKED};
                    color: white; border-radius: 8px; border: none;
                }}
            """)
        else:
            btn_tiket2.setStyleSheet("""
                QPushButton {
                    background-color: #5D6B6B;
                    color: white; border-radius: 8px; border: none;
                    font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #4a5858; }
            """)

        def on_tiket2_diklik(checked, ev=event, btn=btn_tiket2):
            if ev.get("tipe_tiket", "Gratis") == "Gratis":
                btn.setText("Booked")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_PINK_BOOKED};
                        color: white; border-radius: 8px; border: none;
                        font-size: 11px; font-weight: bold;
                    }}
                """)
            else:
                QMessageBox.information(
                    self, "Pembayaran", "Fitur pembayaran akan segera hadir!"
                )

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

        # Avatar inisial EO
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

        # 6. Overview
        lbl_overview_title = QLabel("Overview")
        lbl_overview_title.setFont(QFont(self.font_bold, 18))
        lbl_overview_title.setStyleSheet("color: black;")
        kanan_layout.addWidget(lbl_overview_title)

        # 7. Konten overview
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

        # Masukkan panel deskripsi ke stacked_widget dan tampilkan
        self.stacked_widget.addWidget(panel)
        self.stacked_widget.setCurrentWidget(panel)
        self.panel_deskripsi_aktif = panel


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
        return DUMMY_EVENTS_STUDENT


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
        return DUMMY_EVENTS_STUDENT


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