import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

COLOR_PINK_DARK = "#DD33D2" 
COLOR_PINK_LIGHT = "#F7CBCA"
COLOR_GRAY_LIGHT = "#DDE1E2"
COLOR_TEAL_LIGHT = "#D6E6E6"
COLOR_TEAL_MEDIUM = "#BDD7D8"
COLOR_TEXT_PRIMARY = "#5D6B6B"

dummy_events = [
    {"event_id": "EVT-001", "jenis_event": "External", "nama_event": "Sparta Festival", "deskripsi_singkat": "Live painting and exhibition", "gambar_poster": "assets/dummy_sparta.jpg"},
    {"event_id": "EVT-002", "jenis_event": "Internal", "nama_event": "Social Festival", "deskripsi_singkat": "Social talk and social exhibition", "gambar_poster": "assets/dummy_social.jpg"}
]

class EventCardWidget(QWidget):
    def __init__(self, event_data):
        super().__init__()
        self.setFixedSize(200, 260)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.poster = QLabel()
        self.poster.setStyleSheet("background-color: #ffffff; border-radius: 20px;")
        self.poster.setScaledContents(True)
        self.badge = QLabel(event_data['jenis_event'], self.poster)
        self.badge.move(12, 12)
        self.badge.setStyleSheet("background-color: rgba(0, 0, 0, 110); color: white; padding: 4px 12px; border-radius: 10px; font-size: 10px; font-weight: bold;")
        self.title = QLabel(event_data['nama_event'])
        self.title.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {COLOR_TEXT_PRIMARY}; margin-top: 8px;")
        self.desc = QLabel(event_data['deskripsi_singkat'])
        self.desc.setStyleSheet("color: #777; font-size: 11px;")
        layout.addWidget(self.poster, 4)
        layout.addWidget(self.title)
        layout.addWidget(self.desc)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campus Connect - Homepage")
        self.resize(1200, 750)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("mainCanvas")
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"QWidget#mainCanvas {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {COLOR_TEAL_MEDIUM}, stop:0.3 {COLOR_TEAL_LIGHT}, stop:0.8 {COLOR_PINK_LIGHT}, stop:1 #ffffff); }}")
        self.layout_utama = QVBoxLayout(self.central_widget)
        self.layout_utama.setContentsMargins(60, 20, 60, 40)
        self.init_header()
        self.init_hero()
        self.init_scroll_area()
        self.render_event_cards(dummy_events)

    def init_header(self):
        outer_header = QWidget()
        navbar_container = QWidget()
        navbar_container.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT}; border-radius: 40px;")
        navbar_layout = QHBoxLayout(navbar_container)
        self.logo = QLabel("<span style='font-family: serif; font-size: 26px; color: #516465;'>Campus</span><br><span style='font-family: sans-serif; font-size: 26px; font-weight: bold; color: {COLOR_PINK_LIGHT};'>Connect</span>")
        
        self.btn_home = QPushButton("  Home")
        self.btn_home.setIcon(QIcon("assets/home.png"))
        self.btn_home.setIconSize(QSize(20, 20))
        
        self.btn_about = QPushButton("  About Us")
        self.btn_about.setIcon(QIcon("assets/information-button.png"))
        self.btn_about.setIconSize(QSize(20, 20))

        self.btn_login = QPushButton("  Login")
        self.btn_login.setIcon(QIcon("assets/user.png"))
        self.btn_login.setIconSize(QSize(18, 18))

        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(QIcon("assets/menu.png"))
        self.btn_menu.setIconSize(QSize(24, 24))
        
        nav_style = f"background: transparent; color: {COLOR_TEXT_PRIMARY}; border: none;"
        btn_home.setStyleSheet(nav_style + "font-weight: bold;")
        btn_about.setStyleSheet(nav_style)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        btn_login = QPushButton("👤 Login")
        btn_login.setStyleSheet(f"background-color: {COLOR_PINK_LIGHT}; color: white; border-radius: 12px; padding: 6px 18px; font-weight: bold;")
        navbar_layout.addWidget(self.logo)
        navbar_layout.addWidget(btn_home)
        navbar_layout.addWidget(btn_about)
        navbar_layout.addSpacerItem(spacer)
        navbar_layout.addWidget(btn_login)
        QHBoxLayout(outer_header).addWidget(navbar_container)
        self.layout_utama.addWidget(outer_header)

    def init_hero(self):
        hero_widget = QWidget()
        layout = QVBoxLayout(hero_widget)
        layout.setContentsMargins(0, 80, 0, 40)
        l1 = QLabel("Welcome to,")
        l1.setStyleSheet(f"font-size: 24px; font-style: italic; color: {COLOR_TEXT_PRIMARY};")
        l2 = QLabel("Campus Connect")
        l2.setStyleSheet("font-size: 72px; font-weight: bold; color: #516465;")
        layout.addWidget(l1)
        layout.addWidget(l2)
        self.layout_utama.addWidget(hero_widget)

    def init_scroll_area(self):
        self.layout_utama.addWidget(QLabel("Highlight/Upcoming Events"))
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.card_layout = QHBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        self.layout_utama.addWidget(self.scroll)

    def render_event_cards(self, data):
        for e in data:
            self.card_layout.addWidget(EventCardWidget(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())