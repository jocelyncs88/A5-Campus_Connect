# ==============================================================
# FILE: setting_window.py
# TUGAS: Mengelola tampilan halaman Settings Campus Connect
# FITUR: Sidebar navigasi dan panel konten dinamis per menu
# DIBUAT OLEH: UI/UX Designer (fitur-Settings)
#
# STRUKTUR FILE:
#   - SettingsWindow     : jendela utama (topbar + sidebar + stacked)
#   - Panel Account      : didelegasikan ke settings/account_window.py
#   - Panel Your Events  : buat_panel_your_events()
#   - Panel Notifications: buat_panel_notif()
#   - Panel Appearance   : buat_panel_appearance()
#   - Panel Language     : buat_panel_language()
# ==============================================================

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from toggle_widget import ToggleSwitch
from setting_item_widget import SettingItem
from settings.account_window import AccountPanel
  

# ==============================================================
# KONSTANTA WARNA
# Disamakan persis dengan main_window.py agar tampilan konsisten
# di seluruh aplikasi Campus Connect
# ==============================================================
COLOR_PINK_LIGHT   = "#F7CBCA"   # Warna aksen merah muda (background bawah)
COLOR_GRAY_LIGHT   = "#D2E6E5"   # Warna navbar dan elemen panel kiri
COLOR_TEAL_DARK    = "#516465"   # Warna teks gelap dan avatar
COLOR_TEXT_PRIMARY = "#5D6B6B"   # Warna teks utama (abu kehijauan)
COLOR_TEXT_MUTED   = "#9AABAB"   # Warna teks sekunder / placeholder
COLOR_DIVIDER      = "#D2E6E5"   # Warna garis pembatas antar baris


# ==============================================================
# KONSTANTA ROLE USER
# Digunakan untuk menentukan menu mana yang tampil berbeda
# tergantung siapa yang sedang login ke aplikasi
#
# Tiga kemungkinan role:
#   ROLE_ORGANIZER  → Event Organizer (bisa kelola event sendiri)
#   ROLE_MAHASISWA  → Mahasiswa kampus (bisa daftar / RSVP event)
#   ROLE_UMUM       → Pengunjung umum (akses terbatas)
# ==============================================================
ROLE_ORGANIZER = "organizer"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM      = "umum"


# ==============================================================
# CLASS SettingsWindow
# Mewarisi QDialog agar bisa dibuka sebagai jendela popup
# dari main_window.py tanpa menutup halaman homepage
#
# Cara memanggilnya dari main_window.py:
#   from settings_window import SettingsWindow
#   win = SettingsWindow(user_data=user_data, parent=self)
#   win.exec_()
# ==============================================================
class SettingsWindow(QWidget):

    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil otomatis saat objek SettingsWindow dibuat
    #
    # Parameter:
    #   user_data  = dictionary berisi data user yang sedang login
    #                contoh: {
    #                   "nama": "Event Organizer",
    #                   "bio": "Music Festival",
    #                   "email": "eventorganizer@gmail.com",
    #                   "kontak": "+6281-3456-7898",
    #                   "role": "organizer",
    #                   "inisial": "EO"
    #                }
    #   parent     = komponen induk (biasanya MainWindow)
    # ----------------------------------------------------------
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)

        # Menyimpan data user sebagai atribut agar bisa diakses
        # oleh semua fungsi di dalam class ini
        # Jika tidak ada data yang dikirim, gunakan data kosong sebagai fallback
        # (menandakan user belum login)
        self.user_data = user_data or {
            "nama"   : "",
            "bio"    : "",
            "email"  : "",
            "kontak" : "",
            "role"   : ROLE_UMUM,
            "inisial": ""
        }

        # Mengambil nilai role dari user_data untuk keperluan logika
        # tampilan menu yang berbeda-beda sesuai role
        self.role = self.user_data.get("role", ROLE_UMUM)

        # Setup dasar jendela dialog
        self.setWindowTitle("Settings - Campus Connect")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Memuat font custom yang sama dengan main_window.py
        # agar tipografi konsisten di seluruh aplikasi
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        id_lobster = QFontDatabase.addApplicationFont(
            os.path.join(BASE_DIR, "assets", "LobsterTwo-Regular.ttf")
        )
        id_sans = QFontDatabase.addApplicationFont(
            os.path.join(BASE_DIR, "assets", "GoogleSans_17pt-Regular.ttf")
        )
        self.font_lobster = (
            QFontDatabase.applicationFontFamilies(id_lobster)[0]
            if id_lobster != -1 else "serif"
        )
        self.font_sans = (
            QFontDatabase.applicationFontFamilies(id_sans)[0]
            if id_sans != -1 else "sans-serif"
        )

        # Menerapkan background gradient yang sama dengan main_window.py
        # agar transisi visual antara homepage dan settings terasa mulus
        self.setStyleSheet(f"""
            QWidget {{
                font-family: '{self.font_sans}';
                background: transparent;   # ← ganti jadi transparent
            }}
        """)

        # Memanggil fungsi-fungsi pembangun UI secara berurutan
        self.setup_ui()


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun kerangka utama jendela Settings:
    #   - Topbar (judul + tombol Home)
    #   - Body utama yang terbagi dua:
    #       kiri  = sidebar menu navigasi
    #       kanan = area konten panel aktif (QStackedWidget)
    # ----------------------------------------------------------
    def setup_ui(self):

        # Layout vertikal utama: topbar di atas, body di bawah
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---- TOPBAR ----
        topbar = self.buat_topbar()
        root_layout.addWidget(topbar)

        # ---- BODY (Sidebar + Konten) ----
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar kiri berisi daftar menu navigasi settings
        sidebar = self.buat_sidebar()
        body_layout.addWidget(sidebar)

        # Area konten kanan tempat panel aktif ditampilkan
        # QStackedWidget = "tumpukan halaman" — hanya 1 halaman tampil sekaligus
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        # Membuat semua panel dan memasukkannya ke stacked_widget
        # urutan index: 0=Account, 1=YourEvents, 2=Notifications, 3=Appearance, 4=Language
        #
        # Panel Account didelegasikan ke AccountPanel (settings/account_window.py)
        # agar kode tidak duplikat dan lebih mudah di-maintain per file
        self.panel_account     = AccountPanel(
            user_data=self.user_data,
            stacked_widget=self.stacked_widget
        )
        self.panel_your_events = self.buat_panel_your_events()
        self.panel_notif       = self.buat_panel_notif()
        self.panel_appearance  = self.buat_panel_appearance()
        self.panel_language    = self.buat_panel_language()

        self.stacked_widget.addWidget(self.panel_account)     # index 0
        self.stacked_widget.addWidget(self.panel_your_events) # index 1
        self.stacked_widget.addWidget(self.panel_notif)       # index 2
        self.stacked_widget.addWidget(self.panel_appearance)  # index 3
        self.stacked_widget.addWidget(self.panel_language)    # index 4

        body_layout.addWidget(self.stacked_widget, stretch=1)
        root_layout.addWidget(body, stretch=1)

        # Tampilkan panel Account sebagai tampilan awal (index 0)
        self.stacked_widget.setCurrentIndex(0)


    # ----------------------------------------------------------
    # FUNGSI buat_topbar()
    # Membangun bagian atas halaman Settings:
    #   - Icon hamburger + judul "Settings" di kiri
    #   - Tombol "Home" dan avatar user di kanan
    #
    # Return: QWidget siap pakai
    # ----------------------------------------------------------
    def buat_topbar(self):
        topbar = QWidget()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet(f"background-color: white; border-bottom: 1px solid {COLOR_DIVIDER};")

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(20, 0, 20, 0)

        # Icon hamburger (≡) sebagai representasi menu settings
        icon_menu = QLabel("≡")
        icon_menu.setStyleSheet(f"font-size: 22px; color: {COLOR_TEXT_PRIMARY}; font-weight: bold;")

        # Judul halaman
        lbl_title = QLabel("Settings")
        lbl_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Tombol Home — menutup jendela settings dan kembali ke homepage
        self.btn_home = QPushButton("  Home")
        self.btn_home.setIcon(QIcon("assets/home.png"))
        self.btn_home.setIconSize(QSize(16, 16))
        self.btn_home.setCursor(Qt.PointingHandCursor)
        self.btn_home.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLOR_TEXT_PRIMARY};
                font-size: 13px;
                border: none;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                color: {COLOR_TEAL_DARK};
                font-weight: bold;
            }}
        """)
        self.btn_home.clicked.connect(self.close)

        # Avatar lingkaran berisi inisial nama user
        inisial = self.user_data.get("inisial", "")
        avatar = QLabel(inisial if inisial else "")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {COLOR_TEAL_DARK};
            color: white;
            font-weight: bold;
            font-size: 13px;
            border-radius: 18px;
        """)

        layout.addWidget(icon_menu)
        layout.addSpacing(10)
        layout.addWidget(lbl_title)
        layout.addSpacerItem(spacer)
        layout.addWidget(self.btn_home)
        layout.addSpacing(8)
        layout.addWidget(avatar)

        return topbar


    # ----------------------------------------------------------
    # FUNGSI buat_sidebar()
    # Membangun panel navigasi kiri berisi daftar menu settings
    #
    # Return: QWidget siap pakai
    # ----------------------------------------------------------
    def buat_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"background-color: white; border-right: 1px solid {COLOR_DIVIDER};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)

        # Definisi menu: (label teks, index panel di stacked_widget, nama file icon)
        menus = [
            ("Account",       0, "profile"),
            ("Your events",   1, "event"),
            ("Notifications", 2, "bell"),
            ("Appearance",    3, "paint"),
            ("Language",      4, "language"),
        ]

        # Menyimpan semua tombol sidebar agar bisa di-reset saat menu berganti
        self.sidebar_buttons = []

        for label, index, icon_file in menus:
            btn = QPushButton(f"  {label}")
            btn.setIcon(QIcon(f"assets/{icon_file}.png"))
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setStyleSheet(self._style_sidebar_btn(aktif=False))
            btn.clicked.connect(lambda checked, i=index: self.switch_panel(i))

            layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        layout.addStretch()

        # Aktifkan tombol pertama (Account) sebagai default
        self.sidebar_buttons[0].setChecked(True)
        self.sidebar_buttons[0].setStyleSheet(self._style_sidebar_btn(aktif=True))

        return sidebar


    # ----------------------------------------------------------
    # FUNGSI _style_sidebar_btn()
    # Mengembalikan string QSS untuk tombol sidebar
    #
    # Parameter:
    #   aktif = True  → style tombol yang sedang dipilih
    #   aktif = False → style tombol normal
    # ----------------------------------------------------------
    def _style_sidebar_btn(self, aktif=False):
        if aktif:
            return f"""
                QPushButton {{
                    background-color: {COLOR_GRAY_LIGHT};
                    color: {COLOR_TEAL_DARK};
                    font-weight: bold;
                    font-size: 13px;
                    text-align: left;
                    border: none;
                    border-left: 3px solid {COLOR_TEAL_DARK};
                    padding-left: 20px;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_TEXT_PRIMARY};
                    font-size: 13px;
                    text-align: left;
                    border: none;
                    padding-left: 23px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_GRAY_LIGHT};
                    color: {COLOR_TEAL_DARK};
                }}
            """


    # ----------------------------------------------------------
    # FUNGSI switch_panel()
    # Dipanggil setiap kali user mengklik salah satu menu di sidebar
    # Tugasnya:
    #   1. Mengganti panel konten yang tampil di kanan
    #   2. Mengubah style tombol yang aktif vs tidak aktif
    #
    # Parameter:
    #   index = index panel di stacked_widget (0–4)
    # ----------------------------------------------------------
    def switch_panel(self, index):
        self.stacked_widget.setCurrentIndex(index)

        for i, btn in enumerate(self.sidebar_buttons):
            aktif = (i == index)
            btn.setChecked(aktif)
            btn.setStyleSheet(self._style_sidebar_btn(aktif=aktif))


    # ==========================================================
    # ---- PANEL-PANEL KONTEN ----
    # Panel Account → didelegasikan ke AccountPanel (account_window.py)
    # Panel lainnya → dibangun di bawah ini
    # ==========================================================


    # ----------------------------------------------------------
    # FUNGSI buat_panel_your_events()
    # Membangun panel "Your Events" yang BERBEDA sesuai role:
    #
    #   ROLE_ORGANIZER → daftar event yang pernah dibuat + tombol tambah event
    #   ROLE_MAHASISWA → daftar event yang pernah didaftarkan / di-RSVP
    #   ROLE_UMUM      → pesan bahwa fitur ini tidak tersedia + ajakan login
    # ----------------------------------------------------------
    def buat_panel_your_events(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Your Events")
        lbl_judul.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_judul)

        if self.role == ROLE_ORGANIZER:
            lbl_info = QLabel("Event yang pernah kamu buat akan muncul di sini.")
            lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
            layout.addWidget(lbl_info)

            btn_tambah = QPushButton("+ Tambah Event Baru")
            btn_tambah.setCursor(Qt.PointingHandCursor)
            btn_tambah.setFixedWidth(200)
            btn_tambah.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ff99aa;
                    color: white;
                    border-radius: 20px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                }}
                QPushButton:hover {{ background-color: #ff7799; }}
            """)
            layout.addWidget(btn_tambah)

        elif self.role == ROLE_MAHASISWA:
            lbl_info = QLabel("Event yang pernah kamu ikuti akan muncul di sini.")
            lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
            layout.addWidget(lbl_info)

        else:
            lbl_info = QLabel("Fitur ini hanya tersedia untuk pengguna terdaftar.\nSilakan login untuk mengakses riwayat event kamu.")
            lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
            lbl_info.setWordWrap(True)
            layout.addWidget(lbl_info)

        layout.addStretch()
        return panel


    # ----------------------------------------------------------
    # FUNGSI buat_panel_notif()
    # Membangun panel "Notifications" yang BERBEDA sesuai role:
    #
    #   ROLE_ORGANIZER → toggle notifikasi untuk pendaftar event mereka
    #   ROLE_MAHASISWA → toggle notifikasi untuk event yang diikuti
    #   ROLE_UMUM      → toggle notifikasi umum (terbatas)
    # ----------------------------------------------------------
    def buat_panel_notif(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Notifications")
        lbl_judul.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_judul)

        if self.role == ROLE_ORGANIZER:
            deskripsi = "Atur kapan kamu ingin mendapat notifikasi tentang pendaftar event yang kamu buat."
        elif self.role == ROLE_MAHASISWA:
            deskripsi = "Atur kapan kamu ingin mendapat pengingat untuk event yang kamu ikuti."
        else:
            deskripsi = "Atur preferensi notifikasi umum kamu di sini."

        lbl_info = QLabel(deskripsi)
        lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        item = SettingItem(
            judul="New registrant",
            deskripsi="Get alerts every time a user registers",
            nama_setting="notif_registrant",
            default_on=True
        )
        layout.addWidget(item)

        layout.addStretch()
        return panel


    # ----------------------------------------------------------
    # FUNGSI buat_panel_appearance()
    # Membangun panel "Appearance" berisi pengaturan tampilan
    # Tampilan panel ini SAMA untuk semua role user
    # ----------------------------------------------------------
    def buat_panel_appearance(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Appearance")
        lbl_judul.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_judul)

        lbl_info = QLabel("Pengaturan tema dan tampilan akan hadir di sprint berikutnya.")
        lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-style: italic;")
        layout.addWidget(lbl_info)

        layout.addStretch()
        return panel


    # ----------------------------------------------------------
    # FUNGSI buat_panel_language()
    # Membangun panel "Language" berisi pengaturan bahasa antarmuka
    # Tampilan panel ini SAMA untuk semua role user
    # ----------------------------------------------------------
    def buat_panel_language(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Language")
        lbl_judul.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_judul)

        lbl_info = QLabel("Pengaturan bahasa antarmuka akan hadir di sprint berikutnya.")
        lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-style: italic;")
        layout.addWidget(lbl_info)

        layout.addStretch()
        return panel


# ==============================================================
# BLOK TESTING MANDIRI
# Jalankan file ini langsung (python settings_window.py) untuk
# melihat preview tampilan tanpa harus membuka main_window.py
#
# Untuk mengganti role yang ditest, ubah nilai "role" di user_dummy
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Data dummy untuk keperluan testing tampilan
    # Kosongkan nilai untuk simulasi user belum login
    user_dummy = {
        "nama"   : "",
        "bio"    : "",
        "email"  : "",
        "kontak" : "",
        "role"   : ROLE_UMUM,   # Ganti ke ROLE_ORGANIZER atau ROLE_MAHASISWA untuk test role lain
        "inisial": ""
    }

    window = SettingsWindow(user_data=user_dummy)
    window.show()
    sys.exit(app.exec_())
