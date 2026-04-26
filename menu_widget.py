# ==============================================================
# FILE: menu_widget.py
# TUGAS: Membuat komponen dropdown menu yang muncul
#        saat tombol hamburger (≡) diklik
# DIBUAT OLEH: UI/UX Component Builder (Tania)
# ==============================================================


# QWidget     = class dasar untuk semua komponen visual di PyQt5
# QVBoxLayout = pengatur tata letak vertikal (atas ke bawah)
# QPushButton = komponen tombol yang bisa diklik
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

# pyqtSignal = cara membuat sinyal komunikasi antar komponen
# Qt         = berisi konstanta seperti Qt.LeftToRight
from PyQt5.QtCore import pyqtSignal, Qt

# QFont = class untuk mengatur jenis, ukuran, dan ketebalan font
from PyQt5.QtGui import QFont


# ==============================================================
# CLASS DropdownMenu
# Mewarisi QWidget artinya DropdownMenu ADALAH komponen UI
# Komponen ini muncul/sembunyi saat tombol hamburger diklik
# ==============================================================
class DropdownMenu(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Masing-masing menu punya sinyal tersendiri
    # Saat tombol diklik, sinyal dipancarkan ke main_window.py
    # ----------------------------------------------------------

    # Sinyal saat "Add event" diklik
    # main_window.py akan menerima sinyal ini dan membuka halaman Add Event
    add_event_diklik = pyqtSignal()

    # Sinyal saat "FAQ" diklik
    # main_window.py akan menerima sinyal ini dan membuka halaman FAQ
    faq_diklik = pyqtSignal()

    # Sinyal saat "Setting" diklik
    # main_window.py akan menerima sinyal ini dan membuka halaman Setting
    settings_diklik = pyqtSignal()


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil OTOMATIS saat objek DropdownMenu pertama kali dibuat
    #
    # Parameter:
    #   parent = komponen induk (default None = berdiri sendiri)
    # ----------------------------------------------------------
    def __init__(self, parent=None):

        # Wajib memanggil konstruktor QWidget terlebih dahulu
        # Menginisialisasi semua fitur bawaan QWidget ke objek ini
        super().__init__(parent)

        # Memberi nama objek "dropdown_menu" agar bisa ditarget QSS
        # Mirip seperti id="dropdown_menu" di HTML
        self.setObjectName("dropdown_menu")

        # Menyembunyikan menu saat pertama kali dibuat
        # Menu hanya akan muncul saat tombol hamburger diklik
        # Dipanggil lewat fungsi tampilkan() dari main_window.py
        self.hide()

        # Memanggil fungsi untuk membangun tampilan menu
        self.setup_ui()

        # Memanggil fungsi untuk mengatur gaya visual menu
        self.apply_style()


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun 3 tombol menu: Add event, FAQ, Setting
    # Dipanggil sekali saat objek pertama kali dibuat
    # ----------------------------------------------------------
    def setup_ui(self):

        # Layout vertikal agar tombol tersusun dari atas ke bawah
        layout = QVBoxLayout()

        # Tidak ada jarak antar tombol agar terlihat menyatu
        layout.setSpacing(0)

        # Margin dalam dropdown: atas-bawah 8px, kiri-kanan 4px
        # Memberi sedikit napas di dalam kotak menu
        layout.setContentsMargins(4, 8, 4, 8)


        # ---- TOMBOL ADD EVENT ----

        # Membuat tombol dengan icon kalender + teks "Add event"
        # Icon menggunakan unicode emoji sesuai mockup Figma
        self.btn_add_event = QPushButton("  🗓  Add event")

        # Memberi nama objek untuk ditarget QSS di apply_style()
        self.btn_add_event.setObjectName("menu_button")

        # Memastikan teks dan icon rata ke kiri sesuai mockup
        self.btn_add_event.setLayoutDirection(Qt.LeftToRight)

        # Menghubungkan sinyal clicked tombol ke sinyal add_event_diklik
        # Saat tombol diklik → sinyal add_event_diklik dipancarkan
        # main_window.py yang sudah connect() akan menerima sinyal ini
        self.btn_add_event.clicked.connect(self.add_event_diklik.emit)

        # Menambahkan tombol ke layout
        layout.addWidget(self.btn_add_event)


        # ---- TOMBOL FAQ ----

        # Icon lingkaran tanda tanya sesuai mockup Figma
        self.btn_faq = QPushButton("  ❓  FAQ")

        # Memberi nama objek untuk ditarget QSS
        self.btn_faq.setObjectName("menu_button")

        # Teks rata kiri sesuai mockup
        self.btn_faq.setLayoutDirection(Qt.LeftToRight)

        # Menghubungkan klik tombol ke sinyal faq_diklik
        self.btn_faq.clicked.connect(self.faq_diklik.emit)

        # Menambahkan tombol ke layout
        layout.addWidget(self.btn_faq)


        # ---- TOMBOL SETTING ----

        # Icon gear/roda gigi sesuai mockup Figma
        self.btn_settings = QPushButton("  ⚙  Setting")

        # Memberi nama objek untuk ditarget QSS
        self.btn_settings.setObjectName("menu_button")

        # Teks rata kiri sesuai mockup
        self.btn_settings.setLayoutDirection(Qt.LeftToRight)

        # Menghubungkan klik tombol ke sinyal settings_diklik
        self.btn_settings.clicked.connect(self.settings_diklik.emit)

        # Menambahkan tombol ke layout
        layout.addWidget(self.btn_settings)


        # Menerapkan layout yang sudah berisi 3 tombol ke widget ini
        # Tanpa baris ini semua addWidget() di atas tidak akan tampil
        self.setLayout(layout)

        # Mengunci lebar dropdown agar konsisten sesuai proporsi mockup
        self.setFixedWidth(150)


    # ----------------------------------------------------------
    # FUNGSI tampilkan()
    # Dipanggil oleh main_window.py (temanmu)
    # saat tombol hamburger (≡) diklik oleh user
    # ----------------------------------------------------------
    def tampilkan(self):

        # Menampilkan widget dropdown yang sebelumnya disembunyikan
        self.show()

        # Memastikan dropdown muncul di lapisan paling depan
        # raise_() = angkat komponen ke atas semua komponen lain
        # Tanpa ini dropdown bisa tertutup oleh komponen lain
        self.raise_()


    # ----------------------------------------------------------
    # FUNGSI sembunyikan()
    # Dipanggil oleh main_window.py
    # saat user mengklik di luar area dropdown
    # ----------------------------------------------------------
    def sembunyikan(self):

        # Menyembunyikan kembali widget dropdown
        # Widget tidak dihapus dari memori, hanya disembunyikan
        # Sehingga bisa ditampilkan kembali kapanpun
        self.hide()


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual menggunakan QSS (Qt Style Sheet)
    # Disesuaikan dengan mockup Figma
    # ----------------------------------------------------------
    def apply_style(self):

        # Mengatur font Inter Regular ukuran 22 sesuai Figma
        # QFont("Inter", 22) = nama font, ukuran dalam poin
        font = QFont("Inter", 11)

        # QFont.Normal = Regular weight (bukan Bold atau Light)
        # Sesuai Figma: weight Regular
        font.setWeight(QFont.Normal)

        # Menerapkan font yang sama ke semua tombol menu
        self.btn_add_event.setFont(font)
        self.btn_faq.setFont(font)
        self.btn_settings.setFont(font)

        self.setStyleSheet("""

            /* Kotak dropdown utama */
            /* Background putih, sudut sangat membulat, TANPA border */
            /* Sesuai mockup Figma */
            QWidget#dropdown_menu {
                background-color: #D2E6E5;
                border-radius: 16px;
                border: none;
            }

            /* Tombol menu: background transparan, teks rata kiri */
            /* Font diatur via QFont di atas, bukan di sini */
            QPushButton#menu_button {
                background-color: transparent;
                color: #1a1a1a;
                border: none;
                padding: 12px 20px;
                text-align: left;
                font-size: 11px;
                border-radius: 12px;
                line-height: 150%;
            }

            /* Efek saat mouse diarahkan ke tombol */
            /* Sedikit menggelap sebagai feedback visual ke user */
            QPushButton#menu_button:hover {
                background-color: #eeeeee;
            }

            /* Efek saat tombol ditekan */
            /* Lebih gelap dari hover sebagai feedback klik */
            QPushButton#menu_button:pressed {
                background-color: #d0d0d0;
            }
        """)