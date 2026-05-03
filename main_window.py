# ==============================================================
# FILE: main_window.py
# TUGAS: Mengelola tampilan utama (Homepage) Campus Connect
# FITUR: Navbar, Hero Section, Horizontal Scroll Event, dan Add Event Dialog
# DIBUAT OLEH: Jocelyn (fitur-Jocelyn)
# ==============================================================

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from about_page import AboutPage
from faq_page import FAQPage  # ← TAMBAHAN
from add_event_page import AddEventPage # ← TAMBAHAN
from success_page import SuccessPage # ← TAMBAHAN
from crud_events import prepare_create, save_payload

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
        self.init_header()        # Membangun Navbar
        self.layout_utama.addSpacing(40)
        self.init_hero()          # Membangun Judul Besar
        self.layout_utama.addSpacing(30)
        self.init_scroll_area()   # Membangun Wadah Kartu Event
        self.render_event_cards(dummy_events) # Mengisi Kartu dengan Data
        
        self.layout_utama.addStretch() # Mendorong semua ke atas

        # Page references — dibuat lazy (None dulu, baru dibuat saat pertama dibuka)
        self.about_page = None
        self.faq_page = None  # ← TAMBAHAN
        self.add_event_page = None  # ← TAMBAHAN
        self.success_page = None  # ← TAMBAHAN

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
        if self.about_page:
            self.about_page.hide()
        if self.faq_page:
            self.faq_page.hide()
        if self.add_event_page:      
            self.add_event_page.hide()
        if self.success_page:        
            self.success_page.hide()

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
        self.btn_about.setStyleSheet(nav_style)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Bagian Kanan (Login & Hamburger Menu)
        self.btn_login = QPushButton("  Login")
        self.btn_login.setIcon(QIcon("assets/user.png"))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("background-color: #ff99aa; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
        
        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(QIcon("assets/menu.png"))
        self.btn_menu.setIconSize(QSize(24, 24))
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setStyleSheet("background: transparent; border: none;")

<<<<<<< HEAD
        # Custom Styling untuk QMenu (Dropdown) agar tidak warnanya sesuai tema
=======
        # Dropdown Menu Styling
>>>>>>> 8eb470a5e70f717221f3897f7c307398317b8a03
        self.hamburger_menu = QMenu(self)
        self.hamburger_menu.setCursor(Qt.PointingHandCursor)
        self.hamburger_menu.setStyleSheet(f"""
            QMenu {{ background-color: #D2E6E5; color: #5D6B6B; border: 1px solid #BDD7D8; border-radius: 10px; padding: 5px; }}
            QMenu::item {{ background-color: transparent; padding: 8px 25px 8px 10px; border-radius: 5px; }}
            QMenu::item:selected {{ background-color: #BDD7D8; color: #5D6B6B; }}
        """)
        
        # Aksi di dalam Hamburger Menu
        self.hamburger_menu.addAction(QIcon("assets/event.png"), "Add Event").triggered.connect(self.buka_form_input)
        # ← TAMBAHAN: connect FAQ ke show_faq_page
        self.hamburger_menu.addAction(QIcon("assets/question.png"), "FAQ").triggered.connect(self.show_faq_page)
        self.hamburger_menu.addAction(QIcon("assets/gear.png"), "Setting")
        self.btn_menu.setMenu(self.hamburger_menu)

        # Masukkan semua ke layout navbar
        navbar_layout.addWidget(self.logo)
        navbar_layout.addSpacing(30)
        navbar_layout.addWidget(self.btn_home)
        navbar_layout.addWidget(self.btn_about)
        navbar_layout.addSpacerItem(spacer)
        navbar_layout.addWidget(self.btn_login)
        navbar_layout.addSpacing(10)
        navbar_layout.addWidget(self.btn_menu)
        self.layout_utama.addWidget(navbar_container)
        self.btn_about.clicked.connect(self.show_about_page)
        self.btn_home.clicked.connect(self.show_home_page)

    def init_hero(self):
<<<<<<< HEAD
        """Membangun teks sambutan utama"""
        hero_widget = QWidget()
=======
        self.hero_widget = QWidget()
        hero_widget = self.hero_widget
>>>>>>> 8eb470a5e70f717221f3897f7c307398317b8a03
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
<<<<<<< HEAD
        """Membangun area horizontal scroll untuk kartu event"""
        title = QLabel("Highlight / Upcoming Events")
=======
        self.event_title = QLabel("Highlight / Upcoming Events")
        title = self.event_title
>>>>>>> 8eb470a5e70f717221f3897f7c307398317b8a03
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
        for e in data:
            card = EventCard(e)
            card.setCursor(Qt.PointingHandCursor)
            card.diklik.connect(self.handle_card_click) 
            self._register_wheel_forwarding(card)
            
            # Membaca gambar poster dari folder local
            path_poster = e.get("gambar_poster", "")
            if os.path.exists(path_poster):
                with open(path_poster, "rb") as f:
                    card.set_poster(f.read())
            
            self.card_layout.addWidget(card)
        self.card_layout.addStretch()

    def handle_card_click(self, event_id):
        """Respon saat kartu event diklik"""
        QMessageBox.information(self, "Detail Event", f"Membuka detail untuk ID: {event_id}")

    def buka_form_input(self):
<<<<<<< HEAD
        """Membuka dialog Add Event (Blok 3B)"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Event")
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT}; font-family: '{self.font_sans}';")
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("<b>Nama Event:</b>"))
        self.input_nama = QLineEdit()
        layout.addWidget(self.input_nama)
        
        layout.addWidget(QLabel("<b>Deskripsi Singkat:</b>"))
        self.input_desc = QTextEdit()
        layout.addWidget(self.input_desc)
        
        btn_save = QPushButton("Simpan ke List")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("background-color: #ff99aa; color: white; padding: 10px; border-radius: 10px; font-weight: bold;")
        btn_save.clicked.connect(dialog.accept)
        layout.addWidget(btn_save)
        
        dialog.exec_()
=======
        self._hide_all_pages()
        self.navbar_container.hide()
        
        if self.add_event_page is None:
            self.add_event_page = AddEventPage()
            self.add_event_page.event_dipublikasi.connect(self.on_event_dipublikasi)
            self.add_event_page.dibatalkan.connect(self.show_home_page)
            self.layout_utama.insertWidget(4, self.add_event_page)
            # Membuat add_event_page mengisi seluruh ruang yang tersedia
            self.layout_utama.setStretchFactor(self.add_event_page, 1)

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
            "nama_event": data.get("nama_event", ""),
            "deskripsi_event": data.get("deskripsi_singkat", ""),
            "jenis_event": data.get("jenis_event", ""),
            "kategori_event": data.get("kategori", ""),
            "tanggal": data.get("tanggal", ""),
            "waktu": data.get("waktu", ""),
            "poster_event": data.get("gambar_poster", ""),
            "source": data.get("source", "manual"),
        }

        is_valid, errors, payload = prepare_create(form_data)
        if not is_valid:
            pesan_error = "\n".join(errors.values()) if errors else "Data event tidak valid."
            QMessageBox.warning(self, "Event Gagal Dipublikasi", pesan_error)
            return

        save_payload(payload)

        self._hide_all_pages()
        self.layout_utama.setContentsMargins(60, 20, 60, 40)

        if self.success_page is None:
            self.success_page = SuccessPage()
            self.success_page.lihat_event_diklik.connect(self.show_home_page)
            self.success_page.buat_event_lain_diklik.connect(self.buka_form_input)
            self.layout_utama.insertWidget(4, self.success_page)

        self.success_page.set_data(data)
        self.success_page.show()

    # ↓ TAMBAHAN: method untuk buka success page setelah event dipublikasi
    def show_success_page(self):
        self._hide_all_pages()
        self.layout_utama.setContentsMargins(0, 0, 0, 0)

        if self.success_page:
            self.success_page.show()

    def show_home_page(self):
        self._hide_all_pages()
        self.navbar_container.show()

        # Munculkan kembali komponen home
        self.hero_widget.show()
        self.event_title.show()
        self.scroll.show()

>>>>>>> 8eb470a5e70f717221f3897f7c307398317b8a03

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Style Fusion agar tampilan konsisten di Windows/Mac/Linux
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
