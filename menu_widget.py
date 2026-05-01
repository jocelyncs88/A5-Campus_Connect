# ==============================================================
# FILE: menu_widget.py
# TUGAS: Membuat komponen sidebar untuk halaman Settings
#        berisi menu navigasi: Account, Your Events,
#        Notifications, Appearance, dan Language
# DIBUAT OLEH: UI/UX Component Builder
# ==============================================================


# QWidget     = class dasar untuk semua komponen visual di PyQt5
# QVBoxLayout = pengatur tata letak vertikal (atas ke bawah)
# QPushButton = komponen tombol yang bisa diklik
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

# pyqtSignal = cara membuat sinyal komunikasi antar komponen
# Qt         = berisi konstanta seperti Qt.LeftToRight
from PyQt5.QtCore import pyqtSignal, Qt

# QFont = class untuk mengatur jenis dan ukuran font
from PyQt5.QtGui import QFont


# ==============================================================
# CLASS SettingsSidebar
# Mewarisi QWidget artinya SettingsSidebar ADALAH komponen UI
# Komponen ini tampil di sisi kiri halaman Settings
# Berisi tombol navigasi untuk berpindah antar sub-halaman
# ==============================================================
class SettingsSidebar(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Setiap tombol menu punya sinyal tersendiri
    # Saat tombol diklik, sinyal dipancarkan ke halaman Settings
    # di main_window.py agar konten kanan bisa berubah
    # ----------------------------------------------------------

    # Sinyal saat tombol "Account" diklik
    # main_window.py akan menampilkan konten Account Settings
    account_diklik = pyqtSignal()

    # Sinyal saat tombol "Your Events" diklik
    # main_window.py akan menampilkan daftar event milik user
    your_events_diklik = pyqtSignal()

    # Sinyal saat tombol "Notifications" diklik
    # main_window.py akan menampilkan pengaturan notifikasi
    notifications_diklik = pyqtSignal()

    # Sinyal saat tombol "Appearance" diklik
    # main_window.py akan menampilkan pengaturan tampilan
    appearance_diklik = pyqtSignal()

    # Sinyal saat tombol "Language" diklik
    # main_window.py akan menampilkan pengaturan bahasa
    language_diklik = pyqtSignal()


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil OTOMATIS saat objek SettingsSidebar dibuat
    #
    # Parameter:
    #   parent = komponen induk (default None = berdiri sendiri)
    # ----------------------------------------------------------
    def __init__(self, parent=None):

        # Wajib memanggil konstruktor QWidget terlebih dahulu
        # Menginisialisasi semua fitur bawaan QWidget ke objek ini
        super().__init__(parent)

        # Memberi nama objek "settings_sidebar" agar bisa ditarget QSS
        self.setObjectName("settings_sidebar")

        # Memanggil fungsi untuk membangun semua tombol sidebar
        self.setup_ui()

        # Memanggil fungsi untuk mengatur gaya visual sidebar
        self.apply_style()


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun 5 tombol navigasi sidebar Settings
    # Dipanggil sekali saat objek pertama kali dibuat
    # ----------------------------------------------------------
    def setup_ui(self):

        # Layout vertikal agar tombol tersusun dari atas ke bawah
        layout = QVBoxLayout()

        # Jarak 4 piksel antar tombol agar tidak terlalu rapat
        layout.setSpacing(4)

        # Margin dalam sidebar: atas-bawah 16px, kiri-kanan 8px
        # Memberi napas agar tombol tidak mepet ke tepi sidebar
        layout.setContentsMargins(8, 16, 8, 16)


        # ---- TOMBOL ACCOUNT ----

        # Membuat tombol dengan icon orang + teks "Account"
        # Icon menggunakan unicode emoji sesuai mockup Figma
        self.btn_account = QPushButton("  🙍  Account")

        # "sidebar_button" = style tombol normal (belum dipilih)
        self.btn_account.setObjectName("sidebar_button")

        # Menghubungkan klik tombol ke sinyal account_diklik
        # Saat diklik → sinyal dipancarkan → main_window merespons
        self.btn_account.clicked.connect(self.account_diklik.emit)

        # Menambahkan tombol ke layout
        layout.addWidget(self.btn_account)


        # ---- TOMBOL YOUR EVENTS ----

        # Icon kalender + teks "Your events" sesuai mockup Figma
        self.btn_events = QPushButton("  🗓  Your events")

        # Nama objek untuk QSS, sama dengan tombol lainnya
        self.btn_events.setObjectName("sidebar_button")

        # Menghubungkan klik ke sinyal your_events_diklik
        self.btn_events.clicked.connect(self.your_events_diklik.emit)

        layout.addWidget(self.btn_events)


        # ---- TOMBOL NOTIFICATIONS ----

        # Icon lonceng + teks "Notifications" sesuai mockup Figma
        self.btn_notif = QPushButton("  🔔  Notifications")

        self.btn_notif.setObjectName("sidebar_button")

        # Menghubungkan klik ke sinyal notifications_diklik
        self.btn_notif.clicked.connect(self.notifications_diklik.emit)

        layout.addWidget(self.btn_notif)


        # ---- TOMBOL APPEARANCE ----

        # Icon palet + teks "Appearance" sesuai mockup Figma
        self.btn_appearance = QPushButton("  🎨  Appearance")

        self.btn_appearance.setObjectName("sidebar_button")

        # Menghubungkan klik ke sinyal appearance_diklik
        self.btn_appearance.clicked.connect(self.appearance_diklik.emit)

        layout.addWidget(self.btn_appearance)


        # ---- TOMBOL LANGUAGE ----

        # Icon globe + teks "Language" sesuai mockup Figma
        self.btn_language = QPushButton("  🌐  Language")

        self.btn_language.setObjectName("sidebar_button")

        # Menghubungkan klik ke sinyal language_diklik
        self.btn_language.clicked.connect(self.language_diklik.emit)

        layout.addWidget(self.btn_language)


        # Mendorong semua tombol ke atas agar tidak tersebar
        # addStretch() = mengisi sisa ruang kosong di bawah tombol
        # dengan ruang kosong elastis agar tombol selalu rapi di atas 
        # meskipun jendela diperbesar
        layout.addStretch()

        # Menerapkan layout yang sudah berisi semua tombol
        self.setLayout(layout)

        # Mengunci lebar sidebar menjadi 200 piksel
        # Agar konsisten dengan mockup Figma
        self.setFixedWidth(200)


    # ----------------------------------------------------------
    # FUNGSI set_active()
    # Mengubah tampilan tombol yang sedang aktif/dipilih
    # Dipanggil dari main_window.py setiap kali tombol diklik
    #
    # Parameter:
    #   button = objek tombol yang ingin ditandai sebagai aktif
    #            contoh: self.sidebar.set_active(self.sidebar.btn_account)
    # ----------------------------------------------------------
    def set_active(self, button):

        # Reset SEMUA tombol ke style normal dulu
        # Agar hanya satu tombol yang aktif di satu waktu
        for btn in [self.btn_account, self.btn_events,
                    self.btn_notif, self.btn_appearance,
                    self.btn_language]:

            # Kembalikan nama objek ke "sidebar_button" (style normal)
            btn.setObjectName("sidebar_button")

            # unpolish() = hapus style lama yang sudah diterapkan
            btn.style().unpolish(btn)

            # polish() = terapkan ulang style berdasarkan objectName baru
            btn.style().polish(btn)

        # Ubah nama objek tombol yang dipilih menjadi "sidebar_button_active"
        # Sehingga QSS menerapkan style aktif (background lebih gelap, teks tebal)
        button.setObjectName("sidebar_button_active")

        # Terapkan ulang style untuk tombol yang aktif
        button.style().unpolish(button)
        button.style().polish(button)


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual sidebar menggunakan QSS
    # Disesuaikan dengan mockup Figma
    # ----------------------------------------------------------
    def apply_style(self):

        # Mengatur font Inter Regular ukuran 14 untuk semua tombol
        font = QFont("Inter", 14)

        # QFont.Normal = Regular weight sesuai mockup
        font.setWeight(QFont.Normal)

        # Menerapkan font yang sama ke semua tombol sidebar
        for btn in [self.btn_account, self.btn_events,
                    self.btn_notif, self.btn_appearance,
                    self.btn_language]:
            btn.setFont(font)

        self.setStyleSheet("""

            /* Sidebar utama */
            /* Background putih*/
            /* border-radius besar agar sudut membulat */
            QWidget#settings_sidebar {
                background-color: #D2E6E5;
                border-radius: 0px;
                border: none;
            }

            /* Tombol sidebar dalam kondisi normal (belum dipilih) */
            /* Background transparan agar warna sidebar tembus */
            QPushButton#sidebar_button {
                background-color: transparent;
                color: #5D6B6B;
                border: none;
                padding: 12px 16px;
                text-align: left;
                border-radius: 0px;
            }

            /* Efek saat mouse diarahkan ke tombol */
            /* Sedikit menggelap sebagai feedback visual */
            QPushButton#sidebar_button:hover {
                background-color: #D2E6E5;
            }

            /* Efek saat tombol ditekan */
            /* Lebih gelap dari hover sebagai feedback klik */
            QPushButton#sidebar_button:pressed {
                background-color: #a8c8c9;
            }

            /* Tombol yang sedang aktif/dipilih */
            /* Background lebih gelap dan teks tebal */
            /* untuk menandakan halaman yang sedang dibuka */
            QPushButton#sidebar_button_active {
                background-color: #BDD7D8;
                color: #3a5555;
                font-weight: bold;
                border: none;
                padding: 12px 16px;
                text-align: left;
                border-radius: 10px;
            }
        """)