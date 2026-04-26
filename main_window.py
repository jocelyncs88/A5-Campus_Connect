import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from about_page import AboutPage

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
        self.resize(1200, 750)
        
        # Background Canvas Gradient
        self.central_widget = QWidget()
        self.central_widget.setObjectName("mainCanvas")
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"""
            QWidget#mainCanvas {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #5D6B6B, stop:0.25 #BDD7D8, stop:0.5 #D6E6E6, stop:0.75 #D2E6E5, stop:1 #F7CBCA); 
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

        self.about_page = None
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
                        # Shift + wheel juga dipetakan ke horizontal, seperti pola umum desktop.
                        if modifiers & Qt.ShiftModifier:
                            move_by = int(-steps * step_size)
                        else:
                            move_by = int(-steps * step_size)

                if move_by:
                    hbar.setValue(hbar.value() + move_by)
                    event.accept()
                    return True

        return super().eventFilter(watched, event)

    def init_header(self):
        navbar_container = QWidget()
        navbar_container.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT}; border-radius: 40px;")
        navbar_layout = QHBoxLayout(navbar_container)
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

        # Dropdown Menu Styling (Blok 3A)
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
        self.hamburger_menu.addAction(QIcon("assets/question.png"), "FAQ")
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
            card.setCursor(Qt.PointingHandCursor) # Mouse tangan untuk kartu
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
        # Implementasi Jendela Dialog (Blok 3B)
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Event")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT}; font-family: '{self.font_sans}';")
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("<b>Nama Event:</b>"))
        layout.addWidget(QLineEdit())
        layout.addWidget(QLabel("<b>Deskripsi:</b>"))
        layout.addWidget(QTextEdit())
        
        btn_save = QPushButton("Simpan Event")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("background-color: #ff99aa; color: white; padding: 8px; border-radius: 10px; font-weight: bold;")
        btn_save.clicked.connect(dialog.accept)
        layout.addWidget(btn_save)
        
        dialog.exec_()

    def show_about_page(self):
        # sembunyikan homepage
        self.hero_widget.hide()
        self.event_title.hide()
        self.scroll.hide()

        # buat page sekali saja
        if self.about_page is None:
            self.about_page = AboutPage()
            self.layout_utama.insertWidget(4, self.about_page)

        self.about_page.show()


    def show_home_page(self):
        # munculkan homepage
        self.hero_widget.show()
        self.event_title.show()
        self.scroll.show()

        # sembunyikan about
        if self.about_page:
            self.about_page.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())