import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- WARNA-WARNA UTAMA ---
COLOR_PINK_LIGHT = "#F7CBCA"
COLOR_GRAY_LIGHT = "#D2E6E5"
COLOR_TEAL_LIGHT = "#D6E6E6"
COLOR_TEAL_MEDIUM = "#BDD7D8"
COLOR_TEXT_PRIMARY = "#5D6B6B"

dummy_events = [
    {
        "event_id": "EVT-001", 
        "jenis_event": "External", 
        "nama_event": "Sparta Festival", 
        "deskripsi_singkat": "Live painting and exhibition", 
        "gambar_poster": os.path.join(BASE_DIR, "assets", "dummy_sparta.jpg")
    },
    {
        "event_id": "EVT-002", 
        "jenis_event": "Internal", 
        "nama_event": "Social Festival", 
        "deskripsi_singkat": "Social talk and social exhibition", 
        "gambar_poster": os.path.join(BASE_DIR, "assets", "dummy_social.jpg")
    },
    {
        "event_id": "EVT-003", 
        "jenis_event": "Internal", 
        "nama_event": "Kelas Karir 4.0", 
        "deskripsi_singkat": "Career talk", 
        "gambar_poster": os.path.join(BASE_DIR, "assets", "career_40.png")
    },
    {
        "event_id": "EVT-004", 
        "jenis_event": "Internal", 
        "nama_event": "Polban After Campus", 
        "deskripsi_singkat": "Career preparation", 
        "gambar_poster": os.path.join(BASE_DIR, "assets", "after_campus.jpg")
    },
    {
        "event_id": "EVT-005", 
        "jenis_event": "Internal", 
        "nama_event": "Malam Gala Mahasiswa", 
        "deskripsi_singkat": "Got talent", 
        "gambar_poster": os.path.join(BASE_DIR, "assets", "gala.jpg")
    }
]

class EventCardWidget(QWidget):
    def __init__(self, event_data):
        super().__init__()
        # FIX 1: Ukuran tetap agar kartu tidak gepeng/melebar saat fullscreen
        self.setFixedSize(220, 310) 
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.poster = QLabel()
        self.poster.setFixedHeight(220) # Poster kotak sempurna
        self.poster.setStyleSheet("background-color: #ffffff; border-radius: 20px;")
        self.poster.setScaledContents(True)
        
        self.badge = QLabel(event_data['jenis_event'], self.poster)
        self.badge.move(12, 12)
        self.badge.setStyleSheet("background-color: rgba(0, 0, 0, 110); color: white; padding: 4px 12px; border-radius: 10px; font-size: 10px; font-weight: bold;")
        
        path_gambar = event_data['gambar_poster']
        if os.path.exists(path_gambar):
            self.poster.setPixmap(QPixmap(path_gambar))
        else:
            self.poster.setText("Gambar\nNot Found")
            self.poster.setAlignment(Qt.AlignCenter)
            self.poster.setStyleSheet("background-color: #ddd; color: #777; border-radius: 20px;")

        self.title = QLabel(event_data['nama_event'])
        self.title.setWordWrap(True)
        self.title.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {COLOR_TEXT_PRIMARY}; margin-top: 5px;")
        
        self.desc = QLabel(event_data['deskripsi_singkat'])
        self.desc.setStyleSheet("color: #777; font-size: 11px;")
        
        layout.addWidget(self.poster)
        layout.addWidget(self.title)
        layout.addWidget(self.desc)
        layout.addStretch() # Pastikan teks rapat ke poster

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load Fonts
        QFontDatabase.addApplicationFont("assets/LobsterTwo-Bold.ttf")
        QFontDatabase.addApplicationFont("assets/LobsterTwo-Italic.ttf")
        id_lobster = QFontDatabase.addApplicationFont("assets/LobsterTwo-Regular.ttf")
        
        QFontDatabase.addApplicationFont("assets/GoogleSans_17pt-Bold.ttf")
        QFontDatabase.addApplicationFont("assets/GoogleSans_17pt-Italic.ttf")
        id_sans = QFontDatabase.addApplicationFont("assets/GoogleSans_17pt-Regular.ttf")

        self.font_lobster = QFontDatabase.applicationFontFamilies(id_lobster)[0] if id_lobster != -1 else "serif"
        self.font_sans = QFontDatabase.applicationFontFamilies(id_sans)[0] if id_sans != -1 else "sans-serif"

        self.setFont(QFont(self.font_sans, 10))
        self.setWindowTitle("Campus Connect - Homepage")
        self.resize(1200, 750)
        
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
        
        # FIX 2: Layout Utama menggunakan Spacing agar tidak menciut ke tengah
        self.init_header()
        self.layout_utama.addSpacing(40) # Jarak navbar ke Hero
        
        self.init_hero()
        self.layout_utama.addSpacing(30) # Jarak Hero ke Events
        
        self.init_scroll_area()
        self.render_event_cards(dummy_events)
        
        # Dorong semua konten ke atas
        self.layout_utama.addStretch()

    def init_header(self):
        outer_header = QWidget()
        navbar_container = QWidget()
        navbar_container.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT}; border-radius: 40px;")
        navbar_layout = QHBoxLayout(navbar_container)
        navbar_layout.setContentsMargins(25, 10, 25, 10)

        self.logo = QLabel(
            f"<span style='font-family: \"{self.font_lobster}\"; font-size: 26px; color: #516465;'>Campus</span><br>"
            f"<span style='font-family: \"{self.font_lobster}\"; font-size: 26px; font-weight: bold; color: #F7CBCA;'>Connect</span>"
        )
        
        self.btn_home = QPushButton("  Home")
        self.btn_home.setIcon(QIcon("assets/home.png"))
        self.btn_home.setIconSize(QSize(20, 20))
        self.btn_home.setCursor(Qt.PointingHandCursor)
        
        self.btn_about = QPushButton("  About Us")
        self.btn_about.setIcon(QIcon("assets/information-button.png"))
        self.btn_about.setIconSize(QSize(20, 20))
        self.btn_about.setCursor(Qt.PointingHandCursor)

        self.btn_login = QPushButton("  Login")
        self.btn_login.setIcon(QIcon("assets/user.png"))
        self.btn_login.setIconSize(QSize(18, 18))
        self.btn_login.setCursor(Qt.PointingHandCursor)

        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(QIcon("assets/menu.png"))
        self.btn_menu.setIconSize(QSize(24, 24))
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        
        nav_style = f"font-family: \"{self.font_sans}\"; background: transparent; color: {COLOR_TEXT_PRIMARY}; border: none; font-size: 14px;"
        self.btn_home.setStyleSheet(nav_style + "font-weight: bold;")
        self.btn_about.setStyleSheet(nav_style)
        self.btn_login.setStyleSheet(f"font-family: \"{self.font_sans}\"; background-color: {COLOR_PINK_LIGHT}; color: white; border-radius: 20px; padding: 10px 25px; font-weight: bold;")
        self.btn_menu.setStyleSheet("background: transparent; border: none;")

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        navbar_layout.addWidget(self.logo)
        navbar_layout.addSpacing(30)
        navbar_layout.addWidget(self.btn_home)
        navbar_layout.addWidget(self.btn_about)
        navbar_layout.addSpacerItem(spacer)
        navbar_layout.addWidget(self.btn_login)
        navbar_layout.addSpacing(10)
        navbar_layout.addWidget(self.btn_menu)
        
        header_layout = QHBoxLayout(outer_header)
        header_layout.addWidget(navbar_container)
        self.layout_utama.addWidget(outer_header)

    def init_hero(self):
        hero_widget = QWidget()
        layout = QVBoxLayout(hero_widget)
        layout.setContentsMargins(0, 20, 0, 10)
        
        l1 = QLabel("Welcome to,")
        l1.setStyleSheet(f"font-family: \"{self.font_sans}\"; font-size: 24px; font-style: italic; color: {COLOR_TEXT_PRIMARY};")
        
        l2 = QLabel("Campus Connect")
        l2.setStyleSheet(f"font-family: \"{self.font_lobster}\"; font-size: 72px; font-weight: bold; color: #516465;")
        
        layout.addWidget(l1)
        layout.addWidget(l2)
        self.layout_utama.addWidget(hero_widget)

    def init_scroll_area(self):
        title = QLabel("Highlight / Upcoming Events")
        title.setStyleSheet(f"font-family: {self.font_sans}; font-weight: bold; font-size: 18px; color: {COLOR_TEXT_PRIMARY}; margin-bottom: 10px;")
        self.layout_utama.addWidget(title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        # FIX 3: Batasi tinggi scroll area agar kartu tidak melar ke bawah
        self.scroll.setFixedHeight(340) 
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;") 
        
        self.card_layout = QHBoxLayout(self.scroll_content)
        self.card_layout.setSpacing(25)
        self.card_layout.setContentsMargins(10, 0, 10, 0)
        self.card_layout.setAlignment(Qt.AlignLeft)
        
        self.scroll.setWidget(self.scroll_content)
        self.layout_utama.addWidget(self.scroll)

    def render_event_cards(self, data):
        for e in data:
            card = EventCardWidget(e)
            self.card_layout.addWidget(card)
        self.card_layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())