# ==============================================================
# FILE: settings_window.py
# TUGAS: Mengelola tampilan halaman Settings Campus Connect
# FITUR: Sidebar navigasi, Account Settings, dan panel konten
#        dinamis yang menyesuaikan role user
# DIBUAT OLEH: UI/UX Designer (fitur-Settings)
# ==============================================================

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


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
#   win = SettingsWindow(user_role=ROLE_ORGANIZER, parent=self)
#   win.exec_()
# ==============================================================
class SettingsWindow(QDialog):

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
    #                   "role": "organizer"
    #                }
    #   parent     = komponen induk (biasanya MainWindow)
    # ----------------------------------------------------------
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)

        # Menyimpan data user sebagai atribut agar bisa diakses
        # oleh semua fungsi di dalam class ini
        # Jika tidak ada data yang dikirim, gunakan data dummy sebagai fallback
        self.user_data = user_data or {
            "nama"   : "Event Organizer",
            "bio"    : "Music Festival",
            "email"  : "eventorganizer@gmail.com",
            "kontak" : "+6281-3456-7898",
            "role"   : ROLE_ORGANIZER,
            "inisial": "EO"
        }

        # Mengambil nilai role dari user_data untuk keperluan logika
        # tampilan menu yang berbeda-beda sesuai role
        self.role = self.user_data.get("role", ROLE_UMUM)

        # Menyimpan referensi ke panel konten yang sedang aktif
        # Digunakan oleh fungsi switch_panel() untuk mengganti konten
        self.panel_aktif = None

        # Setup dasar jendela dialog
        self.setWindowTitle("Settings - Campus Connect")
        self.setFixedSize(900, 620)
        self.setModal(True)  # Memblokir interaksi ke window di belakangnya

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
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0   #BDD7D8,
                    stop:0.5 #D6E6E6,
                    stop:0.75 #D2E6E5,
                    stop:1   #F7CBCA
                );
                font-family: '{self.font_sans}';
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
    #       kanan = area konten panel aktif
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
        # QSplitter memungkinkan lebar sidebar bisa digeser oleh user
        # Sidebar → kiri, Panel konten → kanan
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
        self.panel_account      = self.buat_panel_account()
        self.panel_your_events  = self.buat_panel_your_events()
        self.panel_notif        = self.buat_panel_notif()
        self.panel_appearance   = self.buat_panel_appearance()
        self.panel_language     = self.buat_panel_language()

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
        btn_home = QPushButton("🏠 Home")
        btn_home.setCursor(Qt.PointingHandCursor)
        btn_home.setStyleSheet(f"""
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
        btn_home.clicked.connect(self.close)  # Menutup dialog saat diklik

        # Avatar lingkaran berisi inisial nama user
        inisial = self.user_data.get("inisial", "??")
        avatar = QLabel(inisial)
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
        layout.addWidget(btn_home)
        layout.addSpacing(8)
        layout.addWidget(avatar)

        return topbar


    # ----------------------------------------------------------
    # FUNGSI buat_sidebar()
    # Membangun panel navigasi kiri berisi daftar menu settings
    #
    # Daftar menu dan ikonnya:
    #   Account       → ikon orang
    #   Your Events   → ikon kalender (tampilan tergantung role)
    #   Notifications → ikon lonceng (tampilan tergantung role)
    #   Appearance    → ikon palet
    #   Language      → ikon teks A
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

        # Definisi menu: (label teks, index panel di stacked_widget, unicode icon)
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
            btn = QPushButton(f"  {label}")   # ← hapus {icon} dari teks
            btn.setIcon(QIcon(f"assets/{icon_file}.png"))   # ← tambahkan icon gambar
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setStyleSheet(self._style_sidebar_btn(aktif=False))
            btn.clicked.connect(lambda checked, i=index: self.switch_panel(i))

            layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        layout.addStretch()  # Mendorong semua tombol ke atas

        # Aktifkan tombol pertama (Account) sebagai default
        self.sidebar_buttons[0].setChecked(True)
        self.sidebar_buttons[0].setStyleSheet(self._style_sidebar_btn(aktif=True))

        return sidebar


    # ----------------------------------------------------------
    # FUNGSI _style_sidebar_btn()
    # Mengembalikan string QSS untuk tombol sidebar
    # Dipisah agar mudah diubah tanpa menyentuh logika
    #
    # Parameter:
    #   aktif = True  → tampilkan style tombol yang sedang dipilih
    #   aktif = False → tampilkan style tombol normal
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
        # Ganti panel yang tampil
        self.stacked_widget.setCurrentIndex(index)

        # Reset style semua tombol ke kondisi tidak aktif
        for i, btn in enumerate(self.sidebar_buttons):
            aktif = (i == index)
            btn.setChecked(aktif)
            btn.setStyleSheet(self._style_sidebar_btn(aktif=aktif))


    # ==========================================================
    # ---- PANEL-PANEL KONTEN ----
    # Setiap fungsi di bawah membangun satu panel untuk satu menu
    # Semua panel dimasukkan ke self.stacked_widget di setup_ui()
    # ==========================================================


    # ----------------------------------------------------------
    # FUNGSI buat_panel_account()
    # Membangun panel "Account Settings" yang berisi:
    #   - Judul halaman
    #   - Sub-judul "Basic info"
    #   - Baris profile picture (dengan avatar + tombol Upload/Remove)
    #   - Baris-baris info: Name, Bio, Email, Contact
    #
    # Tampilan panel ini SAMA untuk semua role user
    # ----------------------------------------------------------
    def buat_panel_account(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(0)

        # ---- Judul halaman ----
        lbl_judul = QLabel("Account Settings")
        lbl_judul.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLOR_TEXT_PRIMARY};
            margin-bottom: 24px;
        """)
        layout.addWidget(lbl_judul)
        layout.addSpacing(20)

        # ---- Sub-judul "Basic info" ----
        lbl_basic = QLabel("Basic info")
        lbl_basic.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLOR_TEXT_PRIMARY};
            margin-bottom: 12px;
        """)
        layout.addWidget(lbl_basic)
        layout.addSpacing(10)

        # ---- Garis pembatas atas ----
        layout.addWidget(self._buat_divider())

        # ---- Baris Profile Picture ----
        baris_foto = self._buat_baris_foto()
        layout.addWidget(baris_foto)
        layout.addWidget(self._buat_divider())

        # ---- Baris-baris info dari dictionary user_data ----
        # Setiap baris berisi: label kiri (nama field) + nilai + panah (>)
        fields = [
            ("Name",    self.user_data.get("nama",   "")),
            ("Bio",     self.user_data.get("bio",    "")),
            ("Email",   self.user_data.get("email",  "")),
            ("Contact", self.user_data.get("kontak", "")),
        ]

        for field_label, field_value in fields:
            baris = self._buat_baris_info(field_label, field_value)
            layout.addWidget(baris)
            layout.addWidget(self._buat_divider())

        layout.addStretch()  # Mendorong semua konten ke atas

        return panel


    # ----------------------------------------------------------
    # FUNGSI _buat_baris_foto()
    # Membangun baris khusus untuk menampilkan dan mengubah foto profil
    # Isi baris (dari kiri ke kanan):
    #   - Teks "Profile picture" di kiri (warna muted)
    #   - Avatar lingkaran dengan inisial di tengah-kanan
    #   - Teks "Upload new picture" + "Remove" di kanan
    #
    # Return: QWidget baris siap pakai
    # ----------------------------------------------------------
    def _buat_baris_foto(self):
        baris = QWidget()
        baris.setStyleSheet("background: transparent;")
        baris.setFixedHeight(80)

        layout = QHBoxLayout(baris)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label nama field di kiri
        lbl_field = QLabel("Profile picture")
        lbl_field.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        lbl_field.setFixedWidth(220)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Avatar lingkaran berisi inisial (sama seperti di topbar)
        inisial = self.user_data.get("inisial", "??")
        avatar = QLabel(inisial)
        avatar.setFixedSize(48, 48)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {COLOR_TEAL_DARK};
            color: white;
            font-weight: bold;
            font-size: 16px;
            border-radius: 24px;
        """)

        # Kolom kanan: tombol Upload dan Remove
        action_col = QWidget()
        action_col.setStyleSheet("background: transparent;")
        action_layout = QVBoxLayout(action_col)
        action_layout.setContentsMargins(12, 0, 0, 0)
        action_layout.setSpacing(2)

        btn_upload = QLabel("Upload new picture")
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px;")

        btn_remove = QLabel("Remove")
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setStyleSheet("color: #E05C5C; font-size: 12px;")  # Merah untuk aksi berbahaya

        action_layout.addWidget(btn_upload)
        action_layout.addWidget(btn_remove)

        layout.addWidget(lbl_field)
        layout.addSpacerItem(spacer)
        layout.addWidget(avatar)
        layout.addWidget(action_col)

        return baris


    # ----------------------------------------------------------
    # FUNGSI _buat_baris_info()
    # Template untuk membuat satu baris info yang bisa diklik
    # Isi baris (dari kiri ke kanan):
    #   - Nama field di kiri (warna muted)
    #   - Nilai field di kanan
    #   - Panah (>) sebagai petunjuk bisa diklik untuk edit
    #
    # Parameter:
    #   field_label = nama field, contoh: "Name", "Email"
    #   field_value = nilai saat ini, contoh: "Event Organizer"
    #
    # Return: QWidget baris siap pakai
    # ----------------------------------------------------------
    def _buat_baris_info(self, field_label, field_value):
        baris = QWidget()
        baris.setStyleSheet("background: transparent;")
        baris.setFixedHeight(56)
        baris.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(baris)
        layout.setContentsMargins(0, 0, 0, 0)

        # Nama field di kiri
        lbl_field = QLabel(field_label)
        lbl_field.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        lbl_field.setFixedWidth(220)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Nilai field di kanan (teks gelap)
        lbl_value = QLabel(field_value)
        lbl_value.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px;")
        lbl_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Panah ">" sebagai indikator visual bahwa baris ini bisa diklik
        lbl_arrow = QLabel(">")
        lbl_arrow.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; margin-left: 8px;")

        layout.addWidget(lbl_field)
        layout.addSpacerItem(spacer)
        layout.addWidget(lbl_value)
        layout.addWidget(lbl_arrow)

        return baris


    # ----------------------------------------------------------
    # FUNGSI _buat_divider()
    # Membuat garis tipis horizontal sebagai pemisah antar baris
    # Agar tampilan lebih rapi dan terstruktur seperti settings iOS/Android
    #
    # Return: QFrame siap pakai
    # ----------------------------------------------------------
    def _buat_divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {COLOR_DIVIDER}; background-color: {COLOR_DIVIDER};")
        line.setFixedHeight(1)
        return line


    # ----------------------------------------------------------
    # FUNGSI buat_panel_your_events()
    # Membangun panel "Your Events" yang BERBEDA sesuai role:
    #
    #   ROLE_ORGANIZER → daftar event yang pernah dibuat + tombol tambah event
    #   ROLE_MAHASISWA → daftar event yang pernah didaftarkan / di-RSVP
    #   ROLE_UMUM      → pesan bahwa fitur ini tidak tersedia + ajakan login
    #
    # CATATAN: Implementasi penuh (dengan data dari database) akan
    # dikerjakan di sprint berikutnya. Saat ini ditampilkan placeholder.
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

        # Konten berbeda berdasarkan role user
        if self.role == ROLE_ORGANIZER:
            # Event Organizer melihat event yang pernah mereka buat
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
            # Mahasiswa melihat event yang pernah mereka daftarkan
            lbl_info = QLabel("Event yang pernah kamu ikuti akan muncul di sini.")
            lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
            layout.addWidget(lbl_info)

        else:
            # User umum tidak punya akses ke fitur ini
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
    #
    # CATATAN: Implementasi penuh dengan toggle switch (QCheckBox /
    # custom toggle) akan dikerjakan di sprint berikutnya.
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

        # Deskripsi notifikasi berbeda per role
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

        # Placeholder toggle (akan diganti QCheckBox bergaya custom nanti)
        lbl_coming = QLabel("⚙️  Pengaturan notifikasi akan hadir di sprint berikutnya.")
        lbl_coming.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; font-style: italic;")
        layout.addWidget(lbl_coming)

        layout.addStretch()
        return panel


    # ----------------------------------------------------------
    # FUNGSI buat_panel_appearance()
    # Membangun panel "Appearance" berisi pengaturan tampilan
    # Tampilan panel ini SAMA untuk semua role user
    #
    # Rencana konten (sprint berikutnya):
    #   - Pilihan tema: Light / Dark / System
    #   - Ukuran font
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
    #
    # Rencana konten (sprint berikutnya):
    #   - Pilihan bahasa: Bahasa Indonesia / English
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
    user_dummy = {
        "nama"   : "Event Organizer",
        "bio"    : "Music Festival",
        "email"  : "eventorganizer@gmail.com",
        "kontak" : "+6281-3456-7898",
        "role"   : ROLE_ORGANIZER,   # Ganti ke ROLE_MAHASISWA atau ROLE_UMUM untuk test role lain
        "inisial": "EO"
    }

    window = SettingsWindow(user_data=user_dummy)
    window.show()
    sys.exit(app.exec_())
