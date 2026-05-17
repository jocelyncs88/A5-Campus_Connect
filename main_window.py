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
        self.resize(1280, 900)
        
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
        
        # 4. INISIALISASI KOMPONEN UI
# SESUDAH:
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
        
        self.layout_utama.addStretch() # Mendorong semua ke atas

        # Page references — dibuat lazy (None dulu, baru dibuat saat pertama dibuka)
        self.about_page = None
        self.faq_page = None  # ← TAMBAHAN
        self.add_event_page = None  
        self.success_page = None 
        self.settings_page = None
        self.login_page = None
        self.admin_page = None
        self.detail_event_page = None
        self.event_data_map = {}    
        self.current_user_role = "guest"
        self.current_user_email = ""  # Email user yang sedang login
        self.update_navbar_berdasarkan_role()
        
        # === FITUR AUTO UPDATE 15 MENIT ===
        # QTimer sudah di-import melalui 'from PyQt5.QtCore import *'
        self.timer_update = QTimer(self)
        
        # Hubungkan detak timer ke fungsi eksekutor
        self.timer_update.timeout.connect(self.jalankan_auto_update)
        
        # Mulai timer: 15 menit = 15 * 60 detik * 1000 milidetik = 900000 ms
        self.timer_update.start(900000)

        # NOTE: initial synchronization is performed by `main._sync_scraped_events_to_db()`
        # during application startup. To avoid running the scraper twice in quick
        # succession, do not trigger `jalankan_auto_update()` here immediately.
        # The periodic timer will run the first auto-update after its interval.
        
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
        try:
            from main import _cache_image
        except ImportError:
            _cache_image = lambda x: x

        # Reuse kanvas scroll yang sudah ada, lalu bersihkan isi lamanya.
        if self.scroll.widget() is None:
            self.scroll_content = QWidget()
            self.scroll_content.setStyleSheet("background: transparent;")
            self.card_layout = QHBoxLayout(self.scroll_content)
            self.card_layout.setSpacing(25)
            self.card_layout.setContentsMargins(10, 0, 10, 10)
            self.card_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.scroll.setWidget(self.scroll_content)
            self.scroll_content.installEventFilter(self)

        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # 1. Ambil data terbaru dari database tanpa membatasi status,
        # agar homepage tetap konsisten dengan tampilan awal aplikasi.
        data_db_terbaru = db_manager.get_events_by_status("approved")
        
        # 2. Format ulang data
        data_untuk_ui = []
        for row in data_db_terbaru:
            event_dict = {
                "db_id": str(row.get("id", "")),
                "event_id": row.get("event_id", ""),
                "nama_event": row.get("nama_event") or "Tanpa Judul",
                "deskripsi_singkat": row.get("deskripsi_singkat") or "...",
                "gambar_poster": _cache_image(row.get("gambar_poster") or ""),
                "jenis_event": (row.get("jenis_event") or "External").title(),
                "tanggal_waktu": row.get("tanggal_waktu") or "TBA",
                "lokasi"           : row.get("lokasi", "") or "",        # ← TAMBAH
                "penyelenggara"    : row.get("nama_eo", "") or "",       # ← TAMBAH
                "tipe_tiket"       : row.get("tipe_tiket", "Free") or "Free",  # ← TAMBAH
                "harga_tiket"      : row.get("harga_tiket", "0") or "0",      # ← TAMBAH
            }
            data_untuk_ui.append(event_dict)
            
        # 3. Cetak ulang kartu di kanvas yang sudah dibersihkan
        self.render_event_cards(data_untuk_ui)
        
    def show_home_page(self):
        self._hide_all_pages()
        
        # REFRESH DATA SETIAP KALI KE HOME (Biar langsung update tanpa close program!)
        self.refresh_tampilan_homepage()

        self.navbar_container.show()
        self.spacing_after_navbar.show()
        self.spacing_after_hero.show()

        self.layout_utama.setContentsMargins(60, 20, 60, 40)
        self.layout_utama.setSpacing(0)

        self.hero_widget.show()
        self.event_title.show()
        self.scroll.show()
        
    def _register_wheel_forwarding(self, widget):
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, watched, event):
        if hasattr(self, "scroll") and event.type() == QEvent.Wheel:
            sources = {
                self.scroll,
                self.scroll.viewport(),
                self.scroll_content,
            }
            if watched in sources or self.scroll_content.isAncestorOf(watched):
                hbar = self.scroll.horizontalScrollBar()
                if hbar.maximum() <= 0:
                    return super().eventFilter(watched, event)

                pixel_delta = event.pixelDelta()
                angle_delta = event.angleDelta()
                modifiers = event.modifiers()

                step_size = max(hbar.singleStep(), 40)
                move_by = 0

                if not pixel_delta.isNull():
                    if pixel_delta.x() != 0:
                        move_by = -pixel_delta.x()
                    else:
                        move_by = -pixel_delta.y()
                elif not angle_delta.isNull():
                    if angle_delta.x() != 0:
                        steps = angle_delta.x() / 120
                        move_by = int(-steps * step_size)
                    else:
                        steps = angle_delta.y() / 120
                        if modifiers & Qt.ShiftModifier:
                            move_by = int(-steps * step_size)
                        else:
                            move_by = int(-steps * step_size)

                if move_by:
                    hbar.setValue(hbar.value() + move_by)
                    event.accept()
                    return True

        return super().eventFilter(watched, event)

    def _hide_all_pages(self):
        """Helper: sembunyikan semua page konten (home, about, faq)."""
        self.hero_widget.hide()
        self.event_title.hide()
        self.scroll.hide()
        self.spacing_after_navbar.hide()
        self.spacing_after_hero.hide()
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

    def init_header(self):
        """Membangun bagian navigasi atas (Navbar)"""
        navbar_container = QWidget()
        navbar_container.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT}; border-radius: 40px;")
        navbar_layout = QHBoxLayout(navbar_container)
        self.navbar_container = navbar_container 
        navbar_layout.setContentsMargins(25, 10, 25, 10)

        # Logo dengan perpaduan font Lobster
        self.logo = QLabel(f"<span style='font-family: \"{self.font_lobster}\"; font-size: 26px; color: #516465;'>Campus</span><br><span style='font-family: \"{self.font_lobster}\"; font-size: 26px; font-weight: bold; color: #F7CBCA;'>Connect</span>")
        
        # Tombol Navigasi Kiri
        self.btn_home = QPushButton("  Home")
        self.btn_home.setIcon(QIcon("assets/home.png"))
        self.btn_home.setCursor(Qt.PointingHandCursor)
        
        self.btn_about = QPushButton("  About Us")
        self.btn_about.setIcon(QIcon("assets/information-button.png"))
        self.btn_about.setCursor(Qt.PointingHandCursor)
        
        nav_style = f"font-family: \"{self.font_sans}\"; background: transparent; color: {COLOR_TEXT_PRIMARY}; border: none; font-size: 14px;"
        self.btn_home.setStyleSheet(nav_style + "font-weight: bold;")
        self.btn_about.setStyleSheet(nav_style + "margin-left: 30px;")

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Bagian Kanan (Login & Hamburger Menu)
        self.btn_login = QPushButton("  Login")
        self.btn_login.setIcon(QIcon("assets/user.png"))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("background-color: #ff99aa; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")

        self.btn_login.clicked.connect(self.show_login_page)
        
        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(QIcon("assets/menu.png"))
        self.btn_menu.setIconSize(QSize(24, 24))
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton::menu-indicator {
                image: none;
                width: 0px;
                height: 0px;
            }
        """)

        # Dropdown Menu Styling
        self.hamburger_menu = QMenu(self)
        self.hamburger_menu.setCursor(Qt.PointingHandCursor)
        self.hamburger_menu.setStyleSheet(f"""
            QMenu {{ background-color: #D2E6E5; color: #5D6B6B; border: 1px solid #BDD7D8; border-radius: 10px; padding: 5px; }}
            QMenu::item {{ background-color: transparent; padding: 8px 25px 8px 10px; border-radius: 5px; }}
            QMenu::item:selected {{ background-color: #BDD7D8; color: #5D6B6B; }}
        """)
        
        #hamburger menu udh ada di self.hamburger_menu.addAction (update navbar berdasarkan role)
        
        # # Aksi di dalam Hamburger Menu
        # self.hamburger_menu.addAction(QIcon("assets/event.png"), "Add Event").triggered.connect(self.buka_form_input)
        # # ← TAMBAHAN: connect FAQ ke show_faq_page
        # self.hamburger_menu.addAction(QIcon("assets/question.png"), "FAQ").triggered.connect(self.show_faq_page)
        # self.hamburger_menu.addAction(QIcon("assets/gear.png"), "Setting").triggered.connect(self.buka_settings)
        self.btn_menu.setMenu(self.hamburger_menu)

        # Masukkan semua ke layout navbar
        navbar_layout.addWidget(self.logo)
        navbar_layout.addSpacing(30)
        navbar_layout.addWidget(self.btn_home)
        navbar_layout.addWidget(self.btn_about)
        navbar_layout.addSpacerItem(spacer)
        navbar_layout.addWidget(self.btn_login)
        navbar_layout.addSpacing(30)
        navbar_layout.addWidget(self.btn_menu)
        self.layout_utama.addWidget(navbar_container)
        self.btn_about.clicked.connect(self.show_about_page)
        self.btn_home.clicked.connect(self.show_home_page)

    def init_hero(self):
        self.hero_widget = QWidget()
        hero_widget = self.hero_widget
        layout = QVBoxLayout(hero_widget)
        l1 = QLabel("Welcome to,")
        l1.setStyleSheet(f"font-size: 24px; font-style: italic; color: {COLOR_TEXT_PRIMARY};")
        l2 = QLabel("Campus Connect")
        l2.setStyleSheet(f"font-family: \"{self.font_lobster}\"; font-size: 72px; font-weight: bold; color: #516465;")
        layout.addWidget(l1)
        layout.addWidget(l2)
        layout.setAlignment(Qt.AlignLeft)
        self.layout_utama.addWidget(hero_widget)

    def init_scroll_area(self):
        self.event_title = QLabel("Highlight / Upcoming Events")
        title = self.event_title
        title.setStyleSheet(f"font-weight: bold; font-size: 18px; color: {COLOR_TEXT_PRIMARY}; margin-bottom: 10px;")
        self.layout_utama.addWidget(title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(420)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Styling Scrollbar agar senada
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal { border: none; background: rgba(255, 255, 255, 50); height: 8px; border-radius: 4px; margin: 0px 20px 0px 20px; }
            QScrollBar::handle:horizontal { background: #5D6B6B; min-width: 20px; border-radius: 4px; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;") 
        self.card_layout = QHBoxLayout(self.scroll_content)
        self.card_layout.setSpacing(25)
        self.card_layout.setContentsMargins(10, 0, 10, 10)
        self.card_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.scroll.setWidget(self.scroll_content)
        self.scroll.installEventFilter(self)
        self.scroll.viewport().installEventFilter(self)
        self.scroll_content.installEventFilter(self)
        self.layout_utama.addWidget(self.scroll)

    def render_event_cards(self, data):
        """Membuat dan menampilkan objek kartu berdasarkan list data"""
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Simpan semua event data ke map supaya bisa diakses saat diklik
        self.event_data_map = {}

        for e in data:
            card = EventCard(e)
            card.setCursor(Qt.PointingHandCursor)
            card.diklik.connect(self.handle_card_click)
            self._register_wheel_forwarding(card)
            
            path_poster = e.get("gambar_poster", "")
            if os.path.exists(path_poster):
                with open(path_poster, "rb") as f:
                    card.set_poster(f.read())
            
            # Simpan data event ke map pakai key unik dari database.
            event_key = str(e.get("db_id") or e.get("id") or e.get("event_id") or "")
            if event_key:
                self.event_data_map[event_key] = e

            self.card_layout.addWidget(card)
        self.card_layout.addStretch()

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

        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        if self.detail_event_page is None:
            from detail_event_page import DetailEventPage
            self.detail_event_page = DetailEventPage()
            self.detail_event_page.kembali_diklik.connect(self.show_home_page)
            self.layout_utama.insertWidget(4, self.detail_event_page)
            self.layout_utama.setStretchFactor(self.detail_event_page, 1)

        self.detail_event_page.set_data(data_event)
        self.detail_event_page.show()

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
            pesan_error = "\n".join(errors.values()) if errors else "Data event tidak valid."
            QMessageBox.warning(self, "Event Gagal Dipublikasi", pesan_error)
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

    def show_home_page(self):
        self._hide_all_pages()
        self.navbar_container.show()

        self.spacing_after_navbar.show()
        self.spacing_after_hero.show()

        self.layout_utama.setContentsMargins(60, 20, 60, 40)
        self.layout_utama.setSpacing(0)

        self.hero_widget.show()
        self.event_title.show()
        self.scroll.show()
    
    def show_login_page(self):
        self._hide_all_pages()
        self.navbar_container.hide()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

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
        
    def proses_validasi_admin(self, event_id, status_baru):
        """Mengeksekusi persetujuan atau penolakan event dari Admin"""
        # 1. Ubah status di database
        db_manager.update_event_status(event_id, status_baru)
        
        # 2. Beri notifikasi ke Admin
        aksi = "Disetujui" if status_baru == "approved" else "Ditolak"
        QMessageBox.information(self, "Berhasil", f"Event {event_id} berhasil {aksi}!")
        
        # 3. Refresh tabel di halaman admin (nanti kita buat fungsi ini di admin_page.py)
        self.admin_page.load_data_antrean()
        
        # 4. Refresh layar utama agar event yang di-approve langsung muncul di depan!
        self.refresh_tampilan_homepage()
    
    def on_login_diklik(self, email, password):
            import account_db # Pastikan ini sudah di-import di atas

            user_role = account_db.check_login(email, password)

            if user_role:
                # 1. Ubah state role aplikasi
                self.current_user_role = user_role

                # Simpan email user yang login agar bisa dikirim ke settings
                # dan dipakai oleh YourEventsPanel untuk query event per EO
                self.current_user_email = email

                self.settings_page = None
                
                # 2. Beri notifikasi sukses
                QMessageBox.information(self, "Berhasil", f"Login Sukses sebagai {user_role.upper()}!")
                
                # 3. Panggil fungsi untuk mengubah tampilan navbar
                self.update_navbar_berdasarkan_role()
                
                # 4. Kembali ke halaman utama
                self.show_home_page()
            else:
                QMessageBox.warning(self, "Gagal", "Email atau Password salah!")
                
    def update_navbar_berdasarkan_role(self):
        """Mengubah tampilan Navbar dan isi Menu secara dinamis sesuai role"""
        
        # 1. Bersihkan menu agar tidak terjadi penumpukan (duplikat)
        self.hamburger_menu.clear()

        if self.current_user_role == "guest":
            # --- TAMPILAN GUEST ---
            self.btn_login.setText("  Login")
            self.btn_login.setStyleSheet("background-color: #ff99aa; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
            
            try: self.btn_login.clicked.disconnect() 
            except: pass
            self.btn_login.clicked.connect(self.show_login_page)

            # Guest BISA melihat FAQ dan Setting, tapi TIDAK ADA Add Event
            self.hamburger_menu.addAction(QIcon("assets/question.png"), "FAQ").triggered.connect(self.show_faq_page)
            self.hamburger_menu.addAction(QIcon("assets/gear.png"), "Setting").triggered.connect(self.buka_settings)

        elif self.current_user_role == "eo":
            # --- TAMPILAN EVENT ORGANIZER ---
            self.btn_login.setText("  Hi, Event Organizer!")
            self.btn_login.setStyleSheet("background-color: #2D6A6A; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
            
            try: self.btn_login.clicked.disconnect() 
            except: pass
            self.btn_login.clicked.connect(self.proses_logout)

            # EO punya akses lengkap
            self.hamburger_menu.addAction(QIcon("assets/event.png"), "Add Event").triggered.connect(self.buka_form_input) 
            self.hamburger_menu.addAction(QIcon("assets/event.png"), "My Events")
            self.hamburger_menu.addAction(QIcon("assets/question.png"), "FAQ").triggered.connect(self.show_faq_page)
            self.hamburger_menu.addAction(QIcon("assets/gear.png"), "Setting").triggered.connect(self.buka_settings)

        elif self.current_user_role == "admin":
            # --- TAMPILAN ADMIN ---
            self.btn_login.setText("  Admin Panel")
            self.btn_login.setStyleSheet("background-color: #516465; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
            
            try: self.btn_login.clicked.disconnect() 
            except: pass
            self.btn_login.clicked.connect(self.proses_logout)

            # Menu khusus Admin
            self.hamburger_menu.addAction(QIcon("assets/event.png"), "Dashboard Validasi").triggered.connect(self.show_admin_page)
            self.hamburger_menu.addAction(QIcon("assets/question.png"), "FAQ").triggered.connect(self.show_faq_page)
            self.hamburger_menu.addAction(QIcon("assets/gear.png"), "Setting").triggered.connect(self.buka_settings)
            
    def proses_logout(self):
        # Konfirmasi logout
        jawaban = QMessageBox.question(self, "Logout", "Apakah Anda yakin ingin keluar?", QMessageBox.Yes | QMessageBox.No)
        
        if jawaban == QMessageBox.Yes:
            # Kembalikan state ke guest
            self.current_user_role = "guest"
            self.current_user_email = ""  # Reset email saat logout
            self.settings_page = None
            # Kembalikan tampilan navbar
            self.update_navbar_berdasarkan_role()
            # Buka ulang halaman home
            self.show_home_page()
            QMessageBox.information(self, "Logout", "Berhasil logout.")
        
    def proses_login(self, email, password):
    # Cek ke database
        if account_db.check_login(email, password):
        #   TODO: Nanti kita buat logika ganti tampilan Navbar di sini
            QMessageBox.information(self, "Berhasil", "Login Sukses!")
            self.show_home_page()
        else:
            QMessageBox.warning(self, "Gagal", "Email atau Password salah!")
    
    def buka_settings(self):
        from settings.setting_window import SettingsWindow
        self._hide_all_pages()
        self.navbar_container.hide()

        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        if self.settings_page is None:
            # Kirim email user yang sedang login ke user_data
            # agar YourEventsPanel bisa query event berdasarkan email_eo
            # Email disimpan saat login di self.current_user_email
            self.settings_page = SettingsWindow(
                user_data={
                    "nama"   : "",
                    "bio"    : "",
                    "email"  : getattr(self, "current_user_email", ""),
                    "kontak" : "",
                    "role"   : self.current_user_role,
                    "inisial": ""
                }
            )
            self.settings_page.btn_home.clicked.connect(self.show_home_page)
            # Hubungkan sinyal Add Event dari Settings ke fungsi buka_form_input
            # Dipancarkan saat EO klik "Create your first event now!" di Your Events
            self.settings_page.minta_buka_add_event.connect(self.buka_form_input)
            self.layout_utama.insertWidget(4, self.settings_page)
            self.layout_utama.setStretchFactor(self.settings_page, 1)

        self.settings_page.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Style Fusion agar tampilan konsisten di Windows/Mac/Linux
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())