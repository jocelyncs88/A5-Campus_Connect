import sys
import os
import scraper
import db_manager
from worker_thread import ScraperThread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from about_page import AboutPage
from faq_page import FAQPage  # ← TAMBAHAN
from add_event_page import AddEventPage # ← TAMBAHAN
from success_page import SuccessPage # ← TAMBAHAN
from crud_events import prepare_create, save_payload

# Import class EventCard dari file card_widget.py
# Pastikan file card_widget.py ada di folder yang sama
try:
    from card_widget import EventCard 
except ImportError:
    # Fallback jika file temanmu belum ada agar tidak error saat test
    class EventCard(QWidget):
        diklik = pyqtSignal(str)
        def __init__(self, data):
            super().__init__()
            self.setFixedSize(200, 250)
            layout = QVBoxLayout(self)
            self.label = QLabel(data['nama_event'])
            layout.addWidget(self.label)
            self.setStyleSheet("background: white; border-radius: 15px; color: black;")
        def set_poster(self, data): pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- KONFIGURASI WARNA ---
COLOR_PINK_LIGHT = "#F7CBCA"
COLOR_GRAY_LIGHT = "#D2E6E5"
COLOR_TEXT_PRIMARY = "#5D6B6B"

# Mock Data 6 Event
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
        
        # Load Fonts 
        id_lobster = QFontDatabase.addApplicationFont("assets/LobsterTwo-Regular.ttf")
        id_sans = QFontDatabase.addApplicationFont("assets/GoogleSans_17pt-Regular.ttf")
        self.font_lobster = QFontDatabase.applicationFontFamilies(id_lobster)[0] if id_lobster != -1 else "serif"
        self.font_sans = QFontDatabase.applicationFontFamilies(id_sans)[0] if id_sans != -1 else "sans-serif"

        self.setWindowTitle("Campus Connect - Homepage")
        self.resize(1280, 900)
        
        # Background Canvas Gradient
        self.central_widget = QWidget()
        self.central_widget.setObjectName("mainCanvas")
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"""
            QWidget#mainCanvas {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #B5CECE, stop:0.4 #C8DCDC, stop:0.75 #D6E6E6, stop:1 #F7CBCA); 
            }}
        """)
        
        self.layout_utama = QVBoxLayout(self.central_widget)
        self.layout_utama.setContentsMargins(60, 20, 60, 40)
        
        self.init_header()
        self.layout_utama.addSpacing(40)
        self.init_hero()
        self.layout_utama.addSpacing(30)
        self.init_scroll_area()
        self.render_event_cards(dummy_events)
        self.layout_utama.addStretch()

        # Page references — dibuat lazy (None dulu, baru dibuat saat pertama dibuka)
        self.about_page = None
        self.faq_page = None  # ← TAMBAHAN
        self.add_event_page = None  # ← TAMBAHAN
        self.success_page = None  # ← TAMBAHAN
        
        # === FITUR AUTO UPDATE 15 MENIT ===
        # QTimer sudah di-import melalui 'from PyQt5.QtCore import *'
        self.timer_update = QTimer(self)
        
        # Hubungkan detak timer ke fungsi eksekutor
        self.timer_update.timeout.connect(self.jalankan_auto_update)
        
        # Mulai timer: 15 menit = 15 * 60 detik * 1000 milidetik = 900000 ms
        self.timer_update.start(900000)
        
    def jalankan_auto_update(self):
        print("[AUTO UPDATE] Memulai sinkronisasi data di latar belakang...")
        
        # 1. Ambil data yang sudah ada di database untuk jadi acuan
        data_db = db_manager.get_all_events()
        existing_keys = { (row[2].strip().lower(), row[6].strip().lower()) for row in data_db }
        
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
            db_manager.upsert_event(event)
            
        # 2. Refresh Tampilan UI Layar Utama
        self.refresh_tampilan_homepage()
        print("[AUTO UPDATE] Tampilan homepage berhasil diperbarui dengan data terbaru!")

    def refresh_tampilan_homepage(self):
        """Menghapus kartu lama dan me-render ulang kartu baru dari database."""
        from main import _cache_image
        
        # A. Kosongkan layout kartu yang lama
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # Hapus widget dari memori dengan aman
                widget.deleteLater()
                
        # B. Ambil data terbaru dari database
        data_db_terbaru = db_manager.get_all_events()
        
        # C. Format ulang data dari bentuk baris Database ke bentuk Dictionary untuk UI
        data_untuk_ui = []
        for row in data_db_terbaru:
            event_dict = {
                "event_id": row[1] if len(row) > 1 else "",
                "nama_event": row[2] if len(row) > 2 and row[2] else "Tanpa Judul",
                "deskripsi_singkat": row[3] if len(row) > 3 and row[3] else "...",
                # Ganti baris gambar_poster menjadi ini:
                "gambar_poster": _cache_image(row[4] if len(row) > 4 and row[4] else ""),
                "jenis_event": (row[5] if len(row) > 5 and row[5] else "External").title(),
                "tanggal_waktu": row[6] if len(row) > 6 and row[6] else "TBA",
            }
            data_untuk_ui.append(event_dict)
            
        # D. Cetak ulang kartu-kartu baru ke layar
        self.render_event_cards(data_untuk_ui)

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
        navbar_container = QWidget()
        navbar_container.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT}; border-radius: 40px;")
        navbar_layout = QHBoxLayout(navbar_container)
        self.navbar_container = navbar_container 
        navbar_layout.setContentsMargins(25, 10, 25, 10)

        # Logo
        self.logo = QLabel(f"<span style='font-family: \"{self.font_lobster}\"; font-size: 26px; color: #516465;'>Campus</span><br><span style='font-family: \"{self.font_lobster}\"; font-size: 26px; font-weight: bold; color: #F7CBCA;'>Connect</span>")
        
        # Navigasi
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

        # Login
        self.btn_login = QPushButton("  Login")
        self.btn_login.setIcon(QIcon("assets/user.png"))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("background-color: #ff99aa; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
        
        # Hamburger Menu
        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(QIcon("assets/menu.png"))
        self.btn_menu.setIconSize(QSize(24, 24))
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setStyleSheet("background: transparent; border: none;")

        # Dropdown Menu Styling
        self.hamburger_menu = QMenu(self)
        self.hamburger_menu.setCursor(Qt.PointingHandCursor)
        self.hamburger_menu.setStyleSheet(f"""
            QMenu {{
                background-color: #D2E6E5; 
                color: #5D6B6B;            
                border: 1px solid #BDD7D8; 
                border-radius: 10px;       
                padding: 5px;
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 8px 25px 8px 10px; 
                border-radius: 5px;
            }}
            QMenu::item:selected {{
                background-color: #BDD7D8; 
                color: #5D6B6B;
            }}
        """)
        
        # Aksi Menu
        self.hamburger_menu.addAction(QIcon("assets/event.png"), "Add Event").triggered.connect(self.buka_form_input)
        # ← TAMBAHAN: connect FAQ ke show_faq_page
        self.hamburger_menu.addAction(QIcon("assets/question.png"), "FAQ").triggered.connect(self.show_faq_page)
        self.hamburger_menu.addAction(QIcon("assets/gear.png"), "Setting")
        self.btn_menu.setMenu(self.hamburger_menu)

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
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal {
                border: none; background: rgba(255, 255, 255, 50);
                height: 8px; border-radius: 4px; margin: 0px 20px 0px 20px;
            }
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
        for e in data:
            card = EventCard(e)
            card.setCursor(Qt.PointingHandCursor)
            card.diklik.connect(self.handle_card_click) 
            self._register_wheel_forwarding(card)
            
            path_poster = e.get("gambar_poster", "")
            if os.path.exists(path_poster):
                with open(path_poster, "rb") as f:
                    card.set_poster(f.read())
            
            self.card_layout.addWidget(card)
        self.card_layout.addStretch()

    def handle_card_click(self, event_id):
        QMessageBox.information(self, "Detail Event", f"Membuka detail untuk ID: {event_id}")

    def buka_form_input(self):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
