# ==============================================================
# FILE: main_window.py
# TUGAS: Mengelola tampilan utama (Homepage) Campus Connect
# FITUR: Navbar, Hero Section, Horizontal Scroll Event, dan Add Event Dialog
# DIBUAT OLEH: Jocelyn (fitur-Jocelyn)
# ==============================================================

import email
import sys
import os
import scraper
import db_manager
import account_db

from worker_thread import ScraperThread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from about_page import AboutPage
from faq_page import FAQPage  # ← TAMBAHAN
from add_event_page import AddEventPage # ← TAMBAHAN
from success_page import SuccessPage # ← TAMBAHAN
from crud_events import prepare_create, save_payload
from login_page import LoginPage
from admin_page import AdminPage
from detail_event_page import DetailEventPage
from notification_page import NotificationPage
from signup_page import SignUpPage
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from language_manager import lang




# --- INTEGRASI COMPONENT ---
# Mencoba mengimport EventCard dari file card_widget.py
try:
    from card_widget import EventCard 
except ImportError:
    # Cadangan jika file card_widget.py belum tersedia agar program tetap jalan
    class EventCard(QWidget):
        diklik = pyqtSignal(str)
        def __init__(self, data):
            super().__init__()
            self.setFixedSize(220, 360)
            layout = QVBoxLayout(self)
            self.label = QLabel(data['nama_event'])
            layout.addWidget(self.label)
            self.setStyleSheet("background: white; border-radius: 15px; color: black; border: 1px solid #D2E6E5;")
        def set_poster(self, data): pass

# --- WARNA-WARNA UTAMA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLOR_PINK_LIGHT = "#F7CBCA"
COLOR_PINK_LOGIN = "#ff99aa"
COLOR_GRAY_LIGHT = "#D2E6E5"
COLOR_TEXT_PRIMARY = "#5D6B6B"

# Data Dummy untuk simulasi tampilan event
dummy_events = [
    {"event_id": "EVT-001", "jenis_event": "External", "nama_event": "Sparta Festival", "deskripsi_singkat": "Live painting and exhibition", "tanggal_waktu": "2026-05-20 10:00", "gambar_poster": os.path.join(BASE_DIR, "assets", "dummy_sparta.jpg")},
    {"event_id": "EVT-002", "jenis_event": "Internal", "nama_event": "Social Festival", "deskripsi_singkat": "Social talk and exhibition", "tanggal_waktu": "2026-06-15 13:00", "gambar_poster": os.path.join(BASE_DIR, "assets", "dummy_social.jpg")},
    {"event_id": "EVT-003", "jenis_event": "Internal", "nama_event": "Kelas Karir 4.0", "deskripsi_singkat": "Career preparation and talk", "tanggal_waktu": "2026-07-01 09:00", "gambar_poster": os.path.join(BASE_DIR, "assets", "career_40.png")},
    {"event_id": "EVT-004", "jenis_event": "Internal", "nama_event": "Polban After Campus", "deskripsi_singkat": "Career preparation", "tanggal_waktu": "2026-08-10 10:00", "gambar_poster": os.path.join(BASE_DIR, "assets", "after_campus.jpg")},
    {"event_id": "EVT-005", "jenis_event": "Internal", "nama_event": "Malam Gala Mahasiswa", "deskripsi_singkat": "Got talent show", "tanggal_waktu": "2026-09-05 19:00", "gambar_poster": os.path.join(BASE_DIR, "assets", "gala.jpg")},
    {"event_id": "EVT-006", "jenis_event": "External", "nama_event": "Workshop UI/UX", "deskripsi_singkat": "Design thinking session", "tanggal_waktu": "2026-10-12 13:00", "gambar_poster": os.path.join(BASE_DIR, "assets", "workshop.jpg")}
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. SETUP FONTS (Memuat font custom dari folder assets)
        id_lobster = QFontDatabase.addApplicationFont("assets/LobsterTwo-Regular.ttf")
        id_sans = QFontDatabase.addApplicationFont("assets/GoogleSans_17pt-Regular.ttf")
        self.font_lobster = QFontDatabase.applicationFontFamilies(id_lobster)[0] if id_lobster != -1 else "serif"
        self.font_sans = QFontDatabase.applicationFontFamilies(id_sans)[0] if id_sans != -1 else "sans-serif"

        # 2. WINDOW SETTINGS
        self.setWindowTitle("Campus Connect - Homepage")
        self.setMinimumSize(1024, 720)
        self.resize(1280, 850) 
        self.showMaximized()
        
        # 3. BACKGROUND CANVAS (Menggunakan Gradient QSS)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("mainCanvas")
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"""
            QWidget#mainCanvas {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #B5CECE, stop:0.4 #C8DCDC, stop:0.75 #D6E6E6, stop:1 #F7CBCA); 
            }}
        """)
        
        # Layout Utama Vertikal
        self.layout_utama = QVBoxLayout(self.central_widget)
        self.layout_utama.setContentsMargins(60, 20, 60, 40)
        
        # 4. INISIALISASI STATE (harus sebelum init UI)
        self.event_data_map = {}
        self.all_cards = []
        self.active_filters = {"jenis_event": None, "tipe_tiket": None, "source": None}
        self.current_user_role = "guest"

        # Page references — dibuat lazy
        self.about_page = None
        self.faq_page = None
        self.add_event_page = None
        self.success_page = None
        self.settings_page = None
        self.login_page = None
        self.admin_page = None
        self.detail_event_page = None
        self.notif_page = None

        # 5. INISIALISASI KOMPONEN UI
        self.init_header()
        self.spacing_after_navbar = QWidget()   # ← jadikan widget, bisa di-hide
        self.spacing_after_navbar.setFixedHeight(40)
        self.spacing_after_navbar.setStyleSheet("background: transparent;")
        self.layout_utama.addWidget(self.spacing_after_navbar)
        self.init_hero()
        self.spacing_after_hero = QWidget()
        self.spacing_after_hero.setFixedHeight(30)
        self.spacing_after_hero.setStyleSheet("background: transparent;")
        self.layout_utama.addWidget(self.spacing_after_hero)
        self.init_scroll_area()
        self.render_event_cards(dummy_events) # Mengisi Kartu dengan Data
        # Reflow sekali setelah window benar-benar tampil agar perhitungan
        # kolom memakai lebar viewport final (tidak nyangkut 1-2 kolom).
        QTimer.singleShot(0, self.filter_event_cards)

        # Page references — dibuat lazy (None dulu, baru dibuat saat pertama dibuka)
        self.about_page = None
        self.faq_page = None  # ← TAMBAHAN
        self.add_event_page = None  
        self.success_page = None 
        self.settings_page = None
        self.login_page = None
        self.admin_page = None
        self.detail_event_page = None
        self.notif_page = None          # ← TAMBAHAN: halaman notifikasi
        self.signup_page = None
        self.event_data_map = {} 
        self.all_cards = []   
        self.current_user_role = "guest"
        self.layout_utama.addStretch() # Mendorong semua ke atas
        self.current_user_email = ""  # Email user yang sedang login
        self.current_user_nama  = ""  # Nama user yang sedang login
        self.current_user_foto_path = ""  # Path foto profil user
        self.update_navbar_berdasarkan_role()
        
        # === FITUR AUTO UPDATE 15 MENIT ===
        # QTimer sudah di-import melalui 'from PyQt5.QtCore import *'
        self.timer_update = QTimer(self)
        
        # Hubungkan detak timer ke fungsi eksekutor
        self.timer_update.timeout.connect(self.jalankan_auto_update)
        
        # Mulai timer: 15 menit = 15 * 60 detik * 1000 milidetik = 900000 ms
        self.timer_update.start(900000)

        self.timer_student_notif = QTimer(self)
        self.timer_student_notif.timeout.connect(self._cek_notifikasi_mahasiswa)
        self.timer_student_notif.start(3600000) 

        # NOTE: initial synchronization is performed by `main._sync_scraped_events_to_db()`
        # during application startup. To avoid running the scraper twice in quick
        # succession, do not trigger `jalankan_auto_update()` here immediately.
        # The periodic timer will run the first auto-update after its interval.

        # ── LANGUAGE ──────────────────────────────────────────────────────
        lang.language_changed.connect(self._retranslate)

    def _retranslate(self):
        """Dipanggil otomatis saat bahasa diganti dari Language Setting."""
        self.btn_home.setText(lang.t("nav.home"))
        self.btn_about.setText(lang.t("nav.about"))
        self.search_bar.setPlaceholderText(lang.t("home.search_placeholder"))
        self.event_title.setText(lang.t("home.upcoming"))
        # Retranslate filter chips jika sudah diinisialisasi
        if hasattr(self, '_jenis_chips') and hasattr(self, '_tiket_chips') and hasattr(self, '_sumber_chips'):
            self._retranslate_filters()
        self.update_navbar_berdasarkan_role()

    def jalankan_auto_update(self):
        print("[AUTO UPDATE] Memulai sinkronisasi data di latar belakang...")
        
        # 1. Ambil data yang sudah ada di database untuk jadi acuan
        data_db = db_manager.get_all_events()
        existing_keys = {
            (str(row.get("nama_event") or "").strip().lower(),
            str(row.get("tanggal_waktu") or "").strip().lower())
            for row in data_db
        }
        # 2. Bungkus fungsi scraper + parameternya menggunakan lambda
        fungsi_scraper = lambda: scraper.ambil_event_polban(limit=100, existing_keys=existing_keys)
        
        # 3. Masukkan ke thread
        self.thread_scraper = ScraperThread(fungsi_scraper)
        self.thread_scraper.selesai.connect(self.on_auto_update_selesai)
        self.thread_scraper.error.connect(lambda msg: print(f"[AUTO UPDATE ERROR] {msg}"))
        self.thread_scraper.start()

    def on_auto_update_selesai(self, hasil_scraping):
        """Menerima data dari thread setelah scraping selesai."""
        if not hasil_scraping:
            print("[AUTO UPDATE] Tidak ada data baru yang ditemukan.")
            return

        print(f"[AUTO UPDATE] Berhasil menarik {len(hasil_scraping)} data. Memperbarui database...")
        
        # 1. Update Database (Menggunakan fungsi INSERT OR IGNORE dari db_manager)
        for event in hasil_scraping:
            event["status"] = "approved" # Beri stempel otomatis karena ini dari website resmi
            db_manager.upsert_event(event)
            
        # 2. Refresh Tampilan UI Layar Utama
        self.refresh_tampilan_homepage()
        print("[AUTO UPDATE] Tampilan homepage berhasil diperbarui dengan data terbaru!")

    def refresh_tampilan_homepage(self):
        """Membangun ulang kanvas kartu dari nol agar tidak ada bug UI nyangkut."""

        # Reuse kanvas scroll yang sudah ada, lalu bersihkan isi lamanya.
        if self.scroll.widget() is None:
            self.scroll_content = QWidget()
            self.scroll_content.setStyleSheet("background: transparent;")
            self.card_layout = QGridLayout(self.scroll_content)
            self.card_layout.setSpacing(16)
            self.card_layout.setContentsMargins(6, 0, 6, 10)
            self.card_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.scroll.setWidget(self.scroll_content)
            self.scroll_content.installEventFilter(self)

        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # 1. Ambil data terbaru dari database
        data_db_terbaru = db_manager.get_events_by_status("approved")

        # 2. Format ulang data — _cache_image dijalankan di thread terpisah
        #    agar tidak memblokir UI saat ada gambar URL yang perlu diunduh.
        def _prepare_data():
            try:
                from main import _cache_image
            except ImportError:
                _cache_image = lambda x: x
            result = []
            for row in data_db_terbaru:
                result.append({
                    "db_id":            str(row.get("id", "")),
                    "event_id":         row.get("event_id", ""),
                    "nama_event":       row.get("nama_event") or "Tanpa Judul",
                    "deskripsi_singkat":row.get("deskripsi_singkat") or "...",
                    "gambar_poster":    _cache_image(row.get("gambar_poster") or ""),
                    "jenis_event":      (row.get("jenis_event") or "External").title(),
                    "tanggal_waktu":    row.get("tanggal_waktu") or "TBA",
                    "lokasi":           row.get("lokasi", "") or "",
                    "penyelenggara":    row.get("nama_eo", "") or "",
                    "tipe_tiket":       row.get("tipe_tiket", "Free") or "Free",
                    "harga_tiket":      row.get("harga_tiket", "0") or "0",
                    "source":           row.get("source", "") or "",
                })
            return result

        self._thread_refresh = ScraperThread(_prepare_data)
        self._thread_refresh.selesai.connect(self.render_event_cards)
        self._thread_refresh.error.connect(
            lambda msg: print(f"[REFRESH ERROR] {msg}")
        )
        self._thread_refresh.start()
        
    def show_home_page(self):
        self._hide_all_pages()

        # REFRESH DATA SETIAP KALI KE HOME
        self.refresh_tampilan_homepage()
        if hasattr(self, 'search_bar'):
            self.search_bar.blockSignals(True)
            self.search_bar.clear()
            self.search_bar.blockSignals(False)
            self.btn_clear_search.hide()

        # Reset filter chips ke "All"
        self.active_filters = {"jenis_event": None, "tipe_tiket": None, "source": None}
        if hasattr(self, '_jenis_chips') and hasattr(self, '_tiket_chips'):
            for i, btn in enumerate(self._jenis_chips):
                btn.setStyleSheet(self._chip_active_style if i == 0 else self._chip_inactive_style)
            for i, btn in enumerate(self._tiket_chips):
                btn.setStyleSheet(self._chip_active_style if i == 0 else self._chip_inactive_style)
            if hasattr(self, '_sumber_chips'):
                for i, btn in enumerate(self._sumber_chips):
                    btn.setStyleSheet(self._chip_active_style if i == 0 else self._chip_inactive_style)

        self.navbar_container.show()
        self.spacing_after_navbar.show()
        self.spacing_after_hero.show()
        if hasattr(self, 'filter_bar_widget') and self.filter_bar_widget:
            self.filter_bar_widget.show()

        self.layout_utama.setContentsMargins(60, 20, 60, 40)
        self.layout_utama.setSpacing(0)

        self.hero_widget.show()
        self.event_title.show()
        self.scroll.show()

    def _register_wheel_forwarding(self, widget):
        # Hanya pasang event filter pada root widget kartu saja.
        # Memasang ke semua child menyebabkan banyak pemanggilan eventFilter
        # yang berulang-ulang dan menurunkan performa saat wheel event.
        widget.installEventFilter(self)

    def _get_cards_per_row(self):
        """Hitung jumlah kartu per baris berdasarkan lebar viewport saat ini."""
        if not hasattr(self, "scroll") or not hasattr(self, "card_layout"):
            return 1

        card_width = 220
        spacing = self.card_layout.horizontalSpacing()
        if spacing < 0:
            spacing = 25

        margins = self.card_layout.contentsMargins()
        available = max(0, self.scroll.viewport().width() - margins.left() - margins.right())

        # Fallback saat fase awal render: viewport kadang belum punya ukuran final.
        if available < card_width:
            available = max(available, self.scroll.width() - margins.left() - margins.right())

        # n*card + (n-1)*spacing <= available
        per_row = (available + spacing) // (card_width + spacing)
        return max(1, int(per_row))

    def eventFilter(self, watched, event):
        # Biarkan QScrollArea menangani wheel event secara default (vertikal).
        # Ini memastikan scroll selalu atas-bawah, termasuk saat window di-minimize.
        return super().eventFilter(watched, event)

    def _hide_all_pages(self):
        """Helper: sembunyikan semua page konten (home, about, faq)."""
        self.hero_widget.hide()
        self.event_title.hide()
        self.scroll.hide()
        self.spacing_after_navbar.hide()
        self.spacing_after_hero.hide()
        if hasattr(self, 'filter_bar_widget') and self.filter_bar_widget:
            self.filter_bar_widget.hide()
        if self.about_page:
            self.about_page.hide()
        if self.faq_page:
            self.faq_page.hide()
        if self.add_event_page:      
            self.add_event_page.hide()
        if self.success_page:        
            self.success_page.hide()
        if self.settings_page:
            self.settings_page.hide()
        if self.login_page:
            self.login_page.hide()
        if self.admin_page:
            self.admin_page.hide()
        if self.detail_event_page:
            self.detail_event_page.hide()
        if self.notif_page:                 # ← TAMBAHAN
            self.notif_page.hide()
        if self.signup_page:
            self.signup_page.hide()

    def init_header(self):
        """Membangun bagian navigasi atas (Navbar)"""
        navbar_container = QWidget()
        navbar_container.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT}; border-radius: 40px;")
        navbar_layout = QHBoxLayout(navbar_container)
        self.navbar_container = navbar_container 
        navbar_layout.setContentsMargins(25, 10, 25, 10)

        # Logo dengan perpaduan font Lobster
        self.logo = QLabel(
            f"<span style='font-family: \"{self.font_lobster}\"; font-size: 26px; color: {COLOR_TEXT_PRIMARY};'>Campus</span><br>"
            f"<span style='font-family: \"{self.font_lobster}\"; font-size: 26px; font-weight: bold; color: {COLOR_PINK_LOGIN};'>Connect</span>"
        )
        self.logo.setTextFormat(Qt.RichText)
        
        # Tombol Navigasi Kiri
        self.btn_home = QPushButton(lang.t("nav.home"))
        self.btn_home.setIcon(QIcon("assets/home.png"))
        self.btn_home.setCursor(Qt.PointingHandCursor)
        
        self.btn_about = QPushButton(lang.t("nav.about"))
        self.btn_about.setIcon(QIcon("assets/information-button.png"))
        self.btn_about.setCursor(Qt.PointingHandCursor)
        
        nav_style = f"font-family: \"{self.font_sans}\"; background: transparent; color: {COLOR_TEXT_PRIMARY}; border: none; font-size: 20px;"
        self.btn_home.setStyleSheet(nav_style + "font-weight: bold;")
        self.btn_about.setStyleSheet(nav_style + "margin-left: 30px;")

        # ← TAMBAHKAN BLOK INI DI SINI
        # Bagian Kanan (Login & Hamburger Menu)
        self.btn_login = QPushButton(lang.t("nav.login"))
        self.btn_login.setIcon(QIcon("assets/user.png"))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("background-color: #ff99aa; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
        self.btn_login.clicked.connect(self.show_login_page)

        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(QIcon("assets/menu.png"))
        self.btn_menu.setIconSize(QSize(30, 30))
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton::menu-indicator { image: none; width: 0px; height: 0px; }
        """)
        self.hamburger_menu = QMenu(self)
        self.hamburger_menu.setCursor(Qt.PointingHandCursor)
        self.hamburger_menu.setStyleSheet(f"""
            QMenu {{ background-color: #D2E6E5; color: #5D6B6B; border: 1px solid #BDD7D8; border-radius: 10px; padding: 5px; }}
            QMenu::item {{ background-color: transparent; padding: 8px 25px 8px 10px; border-radius: 5px; }}
            QMenu::item:selected {{ background-color: #BDD7D8; color: #5D6B6B; }}
        """)
        self.btn_menu.setMenu(self.hamburger_menu)

        # juga tambahin widget logo dan tombol nav ke layout SEBELUM spacer
        navbar_layout.addWidget(self.logo)
        navbar_layout.addSpacing(30)
        navbar_layout.addWidget(self.btn_home)
        navbar_layout.addWidget(self.btn_about)


        # --- SEARCH BAR ---
        search_container = QWidget()
        search_container.setFixedWidth(520)
        search_container.setFixedHeight(44)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_layout.setSpacing(6)

        icon_search = QLabel()
        icon_search.setFixedSize(18, 18)
        icon_search.setStyleSheet("background: transparent; border: none;")

        pix = QPixmap("assets/search.png").scaled(
            18, 18,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        icon_search.setPixmap(pix)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(lang.t("home.search_placeholder"))
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 18px;
                color: #516465;
            }
        """)

        self.btn_clear_search = QPushButton("✕")
        self.btn_clear_search.setFixedSize(22, 22)
        self.btn_clear_search.setCursor(Qt.PointingHandCursor)
        self.btn_clear_search.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: #888; font-size: 18px;
            }
            QPushButton:hover { color: #516465; }
        """)
        self.btn_clear_search.hide()
        self.btn_clear_search.clicked.connect(lambda: self.search_bar.clear())

        search_layout.addWidget(icon_search)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.btn_clear_search)

        search_container.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.55);
                border-radius: 18px;
                border: 1px solid rgba(81,100,101,0.2);
            }
        """)

        # Debounce timer — cegah lag, tunggu 250ms setelah stop ketik
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(250)
        self.search_timer.timeout.connect(self.filter_event_cards)
        self.search_bar.textChanged.connect(self._on_search_text_changed)

        spacer_kiri = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_kanan = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        navbar_layout.addSpacerItem(spacer_kiri)
        navbar_layout.addWidget(search_container)
        navbar_layout.addSpacerItem(spacer_kanan)
        navbar_layout.addWidget(self.btn_login)
        navbar_layout.addSpacing(12)

        # ---- ICON LONCENG + BADGE ----
        # Container fixed-size TANPA layout — badge di-overlay secara absolut
        # agar tidak mempengaruhi ukuran navbar saat window di-resize.
        self.bell_container = QWidget()
        self.bell_container.setFixedSize(44, 44)
        self.bell_container.setStyleSheet("background: transparent;")

        # Tombol lonceng — child langsung, posisi absolut
        self.btn_bell = QPushButton(self.bell_container)
        self.btn_bell.setIcon(QIcon("assets/bell.png"))
        self.btn_bell.setIconSize(QSize(26, 26))
        self.btn_bell.setCursor(Qt.PointingHandCursor)
        self.btn_bell.setFixedSize(44, 44)
        self.btn_bell.move(0, 0)
        self.btn_bell.setStyleSheet("""
            QPushButton { background: transparent; border: none; border-radius: 22px; }
            QPushButton:hover { background: rgba(255,255,255,120); }
        """)
        self.btn_bell.clicked.connect(self.show_notif_page)

        # Badge angka merah — overlay pojok kanan atas, tanpa layout
        self.lbl_badge = QLabel("0", self.bell_container)
        self.lbl_badge.setAlignment(Qt.AlignCenter)
        self.lbl_badge.setFixedSize(18, 18)
        self.lbl_badge.move(24, 2)
        self.lbl_badge.setStyleSheet("""
            QLabel {
                background-color: #E53935;
                color: white;
                border-radius: 9px;
                font-size: 9px;
                font-weight: bold;
            }
        """)
        self.lbl_badge.hide()
        self.lbl_badge.raise_()

        navbar_layout.addWidget(self.bell_container)
        self.bell_container.hide()   # hanya tampil saat login sebagai EO

        navbar_layout.addSpacing(12)

        # ---- AVATAR LINGKARAN POJOK KANAN ----
        # Menampilkan foto profil user (atau inisial jika belum ada foto)
        self.navbar_avatar = QLabel()
        self.navbar_avatar.setFixedSize(36, 36)
        self.navbar_avatar.setAlignment(Qt.AlignCenter)
        self.navbar_avatar.setStyleSheet(
            "background-color: #2D6A6A; color: white; font-weight: bold; "
            "font-size: 13px; border-radius: 18px;"
        )
        self.navbar_avatar.hide()  # hanya tampil saat login
        navbar_layout.addWidget(self.navbar_avatar)
        navbar_layout.addSpacing(8)

        navbar_layout.addWidget(self.btn_menu)
        self.layout_utama.addWidget(navbar_container)
        self.btn_about.clicked.connect(self.show_about_page)
        self.btn_home.clicked.connect(self.show_home_page)

    def _on_search_text_changed(self, text):
        if text:
            self.btn_clear_search.show()
        else:
            self.btn_clear_search.hide()
        # Reset timer setiap ketik — cegah spam trigger
        self.search_timer.start()

    def init_filter_bar(self):
        """Filter chips bar: Jenis Event + Tipe Tiket"""
        self.filter_bar_widget = QWidget()
        self.filter_bar_widget.setStyleSheet("background: transparent;")
        
        bar_layout = QHBoxLayout(self.filter_bar_widget)
        bar_layout.setContentsMargins(4, 12, 4, 20)
        bar_layout.setSpacing(14)

        CHIP_ACTIVE   = "background: #516465; color: white; border-radius: 21px; padding: 9px 24px; font-size: 17px; border: none; font-weight: bold;"
        CHIP_INACTIVE = "background: rgba(255,255,255,0.71); color: #516465; border-radius: 21px; padding: 9px 24px; font-size: 17px; border: none; font-weight: bold;"

        # ── Grup Jenis Event ──────────────────────────────────────
        self.lbl_jenis = QLabel(lang.t("home.filter_type"))
        self.lbl_jenis.setStyleSheet("color: #516465; font-size: 17px; font-weight: 700; background: transparent;")
        bar_layout.addWidget(self.lbl_jenis)

        # Mapping untuk retranslasi: (button_index, translation_key)
        self._jenis_chips_keys = [(lang.t("home.filter_all"), None), (lang.t("home.filter_internal"), "Internal"), (lang.t("home.filter_external"), "External")]
        jenis_chips = []
        for label, value in self._jenis_chips_keys:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(42)
            is_active = (value == self.active_filters["jenis_event"])
            btn.setStyleSheet(CHIP_ACTIVE if is_active else CHIP_INACTIVE)
            btn.clicked.connect(
                lambda _, v=value, b=btn, grp=jenis_chips: self._on_filter_chip_clicked("jenis_event", v, b, grp)
            )
            jenis_chips.append(btn)
            bar_layout.addWidget(btn)

        self._jenis_chips = jenis_chips
        self._chip_active_style   = CHIP_ACTIVE
        self._chip_inactive_style = CHIP_INACTIVE

        # Pemisah
        sep = QLabel("|")
        sep.setStyleSheet("color: rgba(81,100,101,0.35); background: transparent; font-size: 19px;")
        bar_layout.addWidget(sep)
        bar_layout.addSpacing(4)

        # ── Grup Tipe Tiket ───────────────────────────────────────
        self.lbl_tiket = QLabel(lang.t("home.filter_ticket"))
        self.lbl_tiket.setStyleSheet("color: #516465; font-size: 17px; font-weight: 700; background: transparent;")
        bar_layout.addWidget(self.lbl_tiket)

        # Mapping untuk retranslasi
        self._tiket_chips_keys = [(lang.t("home.filter_all"), None), (lang.t("home.filter_free"), "Free"), (lang.t("home.filter_paid"), "Paid")]
        tiket_chips = []
        for label, value in self._tiket_chips_keys:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(42)
            is_active = (value == self.active_filters["tipe_tiket"])
            btn.setStyleSheet(CHIP_ACTIVE if is_active else CHIP_INACTIVE)
            btn.clicked.connect(
                lambda _, v=value, b=btn, grp=tiket_chips: self._on_filter_chip_clicked("tipe_tiket", v, b, grp)
            )
            tiket_chips.append(btn)
            bar_layout.addWidget(btn)

        self._tiket_chips = tiket_chips

        # Pemisah
        sep2 = QLabel("|")
        sep2.setStyleSheet("color: rgba(81,100,101,0.35); background: transparent; font-size: 19px;")
        bar_layout.addWidget(sep2)
        bar_layout.addSpacing(6)

        # ── Grup Sumber ───────────────────────────────────────────
        self.lbl_sumber = QLabel(lang.t("home.filter_source"))
        self.lbl_sumber.setStyleSheet("color: #516465; font-size: 17px; font-weight: 700; background: transparent;")
        bar_layout.addWidget(self.lbl_sumber)

        # Mapping untuk retranslasi
        self._sumber_chips_keys = [(lang.t("home.filter_all"), None), (lang.t("home.filter_official"), "scraping"), (lang.t("home.filter_partner"), "manual")]
        sumber_chips = []
        for label, value in self._sumber_chips_keys:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(42)
            is_active = (value == self.active_filters["source"])
            btn.setStyleSheet(CHIP_ACTIVE if is_active else CHIP_INACTIVE)
            btn.clicked.connect(
                lambda _, v=value, b=btn, grp=sumber_chips: self._on_filter_chip_clicked("source", v, b, grp)
            )
            sumber_chips.append(btn)
            bar_layout.addWidget(btn)

        self._sumber_chips = sumber_chips

        bar_layout.addStretch()
        self.layout_utama.addWidget(self.filter_bar_widget)

    def _on_filter_chip_clicked(self, filter_key, value, clicked_btn, btn_group):
        """Toggle chip aktif dan trigger filter ulang."""
        self.active_filters[filter_key] = value
        for btn in btn_group:
            btn.setStyleSheet(
                self._chip_active_style if btn is clicked_btn else self._chip_inactive_style
            )
        self.filter_event_cards()

    def _retranslate_filters(self):
        """Retranslate semua filter chips ketika bahasa berubah."""
        # Update label grup
        self.lbl_jenis.setText(lang.t("home.filter_type"))
        self.lbl_tiket.setText(lang.t("home.filter_ticket"))
        self.lbl_sumber.setText(lang.t("home.filter_source"))
        
        # Definisikan ulang mapping keys dengan text terbaru
        self._jenis_chips_keys = [(lang.t("home.filter_all"), None), 
                                   (lang.t("home.filter_internal"), "Internal"), 
                                   (lang.t("home.filter_external"), "External")]
        self._tiket_chips_keys = [(lang.t("home.filter_all"), None), 
                                  (lang.t("home.filter_free"), "Free"), 
                                  (lang.t("home.filter_paid"), "Paid")]
        self._sumber_chips_keys = [(lang.t("home.filter_all"), None), 
                                   (lang.t("home.filter_official"), "scraping"), 
                                   (lang.t("home.filter_partner"), "manual")]
        
        # Update text button chips
        for i, btn in enumerate(self._jenis_chips):
            btn.setText(self._jenis_chips_keys[i][0])
        
        for i, btn in enumerate(self._tiket_chips):
            btn.setText(self._tiket_chips_keys[i][0])
        
        for i, btn in enumerate(self._sumber_chips):
            btn.setText(self._sumber_chips_keys[i][0])

    def init_hero(self):
        self.hero_widget = QWidget()
        hero_widget = self.hero_widget
        layout = QVBoxLayout(hero_widget)
        l1 = QLabel(lang.t("home.welcome_to"))
        l1.setStyleSheet(f"font-size: 48px; font-style: italic; color: {COLOR_TEXT_PRIMARY};")
        l2 = QLabel(
            f"<span style='font-family: \"{self.font_lobster}\"; font-size: 165px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};'>Campus </span>"
            f"<span style='font-family: \"{self.font_lobster}\"; font-size: 165px; font-weight: bold; color: #EAA4A6;'>Connect</span>"
        )
        l2.setTextFormat(Qt.RichText)
        layout.addWidget(l1)
        layout.addWidget(l2)
        layout.setAlignment(Qt.AlignLeft)
        self.layout_utama.addWidget(hero_widget)

    def init_scroll_area(self):
        self.event_title = QLabel(lang.t("home.upcoming"))
        title = self.event_title
        title.setStyleSheet(f"font-weight: bold; font-size: 32px; color: {COLOR_TEXT_PRIMARY}; margin-bottom: 10px;")
        self.layout_utama.addWidget(title)
        self.init_filter_bar()
        
        self.scroll = QScrollArea()
        self.scroll.setFixedHeight(640) 
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) 
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Styling Scrollbar agar senada
        self.scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
                border-radius: 20px;
                padding: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.3);
                width: 12px;
                border-radius: 6px;
                margin: 10px 4px 10px 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(81, 100, 101, 0.6);
                border-radius: 6px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(81, 100, 101, 1);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.scroll.setGraphicsEffect(shadow)
                
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;") 
        self.card_layout = QGridLayout(self.scroll_content)
        self.card_layout.setSpacing(20)
        self.card_layout.setContentsMargins(6, 0, 6, 10)
        self.card_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scroll.setWidget(self.scroll_content)
        self.scroll.installEventFilter(self)
        self.scroll.viewport().installEventFilter(self)
        self.scroll_content.installEventFilter(self)
        self.layout_utama.addWidget(self.scroll)

    def render_event_cards(self, data):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.event_data_map = {}
        self.all_cards = [] 

        CARDS_PER_ROW = self._get_cards_per_row()

        for i, e in enumerate(data):
            card = EventCard(e)
            card.setCursor(Qt.PointingHandCursor)
            card.diklik.connect(self.handle_card_click)
            self._register_wheel_forwarding(card)
            
            path_poster = e.get("gambar_poster", "")
            if os.path.exists(path_poster):
                with open(path_poster, "rb") as f:
                    card.set_poster(f.read())
            
            db_id = str(e.get("db_id") or e.get("id") or "")
            event_id = str(e.get("event_id") or "")
            if db_id:
                self.event_data_map[db_id] = e
            if event_id:
                self.event_data_map[event_id] = e

            row = i // CARDS_PER_ROW   # ← baris ke berapa
            col = i % CARDS_PER_ROW    # ← kolom ke berapa
            self.card_layout.addWidget(card, row, col)
            self.all_cards.append(card)

    def filter_event_cards(self):
        query        = self.search_bar.text().strip().lower()
        f_jenis      = self.active_filters.get("jenis_event")
        f_tiket      = self.active_filters.get("tipe_tiket")
        f_source     = self.active_filters.get("source")

        cocok = []
        for card in self.all_cards:
            if not hasattr(card, 'event_data'):
                continue
            data   = card.event_data
            nama   = data.get('nama_event', '').lower()
            jenis  = data.get('jenis_event', '').strip().title()
            tiket  = data.get('tipe_tiket', 'Free').strip()
            source = data.get('source', '').strip().lower()

            match_search = (not query) or (query in nama)
            match_jenis  = (f_jenis is None) or (jenis == f_jenis)
            match_tiket  = (f_tiket is None) or (tiket == f_tiket)

            # source di DB: URL panjang = hasil scraping, "manual" = input EO
            is_scraped   = source.startswith("http")
            match_source = (
                f_source is None or
                (f_source == "scraping" and is_scraped) or
                (f_source == "manual"   and not is_scraped)
            )

            if match_search and match_jenis and match_tiket and match_source:
                cocok.append(card)

        # Cabut semua kartu dari grid dulu
        for card in self.all_cards:
            self.card_layout.removeWidget(card)
            card.setVisible(False)

        # Pasang ulang hanya yang cocok mulai dari posisi 0,0
        CARDS_PER_ROW = self._get_cards_per_row()
        for i, card in enumerate(cocok):
            row = i // CARDS_PER_ROW
            col = i % CARDS_PER_ROW
            self.card_layout.addWidget(card, row, col)
            card.setVisible(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Saat ukuran jendela berubah, susun ulang grid agar card ikut wrap.
        if hasattr(self, "all_cards") and self.all_cards:
            self.filter_event_cards()

    def handle_card_click(self, event_id):
        print(f"Card diklik: {event_id}")

        # OPTIMASI: Ambil dari cache yang sudah diisi dari database saat refresh.
        # Ini lebih cepat daripada query seluruh tabel setiap kali kartu diklik.
        data_event = self.event_data_map.get(event_id)

        # Fallback hanya untuk kondisi cache belum sinkron atau event belum termuat.
        if not data_event:
            data_list = db_manager.get_all_events()
            for row in data_list:
                if str(row.get("id")) == str(event_id) or str(row.get("event_id")) == str(event_id):
                    data_event = row
                    break

        if not data_event:
            print(f"Event tidak ditemukan: {event_id}")
            return

        if self.current_user_email and hasattr(db_manager, "is_event_booked"):
            event_key = str(
                data_event.get("event_id")
                or data_event.get("db_id")
                or data_event.get("id")
                or ""
            )
            if event_key:
                event_date = str(
                    data_event.get("tanggal_waktu") or data_event.get("tanggal_display") or ""
                ).strip()
                is_booked = db_manager.is_event_booked(
                    self.current_user_email,
                    event_key,
                    event_date
                )
                data_event["is_booked"] = is_booked

        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        if self.detail_event_page is None:
            from detail_event_page import DetailEventPage
            self.detail_event_page = DetailEventPage(
                current_user_email=self.current_user_email
            )
            self.detail_event_page.kembali_diklik.connect(self.show_home_page)
            self.layout_utama.insertWidget(4, self.detail_event_page)
            self.layout_utama.setStretchFactor(self.detail_event_page, 1)

        self.detail_event_page.current_user_email = self.current_user_email
        self.detail_event_page.current_user_role = self.current_user_role
        self.detail_event_page.set_data(data_event)
        self.detail_event_page.show()
        
        data_event = self.event_data_map.get(event_id)
    
    def proses_booking(self, data_event):

        # Hanya mahasiswa yang boleh booking
        if self.current_user_role != "mahasiswa":
            
            # Kalau belum login
            if self.current_user_role == "guest":
                QMessageBox.warning(
                    self,
                    lang.t("detail.login_required_title"),
                    "You must login as a student first to book this event."
                )

            # Kalau login tapi bukan mahasiswa
            else:
                QMessageBox.warning(
                    self,
                    "Access Denied",
                    "Only student accounts can book events."
                )

            return

        # Kalau mahasiswa → booking berhasil
        QMessageBox.information(
            self,
            lang.t("msg.booking_success"),
            f'You successfully booked "{data_event.get("nama_event", "")}"'
        )

    def buka_form_input(self):
        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)
        
        if self.add_event_page is None:
            self.add_event_page = AddEventPage()
            self.add_event_page.event_dipublikasi.connect(self.on_event_dipublikasi)
            self.add_event_page.dibatalkan.connect(self.show_home_page)
            self.layout_utama.insertWidget(4, self.add_event_page)
            # Membuat add_event_page mengisi seluruh ruang yang tersedia
            self.layout_utama.setStretchFactor(self.add_event_page, 1)

        self.add_event_page.reset_form()
        self.add_event_page.show()

    def show_about_page(self):
        self._hide_all_pages()

        if self.about_page is None:
            self.about_page = AboutPage()
            self.layout_utama.insertWidget(4, self.about_page)

        self.about_page.show()

    # ↓ TAMBAHAN: method untuk buka FAQ page
    def show_faq_page(self):
        self._hide_all_pages()

        if self.faq_page is None:
            self.faq_page = FAQPage()
            self.layout_utama.insertWidget(4, self.faq_page)

        self.faq_page.show()

    # ↓ TAMBAHAN: method untuk buka add event page
    def on_event_dipublikasi(self, data):
        form_data = {
            "nama_event"     : data.get("nama_event", ""),
            "deskripsi_event": data.get("deskripsi_singkat", ""),
            "jenis_event"    : data.get("jenis_event", ""),
            "kategori_event" : data.get("kategori", ""),
            "tanggal"        : data.get("tanggal", ""),
            "waktu"          : data.get("waktu", ""),
            "poster_event"   : data.get("gambar_poster", ""),
            "source"         : data.get("source", "manual"),
        }

        is_valid, errors, payload = prepare_create(form_data)
        if not is_valid:
            pesan_error = "\n".join(errors.values()) if errors else "Invalid event data."
            QMessageBox.warning(self, lang.t("msg.failed_publish"), pesan_error)
            return

        save_payload(payload)

        print(f"[DEBUG] event_id: {payload.get('event_id')}")
        print(f"[DEBUG] lokasi: {data.get('lokasi')}")
        print(f"[DEBUG] penyelenggara: {data.get('penyelenggara')}")

        import sqlite3
        try:
            conn = sqlite3.connect(db_manager.DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE events SET
                    lokasi      = ?,
                    tipe_tiket  = ?,
                    harga_tiket = ?,
                    nama_eo     = ?,
                    email_eo    = ?
                WHERE event_id = ?
            """, (
                data.get("lokasi", ""),
                data.get("tipe_tiket", "Free"),
                data.get("harga_tiket", "0"),
                data.get("penyelenggara", ""),
                getattr(self, "current_user_email", ""),  # ← email EO yang sedang login
                payload.get("event_id", ""),
            ))
            print(f"[DEBUG] rows updated: {cursor.rowcount}")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[WARN] Gagal simpan field extra: {e}")

        # ← JANGAN LUPA INI, biar muncul success page setelah publish
        self._hide_all_pages()
        self.layout_utama.setContentsMargins(60, 20, 60, 40)

        if self.success_page is None:
            self.success_page = SuccessPage()
            self.success_page.lihat_event_diklik.connect(self.show_home_page)
            self.success_page.buat_event_lain_diklik.connect(self.buka_form_input)
            self.layout_utama.insertWidget(4, self.success_page)
            self.layout_utama.setStretchFactor(self.success_page, 1)

        self.success_page.set_data(data)
        self.success_page.show()

    # ↓ TAMBAHAN: method untuk buka success page setelah event dipublikasi
    def show_success_page(self):
        self._hide_all_pages()
        self.layout_utama.setContentsMargins(60, 20, 60, 40)

        if self.success_page:
            self.success_page.show()

    def show_login_page(self):
        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        # HAPUS signup page lama
        if self.signup_page is not None:
            self.layout_utama.removeWidget(self.signup_page)
            self.signup_page.deleteLater()
            self.signup_page = None

        # Jika login_page sudah pernah dibuat sebelumnya, hapus dulu
        # agar tidak ada duplikat widget di layout
        if self.login_page is not None:
            self.layout_utama.removeWidget(self.login_page)
            self.login_page.deleteLater()
            self.login_page = None

        # Buat objek LoginPage baru yang fresh
        self.login_page = LoginPage()
        # Hubungkan sinyal login_diklik ke fungsi yang mengecek email & password ke database
        self.login_page.login_diklik.connect(self.on_login_diklik)
        # pindah ke signup page saat tombol signup diklik di halaman login
        self.login_page.signup_diklik.connect(self.show_signup_page)
        # saat user klik tombol kembali di halaman login, apllikasi akan kembali ke homepage
        self.login_page.kembali_diklik.connect(self.show_home_page)

        self.layout_utama.insertWidget(4, self.login_page)
        self.layout_utama.setStretchFactor(self.login_page, 1)
        # tampilkan login page ke layar
        self.login_page.show()
        
    def show_admin_page(self):
        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        
        if self.admin_page is None:
            self.admin_page = AdminPage()
            # Hubungkan sinyal
            self.admin_page.kembali_diklik.connect(self.show_home_page)
            # Nanti kita buat fungsi proses_validasi untuk mengupdate database
            # Hubungkan tombol Approve/Decline ke database
            self.admin_page.validasi_diklik.connect(self.proses_validasi_admin)
            
            self.layout_utama.insertWidget(4, self.admin_page)
            self.layout_utama.setStretchFactor(self.admin_page, 1)

        # Muat ulang data setiap kali halaman dibuka
        self.admin_page.load_data_antrean()
        self.admin_page.show()
        
    def proses_validasi_admin(self, event_ref, status_baru):
        """Mengeksekusi persetujuan atau penolakan event dari Admin."""
        is_update_request = str(event_ref).startswith("REQ:")
        is_event_ref = str(event_ref).startswith("EVT:")
        item_label = str(event_ref)

        if is_update_request:
            try:
                request_id = int(str(event_ref).split(":", 1)[1])
            except Exception:
                QMessageBox.warning(self, lang.t("msg.error"), lang.t("msg.invalid_update_request"))
                return

            request_data = db_manager.get_event_update_request(request_id)
            if not request_data:
                QMessageBox.warning(self, lang.t("msg.error"), lang.t("msg.update_request_not_found"))
                return

            sukses = db_manager.apply_event_update_request(request_id, status_baru)
            if not sukses:
                QMessageBox.warning(self, lang.t("msg.error"), lang.t("msg.process_update_failed"))
                return

            item_label = f"REQ:{request_id}"
            nama_event = request_data.get("nama_event", f"Request #{request_id}")
            email_eo = request_data.get("requested_by_email", "") or request_data.get("nama_eo", "")
            if status_baru == "approved":
                judul = lang.t("notif.msg_update_approved_title")
                pesan = lang.t("notif.msg_update_approved_body").format(event=nama_event)

                # NEW: kirim notifikasi critical update ke mahasiswa
                # yang sudah booking event ini.
                event_id_update = request_data.get("event_id", "")
                if event_id_update and hasattr(db_manager, "kirim_notif_critical_update"):
                    db_manager.kirim_notif_critical_update(event_id_update, nama_event)
            else:
                judul = lang.t("notif.msg_update_rejected_title")
                pesan = lang.t("notif.msg_update_rejected_body").format(event=nama_event)
            db_manager.tambah_notifikasi_eo(email_eo, judul, pesan)
            
        else:
            event_id = str(event_ref).replace("EVT:", "") if is_event_ref else str(event_ref)
            item_label = event_id

            # 1. Ubah status di database
            db_manager.update_event_status(event_id, status_baru)

            # 2. Ambil info event untuk pesan notifikasi
            semua_event = db_manager.get_all_events()
            data_event = next((e for e in semua_event if e.get("event_id") == event_id), {})
            nama_event = data_event.get("nama_event", event_id)
            email_eo = data_event.get("email_eo", "")

            # 3. Simpan notifikasi ke database agar EO bisa lihat
            if status_baru == "approved":
                judul = lang.t("notif.msg_approved_title")
                pesan = lang.t("notif.msg_approved_body").format(event=nama_event)
                # kirim interest match ke mahasiswa yang punya interest sesuai kategori event
                kategori = data_event.get("kategori", "")
                if kategori and hasattr(db_manager, "kirim_notif_interest_match"):
                    db_manager.kirim_notif_interest_match(event_id, nama_event, kategori)

                # kirim Campus Spotlight untuk event internal
                jenis_event = data_event.get("jenis_event", "")
                if str(jenis_event).strip().lower() == "internal":
                    if hasattr(db_manager, "kirim_notif_campus_spotlight"):
                        db_manager.kirim_notif_campus_spotlight(event_id, nama_event)
            else:
                judul = lang.t("notif.msg_rejected_title")
                pesan = lang.t("notif.msg_rejected_body").format(event=nama_event)

        if email_eo:
            db_manager.simpan_notifikasi(email_eo, judul, pesan)

        # 4. Beri notifikasi ke Admin
        aksi = "Approved" if status_baru == "approved" else "Rejected"
        QMessageBox.information(self, lang.t("msg.success"), f"Item {item_label} successfully {aksi}!")

        # 5. Refresh tabel di halaman admin
        self.admin_page.load_data_antrean()

        # 6. Refresh layar utama agar event yang di-approve langsung muncul di depan!
        self.refresh_tampilan_homepage()

    # =========================================================
    # BELL BADGE — FUNGSI PEMBANTU
    # =========================================================
    def _set_badge(self, count: int):
        """Update tampilan angka badge pada icon lonceng."""
        if not hasattr(self, "lbl_badge"):
            return
        if count > 0:
            self.lbl_badge.setText(str(count) if count < 100 else "99+")
            self.lbl_badge.show()
            self.lbl_badge.raise_()
        else:
            self.lbl_badge.hide()

    def _refresh_bell_badge(self):
        """Hitung ulang notif belum-baca dari DB dan update badge."""
        if self.current_user_role in ["eo", "mahasiswa"] and self.current_user_email:
            count = db_manager.hitung_notifikasi_belum_dibaca(self.current_user_email)
            self._set_badge(count)
        else:
            self._set_badge(0)

    def _cek_notifikasi_mahasiswa(self):
        """Cek reminder H-1 untuk mahasiswa dan refresh badge lonceng."""
        if self.current_user_role != "mahasiswa" or not self.current_user_email:
            return

        try:
            if hasattr(db_manager, "cek_dan_kirim_reminder_h1"):
                db_manager.cek_dan_kirim_reminder_h1(self.current_user_email)
        except Exception as exc:
            print(f"[Student Reminder] {exc}")

        self._refresh_bell_badge()

    def show_notif_page(self):
        """Buka halaman daftar notifikasi EO."""
        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        if self.notif_page is None:
            self.notif_page = NotificationPage(
                email_user=self.current_user_email,
                user_role=self.current_user_role,
            )
            self.notif_page.kembali_diklik.connect(self.show_home_page)
            self.notif_page.badge_berubah.connect(self._set_badge)
            self.notif_page.buka_your_events.connect(self.buka_my_events)
            self.notif_page.buka_detail_event.connect(self._on_buka_detail_event_dari_notif)
            
            self.layout_utama.insertWidget(4, self.notif_page)
            self.layout_utama.setStretchFactor(self.notif_page, 1)
        else:
            # Update email kalau beda & muat ulang
            self.notif_page.set_email(self.current_user_email)

        self.notif_page.show()
    
    def show_signup_page(self):
        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        # Hapus page lama agar fresh
        if self.signup_page is not None:
            self.layout_utama.removeWidget(self.signup_page)
            self.signup_page.deleteLater()
            self.signup_page = None

        # Buat signup page baru
        self.signup_page = SignUpPage()

        # Tombol kembali → Login page
        self.signup_page.kembali_diklik.connect(self.show_login_page)

        # Tombol sign up → proses registrasi akun
        self.signup_page.signup_diklik.connect(self.on_signup_diklik)

        # Tombol "Already have an account? Sign In"
        self.signup_page.login_diklik.connect(self.show_login_page)

        self.layout_utama.insertWidget(4, self.signup_page)
        self.layout_utama.setStretchFactor(self.signup_page, 1)

        self.signup_page.show()

    def _on_buka_detail_event_dari_notif(self, event_id_ref: str):
        """
        Dipanggil saat student klik notif H1_REMINDER / NEW_LIKED_MATCH /
        CAMPUS_NEW_EVENT. Saat ini memanggil handle_card_click yang sudah ada.
        Temanmu bisa mengubah ini untuk langsung buka pop up deskripsi.
        """
        if event_id_ref:
            self.show_home_page()
            self.handle_card_click(event_id_ref)

    def on_signup_diklik(self, nama, email, phone, university, password):
        """Handle sign up dari halaman signup dan simpan akun ke accounts.db."""
        if account_db.register_account(email, password, role="mahasiswa"):
            QMessageBox.information(
                self,
                lang.t("msg.success"),
                "Account created successfully. Please login."
            )
            self.show_login_page()
        else:
            QMessageBox.warning(
                self,
                lang.t("msg.registration_failed"),
                "This email is already registered. Please use another email or login."
            )

    def on_login_diklik(self, email, password):
            import account_db # Pastikan ini sudah di-import di atas

            user_role = account_db.check_login(email, password)

            if user_role:
                # 1. Ubah state role aplikasi
                self.current_user_role = user_role

                # Simpan email user yang login agar bisa dikirim ke settings
                # dan dipakai oleh YourEventsPanel untuk query event per EO
                self.current_user_email = email
                
                # CRITICAL: Create/ensure user exists in database.db users table
                # This is required for booking functionality to work
                db_manager.ensure_user_exists(email, role=user_role)

                # Load profil lengkap dari database (nama, foto, dll)
                profil = db_manager.get_user_profile(email)
                self.current_user_nama = profil.get("nama", "")
                self.current_user_foto_path = profil.get("foto_profil_path", "")

                self.settings_page = None
                
                # 2. Beri notifikasi sukses
                QMessageBox.information(self, lang.t("msg.success"), lang.t("msg.login_success_role").format(role=user_role.upper()))
                
                # 3. Panggil fungsi untuk mengubah tampilan navbar
                self.update_navbar_berdasarkan_role()
                self._cek_notifikasi_mahasiswa()

                # 4. Cek apakah ada pending redirect setelah login
                #    (contoh: user dibawa ke sini dari dialog lang.t("detail.login_required_title") di Account Settings)
                pending = getattr(self, "_pending_after_login", None)
                if pending:
                    self._pending_after_login = None
                    dest, *args = pending
                    if dest == "settings":
                        panel_index = args[0] if args else 0
                        QTimer.singleShot(100, lambda: self.buka_settings(panel_index=panel_index))
                        return

                # 5. Kembali ke halaman utama (default)
                self.show_home_page()
            else:
                QMessageBox.warning(self, lang.t("msg.failed"), lang.t("msg.login_failed"))
                
    def update_navbar_berdasarkan_role(self):
        """Mengubah tampilan Navbar dan isi Menu secara dinamis sesuai role"""
        
        # 1. Bersihkan menu agar tidak terjadi penumpukan (duplikat)
        self.hamburger_menu.clear()

        # Tampilkan lonceng hanya untuk EO
        if self.current_user_role in ["eo", "mahasiswa"]:
            self.bell_container.show()
            self._refresh_bell_badge()
        else:
            self.bell_container.hide()
            self._set_badge(0)

        if self.current_user_role == "guest":
            # --- TAMPILAN GUEST ---
            self.btn_login.setText(lang.t("nav.login"))
            self.btn_login.setStyleSheet("background-color: #ff99aa; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
            
            try: self.btn_login.clicked.disconnect() 
            except: pass
            self.btn_login.clicked.connect(self.show_login_page)

            if hasattr(self, "navbar_avatar"):
                self.navbar_avatar.hide()

            # Guest BISA melihat FAQ dan Setting, tapi TIDAK ADA Add Event
            self.hamburger_menu.addAction(QIcon("assets/question.png"), lang.t("nav.faq")).triggered.connect(self.show_faq_page)
            self.hamburger_menu.addAction(QIcon("assets/gear.png"), lang.t("settings.title")).triggered.connect(self.buka_settings)

        elif self.current_user_role == "eo":
            # --- TAMPILAN EVENT ORGANIZER ---
            nama = getattr(self, "current_user_nama", "")
            sapaan = f"  Halo, {nama}!" if nama else lang.t("nav.hi_eo")
            self.btn_login.setText(sapaan)
            self.btn_login.setStyleSheet("background-color: #2D6A6A; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
            
            try: self.btn_login.clicked.disconnect() 
            except: pass
            self.btn_login.clicked.connect(self.proses_logout)

            self.refresh_avatar_navbar()

            # EO punya akses lengkap
            self.hamburger_menu.addAction(QIcon("assets/event.png"), lang.t("home.add_event_btn")).triggered.connect(self.buka_form_input) 
            self.hamburger_menu.addAction(QIcon("assets/event.png"), lang.t("your_events.title")).triggered.connect(self.buka_my_events)
            self.hamburger_menu.addAction(QIcon("assets/question.png"), lang.t("nav.faq")).triggered.connect(self.show_faq_page)
            self.hamburger_menu.addAction(QIcon("assets/gear.png"), lang.t("settings.title")).triggered.connect(self.buka_settings)

        elif self.current_user_role == "admin":
            # --- TAMPILAN ADMIN ---
            self.btn_login.setText(lang.t("nav.admin_panel"))
            self.btn_login.setStyleSheet("background-color: #516465; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
            
            try: self.btn_login.clicked.disconnect() 
            except: pass
            self.btn_login.clicked.connect(self.proses_logout)

            if hasattr(self, "navbar_avatar"):
                self.navbar_avatar.hide()

            # Menu khusus Admin
            self.hamburger_menu.addAction(QIcon("assets/event.png"), lang.t("admin.title")).triggered.connect(self.show_admin_page)
            self.hamburger_menu.addAction(QIcon("assets/question.png"), lang.t("nav.faq")).triggered.connect(self.show_faq_page)
            self.hamburger_menu.addAction(QIcon("assets/gear.png"), lang.t("settings.title")).triggered.connect(self.buka_settings)
        
        elif self.current_user_role in ["mahasiswa"]:
            # --- TAMPILAN MAHASISWA / USER AUDIENCE ---
            nama = getattr(self, "current_user_nama", "")
            sapaan = f"  Halo, {nama}!" if nama else lang.t("nav.hi_student")
            self.btn_login.setText(sapaan)
            self.btn_login.setStyleSheet("background-color: #2D6A6A; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
            
            try: self.btn_login.clicked.disconnect() 
            except: pass
            self.btn_login.clicked.connect(self.proses_logout)

            self.refresh_avatar_navbar()

            # Sesuai aturan RBAC: Mahasiswa TIDAK BISA "Add Event", 
            # menu hamburger mereka dibuat bersih langsung ke riwayat tiket/event mereka
            self.hamburger_menu.addAction(QIcon("assets/event.png"), lang.t("your_events.title")).triggered.connect(self.buka_my_events)
            self.hamburger_menu.addAction(QIcon("assets/question.png"), lang.t("nav.faq")).triggered.connect(self.show_faq_page)
            self.hamburger_menu.addAction(QIcon("assets/gear.png"), lang.t("settings.title")).triggered.connect(self.buka_settings)
            
    def refresh_greeting_navbar(self):
        """
        Dipanggil dari account_window.py setelah user simpan nama baru.
        Update current_user_nama dari database lalu refresh teks greeting.
        """
        email = getattr(self, "current_user_email", "")
        if email:
            profil = db_manager.get_user_profile(email)
            self.current_user_nama = profil.get("nama", "")
        self.update_navbar_berdasarkan_role()

    def refresh_avatar_navbar(self):
        """
        Dipanggil dari account_window.py setelah user simpan foto baru,
        dan dari update_navbar_berdasarkan_role() saat login.
        Update lingkaran avatar di pojok kanan navbar.
        """
        if not hasattr(self, "navbar_avatar"):
            return

        # Reload path foto terbaru dari database
        email = getattr(self, "current_user_email", "")
        if email:
            profil = db_manager.get_user_profile(email)
            self.current_user_foto_path = profil.get("foto_profil_path", "")
            if not self.current_user_nama:
                self.current_user_nama = profil.get("nama", "")

        foto_path = getattr(self, "current_user_foto_path", "")

        if foto_path and os.path.exists(foto_path):
            # Tampilkan foto sebagai lingkaran
            pixmap = QPixmap(foto_path)
            if not pixmap.isNull():
                size = 36
                pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                # Crop tengah jika tidak persegi
                if pixmap.width() != size or pixmap.height() != size:
                    x = (pixmap.width() - size) // 2
                    y = (pixmap.height() - size) // 2
                    pixmap = pixmap.copy(x, y, size, size)
                # Buat mask lingkaran
                hasil = QPixmap(size, size)
                hasil.fill(Qt.transparent)
                painter = QPainter(hasil)
                painter.setRenderHint(QPainter.Antialiasing)
                from PyQt5.QtGui import QPainterPath
                path = QPainterPath()
                path.addEllipse(0, 0, size, size)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                self.navbar_avatar.setPixmap(hasil)
                self.navbar_avatar.setStyleSheet("border-radius: 18px; background: transparent;")
                self.navbar_avatar.show()
                return

        # Fallback: tampilkan inisial
        nama = getattr(self, "current_user_nama", "")
        inisial = "".join(p[0].upper() for p in nama.strip().split()[:2]) if nama.strip() else ""
        self.navbar_avatar.setPixmap(QPixmap())
        self.navbar_avatar.setText(inisial if inisial else "")
        self.navbar_avatar.setStyleSheet(
            "background-color: #2D6A6A; color: white; font-weight: bold; "
            "font-size: 13px; border-radius: 18px;"
        )
        self.navbar_avatar.show()

    def proses_logout(self):
        # Konfirmasi logout
        jawaban = QMessageBox.question(self, lang.t("msg.logout"), lang.t("msg.logout_confirm"), QMessageBox.Yes | QMessageBox.No)
        
        if jawaban == QMessageBox.Yes:
            # Kembalikan state ke guest
            self.current_user_role = "guest"
            self.current_user_email = ""
            self.current_user_nama  = ""
            self.current_user_foto_path = ""
            self.settings_page = None
            self.notif_page = None
            if hasattr(self, "navbar_avatar"):
                self.navbar_avatar.hide()
            # Kembalikan tampilan navbar
            self.update_navbar_berdasarkan_role()
            # Buka ulang halaman home
            self.show_home_page()
            QMessageBox.information(self, lang.t("msg.logout"), lang.t("msg.logout_success"))
        
    def proses_login(self, email, password):
    # Cek ke database
        if account_db.check_login(email, password):
        #   TODO: Nanti kita buat logika ganti tampilan Navbar di sini
            QMessageBox.information(self, lang.t("msg.success"), lang.t("msg.login_success"))
            self.show_home_page()
        else:
            QMessageBox.warning(self, lang.t("msg.failed"), lang.t("msg.login_failed"))
    
    def _tampil_dialog_login_diperlukan(self, panel_index=0, untuk_edit=False):
        """
        Menampilkan dialog pop-up ketika user mencoba membuka Account Settings
        tanpa login terlebih dahulu.
        - Tombol 'Log In'  → navigasi ke halaman login, setelah berhasil login
                             otomatis kembali ke Account Settings.
        - Tombol 'Cancel'  → kembali ke Homepage.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(lang.t("detail.login_required_title"))
        dialog.setFixedSize(420, 240)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setModal(True)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(0)

        # ── Icon peringatan ──
        lbl_icon = QLabel("🔒")
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 36px; background: transparent;")
        layout.addWidget(lbl_icon)
        layout.addSpacing(12)

        # ── Judul ──
        lbl_title = QLabel(lang.t("detail.login_required_title"))
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2D3748; background: transparent;"
        )
        layout.addWidget(lbl_title)
        layout.addSpacing(8)

        # ── Pesan ──
        if untuk_edit:
            pesan = "You need to log in first to edit\nAccount Settings."
        else:
            pesan = "You need to log in first to access\nAccount Settings."

        lbl_msg = QLabel(pesan)
        lbl_msg.setAlignment(Qt.AlignCenter)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet(
            "font-size: 13px; color: #718096; background: transparent;"
        )
        layout.addWidget(lbl_msg)
        layout.addSpacing(24)

        # ── Tombol ──
        BUTTON_WIDTH = 168
        BUTTON_HEIGHT = 44
        BUTTON_RADIUS = 22

        btn_cancel = QPushButton(lang.t("btn.cancel"))
        btn_cancel.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #EEF3F5;
                color: #243333;
                border: none;
                border-radius: {BUTTON_RADIUS}px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E3ECEF;
            }}
            QPushButton:pressed {{
                background-color: #D6E2E5;
            }}
        """)

        btn_login = QPushButton(lang.t("login.btn_login"))
        btn_login.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: #516465;
                color: white;
                border: none;
                border-radius: {BUTTON_RADIUS}px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #405354;
            }}
            QPushButton:pressed {{
                background-color: #334445;
            }}
        """)
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(12)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_login)
        layout.addLayout(btn_row)

        # ── Aksi tombol ──
        btn_cancel.clicked.connect(dialog.reject)
        if not untuk_edit:
            btn_cancel.clicked.connect(self.show_home_page)

        def _ke_login_lalu_settings():
            dialog.accept()
            # Tandai bahwa setelah login sukses harus buka Account Settings
            self._pending_after_login = ("settings", panel_index)
            self.show_login_page()

        btn_login.clicked.connect(_ke_login_lalu_settings)

        dialog.exec_()

    def buka_settings(self, panel_index=0):
        from settings.setting_window import SettingsWindow

        # Guest tetap boleh membuka halaman Settings.
        # Login baru diminta ketika guest mencoba mengedit Account Settings.
        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)

        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        if self.settings_page is None:
            # Ambil profil lengkap dari DB agar semua field (kontak, bio, dll.) terisi
            email = getattr(self, "current_user_email", "")
            profil = db_manager.get_user_profile(email) if email else {}

            self.settings_page = SettingsWindow(
                user_data={
                    "nama"            : profil.get("nama", getattr(self, "current_user_nama", "")),
                    "bio"             : profil.get("bio", ""),
                    "email"           : profil.get("email", email),
                    "kontak"          : profil.get("kontak", ""),
                    "role"            : self.current_user_role,  # pakai langsung dari account_db, bukan dari profil DB
                    "inisial"         : profil.get("inisial", ""),
                    "foto_profil_path": profil.get("foto_profil_path", getattr(self, "current_user_foto_path", "")),
                }
            )
            self.settings_page.btn_home.clicked.connect(self.show_home_page)
            # Hubungkan sinyal Add Event dari Settings ke fungsi buka_form_input
            # Dipancarkan saat EO klik "Create your first event now!" di Your Events
            self.settings_page.minta_buka_add_event.connect(self.buka_form_input)
            self.layout_utama.insertWidget(4, self.settings_page)
            self.layout_utama.setStretchFactor(self.settings_page, 1)

        self.settings_page.show()

        # Navigasi ke panel tertentu jika diminta
        # (contoh: index 1 = Your Events, dipanggil dari hamburger "My Events")
        if hasattr(self.settings_page, 'switch_panel'):
            self.settings_page.switch_panel(panel_index)

    def buka_my_events(self):
        """Buka Settings dan navigasi langsung ke Your Events panel (index 1)"""
        self.buka_settings(panel_index=1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Style Fusion agar tampilan konsisten di Windows/Mac/Linux
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())